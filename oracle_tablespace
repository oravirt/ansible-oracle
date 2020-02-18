#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_tablespace
short_description: Manage tablespaces in an Oracle database
description:
    - Manage tablespaces in an Oracle database (create, drop, put in read only/read write, offline/online)
    - Can be run locally on the controlmachine or on a remote host
version_added: "1.9.1"
options:
    hostname:
        description:
            - The Oracle database host
        required: false
        default: localhost
    port:
        description:
            - The listener port number on the host
        required: false
        default: 1521
    service_name:
        description:
            - The database service name to connect to
        required: true
    user:
        description:
            - The Oracle user name to connect to the database
        required: true
    mode:
        description:
            - The mode with which to connect to the database (normal/sysdba)
        required: false
        choices: ['normal','sysdba']
        default: normal
    password:
        description:
            - The Oracle user password for 'user'
        required: true
    tablespace:
        description:
            - The tablespace that should be managed
        required: True
    state:
        description:
            - The intended state of the tablespace
        default: present
        choices: ['present','absent','online','offline','read_only','read_write']
    bigfile:
        description:
            - Should the tablespace be created as a bigfile tablespace
        default: false
        choices: ['true','false']
    datafile:
        description:
            - Where to put the datafile. Can be an ASM diskgroup or a filesystem datafile (i.e '+DATA', '/u01/oradata/testdb/test01.dbf')
            - mutually_exclusive with numfiles
        required: false
        aliases: ['df','path']
    numfiles:
        description:
            - If OMF (db_create_file_dest) is set, you can just specify the number of datafiles you want attached to the tablespace
            - mutually_exclusive with datafile
        required: false
    size:
        description:
            - The size of the datafile (10M, 10G, 150G etc)
        required: false
    content:
        description:
            - The type of tablespace (permanent, temporary or undo)
        default: permanent
        choices: ['permanent','temp','undo']
    autoextend:
        description:
            - Should the datafile be autoextended
        default: false
        choices: ['true','false']
    nextsize:
        description:
            - If autoextend, the size of the next extent allocated (1M, 50M, 1G etc)
        aliases: ['next']
    maxsize:
        description:
            - If autoextend, the maximum size of the datafile (1M, 50M, 1G etc). If empty, defaults to database limits
        aliases: ['max']

notes:
    - cx_Oracle needs to be installed
requirements: [ "cx_Oracle" ]
author: Mikael Sandström, oravirt@gmail.com, @oravirt
'''

EXAMPLES = '''
# Create a new normal tablespace
oracle_tablespace: hostname=db-server-scan service_name=orcl user=system password=manager tablespace=test datafile='+DATA' size=100M state=present

# Create a new bigfile temporary tablespace with autoextend on and maxsize set
oracle_tablespace: hostname=db-server service_name=orcl user=system password=manager tablespace=test datafile='+DATA' content=temp size=100M state=present bigfile=true autoextend=true next=100M maxsize=20G

# Drop a tablespace
oracle_tablespace: hostname=localhost service_name=orcl user=system password=manager tablespace=test state=absent

# Make a tablespace read only
oracle_tablespace: hostname=localhost service_name=orcl user=system password=manager tablespace=test state=read_only

# Make a tablespace read write
oracle_tablespace: hostname=localhost service_name=orcl user=system password=manager tablespace=test state=read_write

# Make a tablespace offline
oracle_tablespace: hostname=localhost service_name=orcl user=system password=manager tablespace=test state=offline

# Make a tablespace online
oracle_tablespace: hostname=localhost service_name=orcl user=system password=manager tablespace=test state=online


