import erppeek


new_db = "demo_test40"
new_demo = False
rollback = False

user = "admin"
pwd = "admin"
current_db = "test11"

 

client = erppeek.Client("http://localhost:8069", current_db, user, pwd, verbose=True)
client.create_database(pwd, new_db, new_demo, 'en_GB', pwd)
client.install('t4clinical_demo')
client.execute('demo', 'scenario1', rollback)