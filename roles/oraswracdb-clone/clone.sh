perl $ORACLE_HOME/clone/bin/clone.pl ORACLE_HOME=/u01/app/oracle/12.1.0.1/testdb ORACLE_HOME_NAME=OraDBRAC ORACLE_BASE=/opt/oracle "-O CLUSTER_NODES={node1,node2}" "-O LOCAL_NODE=$THISNODE"

ORACLE_HOME_NAME=testgrid12c
ORACLE_BASE=/u01/app/oracle
ORACLE_HOME=/u01/app/oracle/12.1.0.1/testdb

perl $ORACLE_HOME/clone/bin/clone.pl -silent ORACLE_BASE=$ORACLE_BASE ORACLE_HOME=$ORACLE_HOME ORACLE_HOME_NAME=$ORAHOME_NAME -O'"CLUSTER_NODES={orarac01,orarac02}"' -O'"LOCAL_NODE=ansrac01"' 
