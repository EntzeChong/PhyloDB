import os
import project_parser as pp
import sample_parser as sp
# currently exports values as tables, but can eventually link up directly to our backend DB

#for f in [f for f in os.listdir('.') if os.path.isfile(f)]: print f

# read files
f_shared = open('input/Test.silva_102.wang.tx.shared', 'r')
f_taxonomy = open('input/Test.wang.tx.1.cons.taxonomy', 'r')
f_project = open('input/meta_Project.csv', 'r')
f_sample = open('input/meta_Sample.csv', 'r')

# parse project
pp.parse_and_import(f_project)

# parse sample
sp_data = sp.parse(f_sample)
print sp_data['Sample1'][0][sp.ORGANISM]
print sp_data['Sample1'][0][sp.TITLE]