'''

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


# Check if the tablespace exists
def check_tablespace_exists(module, msg, cursor, tablespace):

    sql = 'select tablespace_name, status from dba_tablespaces where tablespace_name = upper(\'%s\')' % tablespace

    global tsname
    global status

    try:
            cursor.execute(sql)
            #result = cursor.fetchone()[0]
            result = cursor.fetchall()
            count = cursor.rowcount
    except cx_Oracle.DatabaseError as exc:
            error, = exc.args
            msg = error.message+ 'sql: ' + sql
            return False

    if count > 0:
        list_of_dbfs = get_tablespace_files(module, msg, cursor, tablespace)
        #for tsname,status in result:
        for tsname,status in result:
            status  = status

        #return True, status
        return True, status

# Create the tablespace
def create_tablespace(module, msg, cursor, tablespace, state, datafile, numfiles, size, content, bigfile, autoextend, nextsize, maxsize):

    global crfiles
    # Check if OMF is enabled
    checksql = 'select value from v$parameter where lower(name) = \'db_create_file_dest\''
    result = execute_sql_get(module,msg,cursor,checksql)
    dbfc_value = result[0]
    if numfiles is not None:
        numfiles = numfiles
    else:
        numfiles = 1

    # Check if tuple is empty
    if not all(dbfc_value):
        skip_datafile = False
    else:
        skip_datafile = True

    if not size and not autoextend and not maxsize:
        size = '100M'
        autoextend = True
        nextsize = '1M'
        maxsize = 'unlimited'
        # msg = 'Error: Missing parameter - size'
        # module.fail_json(msg=msg, changed=False)

    if bigfile:
        if datafile is not None:
            if len(datafile)>1 or int(numfiles) > 1:
                msg='Only one datafile allowed in BIGFILE tablespace'
                module.fail_json(msg=msg, changed=False)

    if not datafile:
         if skip_datafile:
             if autoextend and not nextsize:
                 module.fail_json(msg='Error: Missing NEXT size for autoextend',changed=False)
             elif autoextend and nextsize and not maxsize:
                 datafile_list = ','.join(' size %s autoextend on next %s' % (size,nextsize) for d in range(int(numfiles)) )
             elif autoextend and nextsize and maxsize:
                 datafile_list = ','.join(' size %s autoextend on next %s maxsize %s' % (size,nextsize,maxsize) for d in range(int(numfiles) ))
             else:
                 datafile_list = ','.join(' size %s ' % (size) for d in range(int(numfiles) ))

             # If db_create_file_dest IS set, and we're missing the datafile datafile we CAN continue because of OMF
             if content == 'undo':
                 if bigfile:
                     sql = 'create bigfile undo tablespace %s datafile  size %s' % (tablespace, size)
                 else:
                     sql = 'create undo tablespace %s datafile  %s' % (tablespace, datafile_list)

             elif content == 'temp':
                 if bigfile:
                     sql = 'create bigfile temporary tablespace %s tempfile size %s' % (tablespace,size)
                 else:
                     sql = 'create temporary tablespace %s tempfile %s' % (tablespace, datafile_list)

             else:
                 if bigfile:
                     sql = 'create bigfile tablespace %s datafile size %s' % (tablespace, size)
                 else:
                     sql = 'create tablespace %s datafile  %s' % (tablespace, datafile_list)

             if execute_sql(module, msg, cursor, sql):
                 crfiles = numfiles
                 return True, crfiles
             else:
                 return False

         elif not skip_datafile:

             # If db_create_file_dest is NOT set, and we're missing the datafile datafile we can't continue

             msg = 'Error: Missing datafile name/datafile. Either set db_create_file_dest or specify one or more datafiles'
             module.fail_json(msg=msg, changed=False)

    else:

        # Everything is ok, tablespace + datafile provided so just continue
        if autoextend and not nextsize:
            module.fail_json(msg='Error: Missing NEXT size for autoextend',changed=False)
        elif autoextend and nextsize and not maxsize:
            datafile_list = ','.join('\''+ d + '\' size %s autoextend on next %s' % (size,nextsize) for d in datafile )
        elif autoextend and nextsize and maxsize:
            datafile_list = ','.join('\''+ d + '\' size %s autoextend on next %s maxsize %s' % (size,nextsize,maxsize) for d in datafile )
        else:
            datafile_list = ','.join('\''+ d + '\' size %s ' % (size) for d in datafile )

        if content == 'undo':
            if bigfile:
                sql = 'create bigfile undo tablespace %s datafile  %s' % (tablespace, datafile_list)
            else:
                sql = 'create undo tablespace %s datafile %s' % (tablespace, datafile_list)

        elif content == 'temp':
            if bigfile:
                sql = 'create bigfile temporary tablespace %s tempfile %s' % (tablespace, datafile_list)
            else:
                sql = 'create temporary tablespace %s tempfile %s' % (tablespace, datafile_list)

        else:
            if bigfile:
                sql = 'create bigfile tablespace %s datafile  %s' % (tablespace, datafile_list)
            else:
                sql = 'create tablespace %s datafile %s' % (tablespace, datafile_list)

        if execute_sql(module, msg, cursor, sql):
            crfiles = len(datafile)
            return True,crfiles
        else:
            return False

def map_status(state,current_status):
    wanted_status = ''
    enforcesql = ''
    if state == 'read_only':
        wanted_status = 'READ ONLY'
        enforcesql = 'read only'
    elif state == 'read_write':
        if current_status == 'ONLINE':
            wanted_status = 'ONLINE'
            enforcesql = 'online'
        elif current_status == 'OFFLINE':
            wanted_status = 'ONLINE'
            enforcesql = 'online'
        else:
            wanted_status = 'ONLINE'
            enforcesql = 'read write'
    elif state == 'online':
        wanted_status = 'ONLINE'
        enforcesql = 'online'
    if state == 'present':
        if current_status == 'READ ONLY':
            wanted_status = 'ONLINE'
            enforcesql = 'read write'
        elif current_status == 'OFFLINE':
            wanted_status = 'ONLINE'
            enforcesql = 'online'
        elif current_status == 'ONLINE':
            wanted_status = 'ONLINE'
            enforcesql = 'online'
    elif state == 'offline':
        wanted_status = 'OFFLINE'
        enforcesql = 'offline'

    return wanted_status, enforcesql

def ensure_tablespace_state (module,msg,cursor,tablespace, state, datafile, numfiles, size, content, bigfile, autoextend, nextsize, maxsize):

    global newtbs
    alter_tbs_list = []
    wanted_list_dbf = []

    #module.exit_json(msg=alter_tbs_list, changed=False)
    checksql = 'select value from v$parameter where lower(name) = \'db_create_file_dest\''
    result = execute_sql_get(module,msg,cursor,checksql)
    dbfc_value = result[0]
    if content == 'temp':
        dftype = 'tempfile'
        dfsource = 'dba_temp_files'
        tbstype = 'Temporary tablespace'
    elif content == 'undo':
        dftype = 'datafile'
        dfsource = 'dba_data_files'
        tbstype = 'Undo tablespace'
    elif content == 'permanent':
        dftype = 'datafile'
        dfsource = 'dba_data_files'
        tbstype = 'Tablespace'

    # Check if tuple is empty
    if not all(dbfc_value):
        skip_datafile = False
    else:
        skip_datafile = True

    if not size and not autoextend and not maxsize:
        size = '100M'
        autoextend = True
        maxsize = 'unlimited'


    statussql = 'select status from dba_tablespaces where tablespace_name = upper(\'%s\')' % (tablespace)
    current_status = execute_sql_get(module,msg,cursor,statussql)
    wanted_status,enforcesql = map_status(state,current_status[0][0])
    # msg = 'ws: %s, curr: %s, sql: %s' % (wanted_status,current_status,enforcesql)
    # module.exit_json(msg=msg,changed=False)
    if wanted_status != current_status[0][0]:
        sql = 'alter tablespace %s %s' % (tablespace, enforcesql)
        alter_tbs_list.append(sql)

    alter_tbs_sql = 'alter tablespace %s' % (tablespace)
    numfiles_curr_sql = 'select count(*) from %s where tablespace_name = upper(\'%s\')' % (dfsource,tablespace)
    numfiles_curr_ = execute_sql_get(module,msg,cursor,numfiles_curr_sql)
    crfiles = numfiles_curr_[0][0]
    #module.exit_json(msg=skip_datafile, changed=False)

    # The following if/elif deals with adding data/temp-files
    #
    if not skip_datafile and datafile is None:
        msg = 'Error: Missing datafile name/datafile. Either set db_create_file_dest or specify one or more datafiles'
        module.fail_json(msg=msg, changed=False)

    elif numfiles is not None and int(numfiles_curr_[0][0]) < int(numfiles) and not bigfile and skip_datafile:
        '''
        This should only run if:
        - db_create_file_dest is set (OMF is in use)
        - Tablespace is not bigfile
        - numfiles is set to a higher value than the existing number of datafiles
        '''
        newfiles = abs(int(numfiles) - int(numfiles_curr_[0][0]))
        #module.exit_json(msg='%s, %s, %s' % (numfiles_curr_[0][0], numfiles, newfiles), changed=False)

        if autoextend and not nextsize:
            module.fail_json(msg='Error: Missing NEXT size for autoextend',changed=False)
        elif autoextend and nextsize and not maxsize:
            wanted_list_dbf = ','.join(' size %s autoextend on next %s' % (size,nextsize) for d in range(int(newfiles)) )
        elif autoextend and nextsize and maxsize:
            wanted_list_dbf = ','.join(' size %s autoextend on next %s maxsize %s' % (size,nextsize,maxsize) for d in range(int(newfiles) ))
        else:
            wanted_list_dbf = ','.join(' size %s ' % (size) for d in range(int(newfiles) ))

        alter_tbs_sql += ' add %s %s ' % (dftype, wanted_list_dbf)
        alter_tbs_list.append(alter_tbs_sql)
        crfiles = numfiles

    elif numfiles is None and not bigfile and datafile is not None and int(numfiles_curr_[0][0]) < int(len(datafile)):
        '''
        This should only run if:
        - 'datafile' is set
        - Tablespace is not bigfile
        - The number of files (len(datafile)) are higher than the existing number of datafiles
        '''

        # Get the current list of datafiles
        currfiles_perm = get_tablespace_files(module,msg,cursor,tablespace)
        # Convert the resultset (list of tuples) to a list
        currfiles_perm = [a[0] for a in currfiles_perm]
        # Compare the current list with the 'wanted_list_dbf'
        wanted_list_dbf = list(set(datafile) - set(currfiles_perm))
        if len(wanted_list_dbf) > 0:
            if autoextend and not nextsize:
                module.fail_json(msg='Error: Missing NEXT size for autoextend',changed=False)
            elif autoextend and nextsize and not maxsize:
                datafile_list = ','.join('\''+ d + '\' size %s autoextend on next %s' % (size,nextsize) for d in wanted_list_dbf )
            elif autoextend and nextsize and maxsize:
                datafile_list = ','.join('\''+ d + '\' size %s autoextend on next %s maxsize %s' % (size,nextsize,maxsize) for d in wanted_list_dbf )
            else:
                datafile_list = ','.join('\''+ d + '\' size %s ' % (size) for d in wanted_list_dbf )

            alter_tbs_sql += ' add %s %s ' % (dftype,datafile_list)
            alter_tbs_list.append(alter_tbs_sql)
            crfiles = len(datafile)


    attribute_change = ensure_tablespace_attributes(module,msg,cursor,tablespace, autoextend, nextsize, maxsize)


    #module.exit_json(msg=alter_tbs_list)
    # Enforce actual changes (if there are any)
    dbf_change = False
    if len(alter_tbs_list) > 0:
        for sql in alter_tbs_list:
            execute_sql(module,msg,cursor,sql)
        dbf_change = True

    if (dbf_change or attribute_change):
        msg = 'Tablespace %s has changed state - initial size: %s, bigfile: %s, autoextend: %s, next: %s, maxsize/file: %s, numfiles: %s, status: %s' % (tablespace, size, bigfile, autoextend, nextsize, maxsize,crfiles,wanted_status)
        module.exit_json(msg=msg, changed=True)
    else:
        if newtbs:
            msg = '%s %s successfully created - initial size: %s, bigfile: %s, autoextend: %s, nextsize: %s, maxsize/file: %s, numfiles: %s, status: %s' % (tbstype, tablespace, size, bigfile, autoextend, nextsize, maxsize,crfiles, wanted_status)
            module.exit_json(msg=msg, changed=True)
        else:
            msg = 'Tablespace %s already exists - initial size: %s, bigfile: %s, autoextend: %s, nextsize: %s, maxsize/file: %s, numfiles: %s, status: %s' % (tablespace, size, bigfile, autoextend, nextsize, maxsize,crfiles,wanted_status)
            module.exit_json(msg=msg, changed=False)


def ensure_tablespace_attributes (module,msg,cursor,tablespace, autoextend, nextsize, maxsize):

    ensure_sql = """
    DECLARE
       -- output
       v_autoextend_change number := 0;
       v_nextsize_change number := 0;
       v_maxsize_change number := 0;
       -- input
       v_tablespace varchar2(30); --:= 'blergh';
       v_autoextend  varchar2(5); --:= 'True';
       v_nextsize varchar2(20); --:= '10M' ;
       v_maxsize varchar2(20); --:= '500M' ;
       -- runtime
       v_nextsize_suffix varchar2(1);
       v_maxsize_suffix varchar2(1);
       v_divisor_nextsize number(20);
       v_divisor_maxsize number(20);
       v_next_change number;
       v_max_change number;
       v_autoextend_ varchar2(3);
       v_autoextend_sql varchar2(30);
       v_nextsize_current varchar2(20) ;
       v_maxsize_current varchar2(20) ;
       v_nextsize_wanted varchar2(20) ;
       v_maxsize_wanted varchar2(20) ;
       v_content varchar2(30) ;
       v_tbs_source varchar2(30);
       v_df_source varchar2(50);
       v_df_file varchar2(50);
       -- exceptions
       missing_suffix exception;

       BEGIN
           v_tablespace:= :tablespace;
           v_autoextend:= :autoextend;
           v_nextsize:= :nextsize;
           v_maxsize:= :maxsize;
           -- Check what type of tablespace it is
           select contents into v_tbs_source from dba_tablespaces where tablespace_name = upper(''||v_tablespace||'');
           IF upper(v_tbs_source) = 'TEMPORARY' THEN
               v_content := 'temp';
           ELSE
               v_content := 'permanent';
           END IF;

           IF upper(v_autoextend) = 'TRUE' THEN
                v_autoextend_ := 'YES';
                v_autoextend_sql := 'on';
           ELSE
                v_autoextend_ := 'NO';
                v_autoextend_sql := 'off';
           END IF;
           -- Get the suffix to decide the divisor
           select substr(v_nextsize,-1),substr(v_maxsize,-1) into v_nextsize_suffix,v_maxsize_suffix from dual;
           IF upper(v_nextsize_suffix) = 'M' THEN
               v_divisor_nextsize := 1024*1024;
           ELSIF upper(v_nextsize_suffix) = 'G' THEN
               v_divisor_nextsize := 1024*1024*1024;
           ELSIF upper(v_nextsize_suffix) = 'T' THEN
               v_divisor_nextsize := 1024*1024*1024*1024;
           ELSE
               NULL;
           END IF;

           IF upper(v_maxsize_suffix) = 'M' THEN
               v_divisor_maxsize := 1024*1024;
           ELSIF upper(v_maxsize_suffix) = 'G' THEN
               v_divisor_maxsize := 1024*1024*1024;
           ELSIF upper(v_maxsize_suffix) = 'T' THEN
               v_divisor_maxsize := 1024*1024*1024*1024;
           ELSE
               NULL;
           END IF;

           -- Strip the suffix (M/G/T) from the input string
          IF upper(v_nextsize_suffix) in ('K','M','G','T') THEN
              select substr (v_nextsize, 0, (length (v_nextsize)-1)) into v_nextsize_wanted from dual;
          END IF;
          IF upper(v_maxsize_suffix) in ('K','M','G','T') THEN
              select substr (v_maxsize, 0, (length (v_maxsize)-1)) into v_maxsize_wanted from dual;
          END IF;

               -- Loop over files in the tablespace and makes changes if needed
               IF upper(v_content) = 'TEMP' THEN
                    v_df_file := 'tempfile';
                    FOR rec in (select df.file_name, df.autoextensible, dt.block_size, df.increment_by, df.maxbytes
                                from dba_tablespaces dt, dba_temp_files df
                                where dt.tablespace_name = df.tablespace_name
                                and dt.tablespace_name = upper(''||v_tablespace||''))

                    LOOP
                        v_nextsize_current := ((rec.block_size*rec.increment_by)/v_divisor_nextsize);
                        v_maxsize_current := ((rec.maxbytes)/v_divisor_maxsize);

                        IF (rec.autoextensible != v_autoextend_) THEN
                            v_autoextend_change := v_autoextend_change+1;
                            --dbms_output.put_line ('alter database '||v_df_file ||' '''||rec.file_name ||''' autoextend '||v_autoextend_sql );
                            execute immediate 'alter database '||v_df_file ||' '''||rec.file_name ||''' autoextend '||v_autoextend_sql;
                        END IF;
                        IF upper(v_autoextend) = 'TRUE' THEN
                            IF (v_nextsize_current != v_nextsize_wanted) THEN
                                v_nextsize_change := v_nextsize_change+1;
                                --dbms_output.put_line ('alter database tempfile '''||rec.file_name ||''' autoextend on next '||v_nextsize );
                                execute immediate 'alter database '||v_df_file ||' '''||rec.file_name ||''' autoextend on next '||v_nextsize;
                            END IF;
                            IF (v_maxsize_current != v_maxsize_wanted) THEN
                                v_maxsize_change := v_maxsize_change+1;
                                --dbms_output.put_line ('alter database tempfile '''||rec.file_name ||''' autoextend on maxsize '||v_maxsize );
                                execute immediate 'alter database '||v_df_file ||' '''||rec.file_name ||''' autoextend on maxsize '||v_maxsize;
                            END IF;
                        END IF;
                    END LOOP;

                    ELSE
                        v_df_file := 'datafile';
                        FOR rec in (select df.file_name, df.autoextensible, dt.block_size, df.increment_by, df.maxbytes
                                    from dba_tablespaces dt, dba_data_files df
                                    where dt.tablespace_name = df.tablespace_name
                                    and dt.tablespace_name = upper(''||v_tablespace||''))

                        LOOP
                            v_nextsize_current := ((rec.block_size*rec.increment_by)/v_divisor_nextsize);
                            v_maxsize_current := ((rec.maxbytes)/v_divisor_maxsize);

                            IF (rec.autoextensible != v_autoextend_) THEN
                                v_autoextend_change := v_autoextend_change+1;
                                --dbms_output.put_line ('alter database '||v_df_file ||' '''||rec.file_name ||''' autoextend '||v_autoextend_sql );
                                execute immediate 'alter database '||v_df_file ||' '''||rec.file_name ||''' autoextend '||v_autoextend_sql;
                            END IF;
                            IF upper(v_autoextend) = 'TRUE' THEN
                                IF (v_nextsize_current != v_nextsize_wanted) THEN
                                    v_nextsize_change := v_nextsize_change+1;
                                    --dbms_output.put_line ('alter database '||v_df_file ||' '''||rec.file_name ||''' autoextend on next '||v_nextsize );
                                    execute immediate 'alter database '||v_df_file ||' '''||rec.file_name ||''' autoextend on next '||v_nextsize;
                                END IF;
                                IF (v_maxsize_current != v_maxsize_wanted) THEN
                                    v_maxsize_change := v_maxsize_change+1;
                                    --dbms_output.put_line ('alter database '||v_df_file ||' '''||rec.file_name ||''' autoextend on maxsize '||v_maxsize );
                                    execute immediate 'alter database '||v_df_file ||' '''||rec.file_name ||''' autoextend on maxsize '||v_maxsize;
                                END IF;
                            END IF;
                        END LOOP;
               END IF;
               :o_autoextend_changed := v_autoextend_change;
               :o_nextsize_changed := v_nextsize_change;
               :o_maxsize_changed := v_maxsize_change;
               IF v_autoextend_change > 0 or v_nextsize_change > 0 or v_maxsize_change > 0 THEN
                  dbms_output.put_line ('auto: '||v_autoextend_change);
                  dbms_output.put_line ('next: '||v_nextsize_change);
                  dbms_output.put_line ('max: '||v_maxsize_change);
                  dbms_output.put_line ('Changes applied');
               END IF;
       END;
    """
    try:
        v_autoextend_change = cursor.var(cx_Oracle.NUMBER)
        v_nextsize_change = cursor.var(cx_Oracle.NUMBER)
        v_maxsize_change = cursor.var(cx_Oracle.NUMBER)

        cursor.execute(ensure_sql,
            {'tablespace': tablespace,'autoextend': str(autoextend), 'nextsize': nextsize, 'maxsize': maxsize, 'o_autoextend_changed': v_autoextend_change, 'o_nextsize_changed': v_nextsize_change,'o_maxsize_changed': v_maxsize_change})
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg = '%s' % (error.message)
        module.fail_json(msg=msg, changed=False)

    autoextend_result_changed = v_autoextend_change.getvalue()
    nextsize_result_changed = v_nextsize_change.getvalue()
    maxsize_result_changed = v_maxsize_change.getvalue()

    if (autoextend_result_changed > 0 or nextsize_result_changed > 0 or maxsize_result_changed):
        return True
    else:
        return False


# Get the existing datafiles for the tablespace
def get_tablespace_files(module, msg, cursor, tablespace):

    sql = 'select f.file_name from dba_data_files f, dba_tablespaces d '
    sql += 'where f.tablespace_name = d.tablespace_name '
    sql += 'and d.tablespace_name = upper(\'%s\')' % tablespace
    try:
            cursor.execute(sql)
            result = cursor.fetchall()
    except cx_Oracle.DatabaseError as exc:
            error, = exc.args
            msg = error.message+ ': sql: ' + sql
            module.fail_json(msg=msg)

    return result

# Make tablespace read only
def manage_tablespace(msg, cursor, tablespace, state):

    if state == 'read_only':
        sql = 'alter tablespace %s read only' % tablespace
        msg = 'Tablespace %s has been put in read only mode' % tablespace
    elif state == 'read_write':
        sql = 'alter tablespace %s read write' % tablespace
        msg = 'Tablespace %s has been put in read write mode' % tablespace
    elif state == 'offline':
        sql = 'alter tablespace %s offline' % tablespace
        msg = 'Tablespace %s has been put offline' % tablespace
    elif state == 'online':
        sql = 'alter tablespace %s online' % tablespace
        msg = 'Tablespace %s has been put online' % tablespace

    try:
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg = error.message+ 'sql: ' + sql
        return False


    return True, msg


# Drop the tablespace
def drop_tablespace(msg, cursor, tablespace):

    sql = 'drop tablespace %s including contents and datafiles' % tablespace

    try:
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg = 'Something went wrong while dropping the tablespace - %s sql: %s' % (error.message, sql)
        module.fail_json(msg=msg, changed=False)

    return True

def execute_sql_get(module, msg, cursor, sql):

    try:
        cursor.execute(sql)
        result = (cursor.fetchall())
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg = 'Something went wrong while executing sql_get - %s sql: %s' % (error.message, sql)
        module.fail_json(msg=msg, changed=False)
        return False
    return result

def execute_sql(module, msg, cursor, sql):
    try:
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg = 'Something went wrong while executing - %s sql: %s' % (error.message, sql)
        module.fail_json(msg=msg, changed=False)
        return False

    return True

def main():

    msg = ['']
    global crfiles
    global newtbs
    newtbs = False
    module = AnsibleModule(
        argument_spec = dict(
            hostname      = dict(default='localhost'),
            port          = dict(default=1521),
            service_name  = dict(required=True),
            mode          = dict(default='normal', choices=['normal', 'sysdba']),
            user          = dict(required=False),
            password      = dict(required=False, no_log=True),
            tablespace    = dict(required=True, aliases=['name','ts']),
            state         = dict(default="present", choices=["present", "absent", "read_only", "read_write", "offline", "online" ]),
            bigfile       = dict(default=False, type='bool'),
            datafile          = dict(required=False, type='list', aliases=['datafile','df']),
            numfiles      = dict(required=False),
            size          = dict(required=False),
            content       = dict(default='permanent', choices=['permanent', 'temp', 'undo']),
            autoextend    = dict(default=False, type='bool'),
            nextsize      = dict(required=False, aliases=['next']),
            maxsize       = dict(required=False, aliases=['max']),
        ),
        mutually_exclusive = [['datafile','numfiles']]
    )


    hostname = module.params["hostname"]
    port = module.params["port"]
    service_name = module.params["service_name"]
    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
    tablespace = module.params["tablespace"]
    state = module.params["state"]
    bigfile = module.params["bigfile"]
    datafile = module.params["datafile"]
    numfiles = module.params["numfiles"]
    size = module.params["size"]
    content = module.params["content"]
    autoextend = module.params["autoextend"]
    nextsize = module.params["nextsize"]
    maxsize = module.params["maxsize"]


    if not cx_oracle_exists:
        module.fail_json(msg="The cx_Oracle module is required. 'pip install cx_Oracle' should do the trick. If cx_Oracle is installed, make sure ORACLE_HOME & LD_LIBRARY_datafile is set")

    wallet_connect = '/@%s' % service_name
    try:
        if (not user and not password ): # If neither user or password is supplied, the use of an oracle wallet is assumed
            if mode == 'sysdba':
                connect = wallet_connect
                conn = cx_Oracle.connect(wallet_connect, mode=cx_Oracle.SYSDBA)
            else:
                connect = wallet_connect
                conn = cx_Oracle.connect(wallet_connect)

        elif (user and password ):
            if mode == 'sysdba':
                dsn = cx_Oracle.makedsn(host=hostname, port=port, service_name=service_name)
                connect = dsn
                conn = cx_Oracle.connect(user, password, dsn, mode=cx_Oracle.SYSDBA)
            else:
                dsn = cx_Oracle.makedsn(host=hostname, port=port, service_name=service_name)
                connect = dsn
                conn = cx_Oracle.connect(user, password, dsn)

        elif (not(user) or not(password)):
            module.fail_json(msg='Missing username or password for cx_Oracle')

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg = 'Could not connect to database - %s, connect descriptor: %s' % (error.message, connect)
        module.fail_json(msg=msg, changed=False)

    cursor = conn.cursor()

    if state in ('present','read_only','read_write','offline','online'):
        if not check_tablespace_exists(module, msg, cursor, tablespace):
            if create_tablespace(module, msg, cursor, tablespace, state, datafile, numfiles, size, content, bigfile, autoextend, nextsize, maxsize):
                newtbs = True
                ensure_tablespace_state(module, msg, cursor, tablespace, state, datafile, numfiles, size, content, bigfile, autoextend, nextsize, maxsize)
            else:
                module.fail_json(msg=msg, changed=False)
        else:
            ensure_tablespace_state(module, msg, cursor, tablespace, state, datafile, numfiles, size, content, bigfile, autoextend, nextsize, maxsize)

    elif state == 'absent':
        if check_tablespace_exists(module, msg, cursor, tablespace):
            if drop_tablespace(msg, cursor, tablespace):
                msg = 'The tablespace %s has been dropped successfully' % tablespace
                module.exit_json(msg=msg, changed=True)
        else:
            module.exit_json(msg='The tablespace %s doesn\'t exist' % tablespace, changed=False)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
