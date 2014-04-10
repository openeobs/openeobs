import erppeek

db = "test1"
demo = False
rollback = True

user = "admin"
pwd = "admin"

client = erppeek.Client("http://localhost:8069", verbose=True)
client.create_database(pwd, db, demo, 'en_GB', pwd)

client.install('t4clinical_demo')

client.execute('demo', 'scenario2', rollback)