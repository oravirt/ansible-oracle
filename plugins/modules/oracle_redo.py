#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community',
}

DOCUMENTATION = '''
---
module: oracle_redo
short_description: Manage the size and number of Oracle online redo log groups
description:
    - Ensures that all online redo log groups have the size O(size) and that every
      enabled redo thread has O(groups) redo log groups.
    - Everything is done in one PL/SQL block in the database.
    - Redo log groups with a different size are replaced. For each such group a new
      group with O(size) is added to the same thread
      (C(ALTER DATABASE ADD LOGFILE THREAD <n> SIZE <size>)) and the old group is
      dropped. If the old group is C(CURRENT) or C(ACTIVE), a log switch and a
      checkpoint are done first (C(SWITCH ALL LOGFILE) and C(CHECKPOINT GLOBAL) in
      RAC), followed by a wait of 5 seconds.
    - New groups are created without file names or member count, so the database
      defaults (for example C(DB_CREATE_ONLINE_LOG_DEST_n)) are used.
    - If a thread has fewer groups than O(groups), groups are added with the next
      free group number. If it has more, the groups with the highest group number
      that are not C(CURRENT) or C(ACTIVE) are dropped. Files of dropped groups are
      not deleted by the module.
    - C(changed=true) is returned if any group was replaced, added or dropped.
    - The connected user needs the privileges to read C(V$LOG), C(V$THREAD) and
      C(V$INSTANCE), C(ALTER DATABASE), C(ALTER SYSTEM) and C(EXECUTE) on
      C(DBMS_LOCK).
    - If neither O(user) nor O(password) is given, a connection with an Oracle wallet
      (C(/@<service_name>)) is used. Otherwise both must be set.
    - Can be run locally on the control machine or on a remote host.
version_added: "2.4"
options:
    hostname:
        description:
            - The Oracle database host.
            - Ignored when connecting with an Oracle wallet.
        type: str
        required: false
        default: localhost
    port:
        description:
            - The listener port number on the host.
            - Ignored when connecting with an Oracle wallet.
        type: int
        required: false
        default: 1521
    service_name:
        description:
            - The database service name to connect to.
            - When connecting with an Oracle wallet, this is the TNS alias of the
              wallet entry.
        type: str
        required: true
    user:
        description:
            - The Oracle user name to connect to the database.
            - Omit O(user) and O(password) to connect with an Oracle wallet.
        type: str
        required: false
    password:
        description:
            - The Oracle user password for O(user).
        type: str
        required: false
    mode:
        description:
            - The mode with which to connect to the database.
        type: str
        required: false
        default: normal
        choices: ['normal', 'sysdba']
    size:
        description:
            - The wanted size of every redo log group.
            - Must end with an uppercase V(M), V(G) or V(T), for example V(512M) or
              V(1G).
        type: str
        required: true
    groups:
        description:
            - The wanted number of redo log groups per enabled redo thread.
        type: int
        required: true
notes:
    - python-oracledb needs to be installed, e.g. with the role
      C(opitzconsulting.ansible_oracle.pyoracledb).
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
requirements: [ "python-oracledb" ]
author:
    - Mikael Sandström (@oravirt)
'''

EXAMPLES = '''
- name: Ensure 3 redo log groups of 1G per thread
  opitzconsulting.ansible_oracle.oracle_redo:
    hostname: "{{ ansible_hostname }}"
    service_name: orclcdb
    user: system
    password: "{{ system_password }}"
    size: 1G
    groups: 3
  environment:
    ORACLE_HOME: /u01/app/oracle/product/19.0.0/dbhome_1
    LD_LIBRARY_PATH: /u01/app/oracle/product/19.0.0/dbhome_1/lib
  run_once: true

- name: Ensure 4 redo log groups of 512M per thread (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_redo:
    service_name: orclcdb
    mode: sysdba
    size: 512M
    groups: 4
'''

RETURN = '''
msg:
    description:
        - Message describing the size changes and the group changes.
    returned: success
    type: str
    sample: >-
        All redologs have been changed to 1G.
        Groups have been adjusted to 3 groups.
'''


