import os
# currently exports values as tables, but can eventually link up directly to our backend DB

for f in [f for f in os.listdir('.') if os.path.isfile(f)]:
    print f

# read files
f_shared = open('Test.silva_102.wang.tx.shared', 'r')
f_taxonomy = open('Test.wang.tx.1.cons.taxonomy', 'r')
f_project = open('meta_Project.csv', 'r')
f_sample = open('meta_Sample.csv', 'r')

# write files
sql_shared = open('output/Test.silva_102.wang.tx.shared.sql', 'w')
sql_taxonomy = open('output/Test.wang.tx.1.cons.taxonomy.sql', 'w')
sql_project = open('output/meta_Project.sql', 'w')
sql_sample = open('output/meta_Sample.sql', 'w')
