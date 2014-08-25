import utils, re
import sqlite3 as lite

PROJECT = 'database_project'
SAMPLE = 'database_sample'
TAXONOMY = 'database_taxonomy'

d_sample = utils.parse_to_list(open('../uploads/temp/meta_Sample.csv', 'r'), ',')
d_project = utils.parse_to_list(open('../uploads/temp/meta_Project.csv', 'r'), ',')

d_taxas = utils.parse_taxonomy_file(open('../uploads/temp/Test.wang.tx.1.cons.taxonomy', 'r'))

'''
for otu in d_taxas:
    print otu + ':' + str(d_taxas[otu])
    print d_taxas['Otu001']
    print d_taxas['Otu014']
'''

con = lite.connect('../dbMicrobe')

# clear db
c = con.cursor()
c.execute('DELETE FROM database_project')
con.commit()

c= con.cursor()
id1 = utils.uniqueID();
print id1
for record_p in d_project:
    record_p.insert(0, id1)
    print record_p
    c.execute(utils.build_sql(PROJECT, record_p))

# view all projects in db
c = con.cursor()
c.execute('select * from database_project')
for record in c.fetchall():
    print record

#print len(utils.uniqueID())
