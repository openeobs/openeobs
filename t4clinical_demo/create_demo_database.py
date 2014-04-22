import erppeek

full_demo = False
demo_modules = []
install_modules = ['t4clinical_demo']
run_list = [{'module': 'demo', 'method': 'scenario2', 'args': [], 'kwargs':{}}]

rollback = False

user = "admin"
pwd = "admin"

client = erppeek.Client("http://localhost:8069", verbose=True)
# Auto db_name like test999
max_db_idx = 0

increment_strings = [db_name.split('test')[1] for db_name in client.db.list() if db_name.startswith('test')]
#import pdb; pdb.set_trace()
increments = []
for inc_str in increment_strings:
    try:
        inc_int = int(inc_str)
    except:
        pass
    else:
        increments.append(inc_int)
increment = increments and max(increments)+1 or 1
db_name = "test%s" % str(increment)
        
client.create_database(pwd, db_name, full_demo, 'en_GB', pwd)

client.install(*install_modules)

# set demo 
demo_module_ids = client.search('ir.module.module', [['name','in',demo_modules]])
client.write('ir.module.module', demo_module_ids, {'demo': 1})

# run list FIXME: ignoring rollback argument...
for run in run_list:
    run['kwargs'].update({'rollback': rollback})
    client.execute(run['module'], run['method'], *run['args'], **run['kwargs'])

