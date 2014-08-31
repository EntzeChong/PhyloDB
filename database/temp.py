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
'''
stmt = 'update database_sample set projectid_id=\'1\', sampleid=\'3\' where sampleid=\'251970249215267570650668799591669167382\' '
c.execute(stmt)
#c.execute('PRAGMA table_info(database_sample)')
#print c.fetchall()
con.commit()
c = con.cursor()
taxa1 = 'insert into database_taxonomy values(\'3\', \'3\', \'Bacteria\', \'Proteobacteria\', \'Alphaproteobacteria\', \'Rhizobiales\', \'Bradyrhizobiaceae\', \'unclassified\', \'unclassified\', \'100\')'
c.execute(taxa1)
#c.execute('PRAGMA table_info(database_taxonomy)')
#print c.fetchall()
con.commit()
'''

'''
c= con.cursor()
id1 = utils.uniqueID();
print id1
for record_p in d_project:
    record_p.insert(0, id1)
    print record_p
    c.execute(utils.build_sql(PROJECT, record_p))
'''
# view all projects in db
c = con.cursor()
c.execute('select * from database_project')
for record in c.fetchall():
    print list(record)
c = con.cursor()
c.execute('select * from database_sample')
for record in c.fetchall():
    print list(record)
c = con.cursor()
c.execute('select * from database_taxonomy')
for record in c.fetchall():
    print list(record)

#print len(utils.uniqueID())
