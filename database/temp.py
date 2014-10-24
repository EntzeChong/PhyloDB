import sqlite3 as lite
import utils


PROJECT = 'database_project'
SAMPLE = 'database_sample'
TAXONOMY = 'database_taxonomy'

#d_sample = utils.parse_to_list(open('../uploads/temp/meta_Sample.csv', 'r'), ',')
#d_project = utils.parse_to_list(open('../uploads/temp/meta_Project.csv', 'r'), ',')

#d_taxas = utils.parse_taxonomy_file(open('../uploads/temp/Test.wang.tx.1.cons.taxonomy', 'r'))

'''
for otu in d_taxas:
    print otu + ':' + str(d_taxas[otu])
    print d_taxas['Otu001']
    print d_taxas['Otu014']

con = lite.connect('../dbMicrobe')

# clear db
c = con.cursor()
c.execute('DELETE FROM database_project')
con.commit()

#c= con.cursor()
#id1 = utils.uniqueID();
#print id1
#for record_p in d_project:
#    record_p.insert(0, id1)
#    print record_p
#    c.execute(utils.build_sql(PROJECT, record_p))

# view all projects in db
#c = con.cursor()
#c.execute('select * from database_project')
#for record in c.fetchall():
#    print record




#parse biome version 1
import json
json_file = '../uploads/temp/study_928.biom'
json_data = open(json_file)
json_obj = json.load(json_data)
json_data.close()

taxa_dict = {}
sample_dict = {}
count_dict = {}

rows = json_obj["rows"]
columns = json_obj["columns"]
data = json_obj["data"]
i=0
#for row in rows:
#    t_metadata = rows["metadata"]
#    t_taxonomy = t_metadata["taxonomy"]
#    t_kingdom = t_taxonomy[0]
#    taxa_dict[i] = t_taxonomy
#    i = i +1

#print taxa_dict

#for column in data:
#    column = data["columns"][0]["id"]
#    s_metadata = data["columns"][0]["metadata"]
#    sample_dict[column] = s_metadata
#    counts = data["data"][0]
#    row_fk = counts[0]
#    column_fk = counts[1]
#    reads = counts[2]
#    count_dict[row_fk] = reads
#    count_dict[column_fk] = reads

#print taxa_dict
#print sample_dict
#print count_dict



#from biom.parse import parse_biom_table
#with open('../uploads/temp/study_928.biom') as f:
#    otu_table = parse_biom_table(f)

#with open('../uploads/temp/table.csv', 'w') as f_out:
#    f_out.write(str(otu_table))
#f_out.close()





import csv
from database.models import Sample as myModel

csvfile = open('../uploads/temp/meta_Sample.csv', 'r')
reader = csv.DictReader(csvfile)

#projectid = uniqueID()
#for row in reader:
#    sampleid = uniqueID()
#    row["projectid"] = projectid
#    row["sampleid"] = sampleid
#    myModel.objects.create(**row)
#    print row


import re
from collections import defaultdict

def parse_to_defaultdict(f_in, hash_index=0):
    d = defaultdict(list)
    for record in parse_to_list(f_in):
        d[record[hash_index]].append(record[hash_index + 1:])
    return d

def strip_parens(txt):
    return re.sub(r'\(.*?\)', '', txt)  # strip parents and everything inside

def parse_taxa(taxa_raw):
    taxa_list = list()
    for t in taxa_raw.split(';')[:-1]:  # get all but last element since it is empty
        taxa_list.append(strip_parens(t))
    return taxa_list

OTU, SIZE, TAXA = 0, 1, 2
def parse_taxonomy_file(f):
    taxa_dict = dict()
    for record in parse_to_list(f):
        taxa_dict[record[OTU]] = parse_taxa(record[TAXA])  # hash otu name to its taxonomy list
    return taxa_dict


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text



'''