# Ansible code
def main():
    global conn, msg, module
    msg = ['']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(default='localhost'),
            port=dict(default=1521, type='int'),
            service_name=dict(required=True),
            user=dict(required=False),
            password=dict(required=False, no_log=True),
            mode=dict(default='normal', choices=["normal", "sysdba"]),
            size=dict(required=True),
            groups=dict(required=True)
            #     threads       = dict(default=1)
        ),
    )

    hostname = module.params["hostname"]
    port = module.params["port"]
    service_name = module.params["service_name"]
    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
    size = module.params["size"]
    groups = module.params["groups"]
    # threads = module.params["threads"]

    conn = oracledb_connect(module, hostname, port, service_name, user, password, mode)
    #
    # if module.check_mode:
    #     module.exit_json(changed=False)
    #

    if not (size.endswith('M') or size.endswith('G') or size.endswith('T')):
        msg = 'You need to suffix the size with (M,G or T), i.e: %sM/%sG/%sT' % (
            size,
            size,
            size,
        )
        module.fail_json(msg=msg, changed=False)

    redosql = """
    DECLARE

       -- output
       v_redo_size_changes   number := 0;
       v_redo_group_changes   number := 0;
       v_msg       varchar2(100);
       -- input
       v_maxbytes  varchar2(20) ;
       v_groups number ;
       -- runtime
       v_maxbytes_actual  number(10,1);
       v_maxbytes_suffix varchar2(1);
       v_divisor number(20);
       v_sleep     number := 5;
       v_israc     VARCHAR2(3);
       v_existing_redogroups number ;
       v_max_groupnum  number;
       v_group_diff number;
       v_sql_sw_lf varchar2 (50);
       v_sql_cp    varchar2 (50);

       -- exceptions
       missing_suffix exception;

       BEGIN

           v_maxbytes:= :redosize;
           v_groups:= :redogroups;



           -- Check if it is a RAC database or not (parallel = True -> RAC)
           select parallel into v_israc from v$instance;
           IF v_israc = 'YES' THEN
              v_sql_sw_lf := 'alter system switch all logfile';
              v_sql_cp := 'alter system checkpoint global';
           ELSE
              v_sql_sw_lf := 'alter system switch logfile';
              v_sql_cp := 'alter system checkpoint';
           END IF;


           -- Get the suffix to decide the divisor
           select substr(v_maxbytes,-1) into v_maxbytes_suffix from dual;
           IF upper(v_maxbytes_suffix) = 'M' THEN
               v_divisor := 1024*1024;
           ELSIF upper(v_maxbytes_suffix) = 'G' THEN
               v_divisor := 1024*1024*1024;
           ELSIF upper(v_maxbytes_suffix) = 'T' THEN
               v_divisor := 1024*1024*1024*1024;
           ELSE
               raise missing_suffix;
           END IF;

           -- Strip the suffix (M/G/T) from the input string
           IF upper(v_maxbytes_suffix) in ('M','G','T') THEN
               select substr (v_maxbytes, 0, (length (v_maxbytes)-1))
               into v_maxbytes_actual
               from dual;
           END IF;


               FOR rec in (select thread#, group#, status, bytes
                           from v$log
                           order by thread#)
               LOOP
                   IF rec.bytes/v_divisor != v_maxbytes_actual    THEN
                       v_redo_size_changes := v_redo_size_changes+1;
                       for chloop in (select thread#, group#, status
                       from v$log
                       where thread# = rec.thread# and group# = rec.group#)
                       loop
                           IF chloop.status in ('CURRENT','ACTIVE') THEN
                                 --dbms_output.put_line('Current');
                                 execute immediate v_sql_sw_lf;
                                 execute immediate v_sql_cp;
                                 dbms_lock.sleep(v_sleep);
                                 execute immediate 'alter database add logfile thread '
                                    || chloop.thread# ||' size '|| v_maxbytes ;
                                 execute immediate 'alter database drop logfile group '
                                    || chloop.group#;
                           ELSE
                                 execute immediate 'alter database add logfile thread '
                                    ||chloop.thread# ||' size '||v_maxbytes ;
                                 execute immediate 'alter database drop logfile group '
                                    ||chloop.group# ;

                           END IF;
                       END LOOP;
                   END IF;
               END LOOP;
               dbms_output.put_line(v_redo_size_changes);

               -- Get number of groups
               for t in (select * from v$thread where enabled != 'DISABLED')
               loop
                   dbms_output.put_line('Thread: '||t.thread#);

                   select count(*)
                   into v_existing_redogroups
                   from v$log
                   where thread# = t.thread#;

                   dbms_output.put_line('Thread: '
                     || t.thread# || ' numgroups: ' || v_existing_redogroups);
                   IF v_existing_redogroups < v_groups THEN

                       select v_groups-v_existing_redogroups
                       into v_group_diff
                       from dual;

                       dbms_output.put_line('Adding ' || v_group_diff
                        || ' groups to thread: ' || t.thread#);
                            for grloop in 1..v_group_diff
                            loop
                                v_redo_group_changes := v_redo_group_changes+1;
                                --v_max_groupnum := 0;
                                select max(group#) into v_max_groupnum from v$log;
                                v_max_groupnum := v_max_groupnum + 1;
                                execute immediate 'alter database add logfile thread '
                                    || t.thread# || ' group ' || v_max_groupnum
                                    ||' size ' || v_maxbytes;
                                dbms_output.put_line('adding group ' || v_max_groupnum
                                    || ' to thread ' || t.thread#);
                            end loop;

                   ELSIF v_existing_redogroups > v_groups THEN
                       -- select count(*)
                       -- into v_existing_redogroups
                       -- from v$log
                       -- where thread# = t.thread#;
                       select v_existing_redogroups-v_groups
                       into v_group_diff
                       from dual;
                       dbms_output.put_line('Removing ' || v_group_diff
                        || ' groups from thread: ' || t.thread#);

                       for grloop in 1..v_group_diff
                       loop
                           v_redo_group_changes := v_redo_group_changes+1;

                           select max(group#)
                           into v_max_groupnum
                           from v$log
                           where upper(status) not in ('ACTIVE','CURRENT')
                            and thread# = t.thread#;

                           execute immediate 'alter database drop logfile group '
                                || v_max_groupnum ;
                           dbms_output.put_line('dropping group ' || v_max_groupnum
                                || ' thread#: ' || t.thread#);
                       end loop;

                   ELSE
                       dbms_output.put_line('Nothing to do');
                   END IF;
               end loop;



              :o_size_changed := v_redo_size_changes;
              :o_group_changed := v_redo_group_changes;
              IF v_redo_size_changes > 0 THEN
                  :o_size_msg := 'All redologs have been changed to '||v_maxbytes;
              ELSE
                  :o_size_msg := 'No size changes';
              END IF;

              IF v_redo_group_changes > 0 THEN
                  :o_group_msg := 'Groups have been adjusted to '||v_groups ||' groups';
              ELSE
                  :o_group_msg := 'No group changes';
              END IF;

              EXCEPTION
              WHEN missing_suffix THEN
                   dbms_output.put_line('--------');
                   dbms_output.put_line('You need to suffix the size with '
                        || '(M,G or T), i.e: '
                        || v_maxbytes || 'M/' || v_maxbytes
                        || 'G/' || v_maxbytes || 'T');
                   dbms_output.put_line('--------');

       END;
    """

    cur = conn.cursor()

    try:
        v_size_changed = cur.var(oracledb.NUMBER)
        v_group_changed = cur.var(oracledb.NUMBER)
        v_size_msg = cur.var(oracledb.STRING)
        v_group_msg = cur.var(oracledb.STRING)
        cur.execute(
            redosql,
            {
                'redosize': size,
                'redogroups': groups,
                'o_size_changed': v_size_changed,
                'o_group_changed': v_group_changed,
                'o_size_msg': v_size_msg,
                'o_group_msg': v_group_msg,
            },
        )
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg = '%s' % (error.message)
        module.fail_json(msg=msg, changed=False)

    size_result_changed = v_size_changed.getvalue()
    group_result_changed = v_group_changed.getvalue()
    # module.exit_json(msg=result_changed, changed=False)
    size_msg = v_size_msg.getvalue()
    group_msg = v_group_msg.getvalue()
    msg = "%s. %s." % (size_msg, group_msg)
    if size_result_changed > 0 or group_result_changed > 0:
        changed = True
    else:
        changed = False
    # module.exit_json(msg=result_changed, changed=False)

    module.exit_json(msg=msg, changed=changed)


if __name__ == '__main__':
    main()
