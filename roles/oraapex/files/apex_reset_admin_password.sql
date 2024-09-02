--
-- Parameter:
--  - Admin-Password

define APEXADMINPASS = &1

set serverout on
set verify off

begin
  dbms_output.enable(10000);
  -- check if admin user exists
  -- => We do not update existing admin users!
  declare
    l_user_name      varchar2(30) := 'ADMIN';
    l_user_email     varchar2(240);
    l_user_id        varchar2(100);
    l_password       varchar2(50) := '&APEXADMINPASS';
    l_apex_owner     varchar2(30);
  begin
    select table_owner
      into l_apex_owner
      from all_synonyms
     where owner = 'PUBLIC'
       and table_name = 'APEX';

    execute immediate 'alter session set current_schema=' || l_apex_owner;

    dbms_output.put_line('APEX Schema: ' || l_apex_owner);

    select user_id, email_address
      into l_user_id, l_user_email
      from wwv_flow_fnd_user
     where security_group_id = 10
       and upper(user_name) = l_user_name;

    dbms_output.put_line('Admin-User (' || l_user_name || ') with user_id (' || l_user_id || ') existing!');

      -- wwv_flow_fnd_user_int.create_or_update_user (
      --   p_username => upper(l_user_name),
      --   p_email    => l_user_email,
      --   p_password => l_password );
      commit;
      dbms_output.put_line('Admin-User (' || l_user_name || ') created!');

  exception
    when no_data_found then
      raise_application_error(-20000, 'User ' || l_user_name || ' not found in APEX');
  end;
end;
/
