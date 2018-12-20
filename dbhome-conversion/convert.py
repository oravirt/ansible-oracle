import os,yaml,io
from jinja2 import Environment, FileSystemLoader

target_home = 'dbhome.yml'
target_db = 'databases.yml'
target_pdb = 'pdbs.yml'
template_home = 'dbhome-template.j2'
template_db = 'db-template.j2'
template_pdb = 'pdb-template.j2'
base_dir = '../group_vars'

file_list_all = []
for root, _, filenames in os.walk(base_dir):
    for filename in filenames:
        file_list_all.append(os.path.join(root, filename))

        
env = Environment(loader = FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
template_home = env.get_template(template_home)
template_db = env.get_template(template_db)
template_pdb = env.get_template(template_pdb)

for a in file_list_all:

    if 'oracle_databases' in open(a).read():
        print "Processing: %s " % (a)
        with open(a, 'r') as sourcefile:
            config_data = yaml.load(sourcefile)
        
        a_strip = os.path.splitext(a)[0]
        
        targetfile_home = a_strip + '_' + target_home
        with open(targetfile_home , 'w') as outfile_home:
            print "\tWriting dbhome config to %s " % (targetfile_home)
            # print(template.render(config_data))
            outfile_home.write(template_home.render(config_data))
        
        targetfile_db = a_strip + '_' + target_db
        with open(targetfile_db , 'w') as outfile_db:
            print "\tWriting new db config to %s " % (targetfile_db)
            # print(template.render(config_data))
            outfile_db.write(template_db.render(config_data))
            
                    
        targetfile_pdb = a_strip + '_' + target_pdb
        with open(targetfile_pdb , 'w') as outfile_pdb:
            print "\tWriting new pdb config to %s " % (targetfile_pdb)
            print ''
            # print(template.render(config_data))
            outfile_pdb.write(template_pdb.render(config_data))

