import erppeek
import psycopg2
import logging
from datetime import datetime as dt
from openerp.osv import fields 

logger = logging.getLogger(__name__)
db = "demo_test15"
demo = False
rollback = True

user = "admin"
pwd = "admin"

client = erppeek.Client("http://localhost:8069", db, user, pwd, verbose=True)
now = dt.strftime(dt.now(), "%Y-%m-%d %H:%M:%S")
model = 'observation.test'

# SQL
sql_delete = "delete from observation_test where 1=1"
sql_create = "insert into observation_test (datetime, source) values('%s', 'sql')" % now
logger.info("SQL write date: %s" % now)
cn = psycopg2.connect("dbname='demo_test15' user='erp7' host='localhost' password='e'")
cr = cn.cursor()
cr.execute(sql_delete)
cr.execute(sql_create)
cn.commit()
cr.close()
cn.close()

# ORM
vals = {'datetime': now, 'source': 'orm'}
client.create('observation.test', vals)

# SQL READ

sql_read = "select datetime, source from observation_test"
cn = psycopg2.connect("dbname='demo_test15' user='erp7' host='localhost' password='e'")
cr = cn.cursor()
cr.execute(sql_read)
print "SQL Read:\n"
for rec in cr.fetchall():
    print "datetime: %s" % rec[0], "  source: %s" % rec[1]
cr.close()
cn.close()


print "ORM Read:\n"
for rec in client.read('observation.test', [], ['datetime', 'source']):
    print "datetime: %s" % rec['datetime'], "  source: %s" % rec['source']