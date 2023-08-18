ansible orarac02 -a "/u01/app/12.1.0.2/grid/crs/install/rootcrs.pl -deconfig -force" -u root
ansible orarac01 -a "/u01/app/12.1.0.2/grid/crs/install/rootcrs.pl -deconfig -force -lastnode" -u root
ansible orarac02 -a "/u01/app/12.1.0.1/grid/crs/install/rootcrs.pl -deconfig -force" -u root
ansible orarac01 -a "/u01/app/12.1.0.1/grid/crs/install/rootcrs.pl -deconfig -force -lastnode" -u root
ansible orarac01 -a "dd if=/dev/zero of=/dev/sdc bs=1M count=100" -u root
ansible orarac01 -a "dd if=/dev/zero of=/dev/sdd bs=1M count=100" -u root
ansible orarac01 -a "dd if=/dev/zero of=/dev/sde bs=1M count=100" -u root
#ansible orarac01 -a "dd if=/dev/zero of=/dev/sdf bs=1M count=100" -u root
#ansible orarac01 -a "dd if=/dev/zero of=/dev/sdg bs=1M count=100" -u root
#ansible orarac01 -a "dd if=/dev/zero of=/dev/sdh bs=1M count=100" -u root
ansible orarac -a "rm -rf /u01/app" -u root
ansible orarac -a "rm -rf /etc/oratab" -u root
ansible orarac -a "rm -rf /etc/oraInst.loc" -u root
ansible orarac -a "chown oracle:dba /u01" -u root
echo "Rebooting servers"
ansible orarac -a "reboot" -u root
