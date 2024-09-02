set serverout on

begin
  for cur1 in (select VERSION_NO
                 from apex_release) loop

    dbms_output.put_line('APEX Version: ' || cur1.version_no);
    apex_instance_admin.set_parameter
      (
        p_parameter => 'IMAGE_PREFIX',
        p_value     => 'https://static.oracle.com/cdn/apex/' || cur1.version_no || '/'
      );

  end loop;
  commit;
end;
/
