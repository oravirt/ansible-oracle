--
-- Parameter:
--  - APEX-Version
--  - Admin-Username
--  - Admin-Password
--  - Admin-Email

define APEXVERSION = &1
define APEXUSER = &2
define APEXPASS = &3
define APEXEMAIL = &4

set serverout on
set verify off

begin
  dbms_output.enable(10000);
  -- check if admin user exists
  -- => We do not update existing admin users!
  declare
    l_user_id        varchar2(100);
    l_password       varchar2(50) := '&APEXPASS';
  begin
    select user_id
      into l_user_id
      from &APEXVERSION..wwv_flow_fnd_user
     where security_group_id = 10
       and upper(user_name) = upper('&APEXUSER');

    dbms_output.put_line('Admin-User (&APEXUSER) with user_id(' || l_user_id || ') existing!');
  exception
    when no_data_found then
      -- admin-user not found
      -- => we can created him!
      &APEXVERSION..wwv_flow_instance_admin.create_or_update_admin_user (
        p_username => upper( '&APEXUSER.' ),
        p_email    => '&APEXEMAIL.',
        p_password => l_password );
      commit;
      dbms_output.put_line('Admin-User (&APEXUSER) created!');
  end;
end;
/
