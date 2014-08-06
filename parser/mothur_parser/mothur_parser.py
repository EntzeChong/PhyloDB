import project_parser as pp
import sample_parser as sample
import database as db


# read files
f_shared = open('input/test_data/Test.silva_102.wang.tx.shared', 'r')
f_taxonomy = open('input/test_data/Test.wang.tx.1.cons.taxonomy', 'r')
f_project = open('input/test_data/meta_Project.csv', 'r')
f_sample = open('input/test_data/meta_Sample.csv', 'r')

# parse project
project_ids = pp.parse_and_import(f_project)
for p in project_ids: print p

# parse sample
sp_data = sample.parse(f_sample)
#print sp_data['Con.Fwy.1'][0][sample.ORGANISM]
#print sp_data['Con.Fwy.1'][0][sample.TITLE]

db.projects()
