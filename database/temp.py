import utils, re

# views wasnt updated so I am re-parsing samples here to get the sampleids
OTU, SIZE, TAXA = 0, 1, 2


def strip_parens(txt):
    return re.sub(r'\(.*?\)', '', txt) # strip parents and everything inside

def parse_taxa(taxa_raw):
    taxa_list = list()
    for t in taxa_raw.split(';')[:-1]: # get all but last element since it is empty
        taxa_list.append(strip_parens(t))
    return taxa_list

def parse_taxonomy_file(f):
    taxa_dict = dict()
    for record in utils.parse_to_list(f):
        taxa_dict[record[OTU]] = parse_taxa(record[TAXA]) # hash otu name to its taxonomy list
    return taxa_dict


d_taxas = parse_taxonomy_file(open('../uploads/temp/Test.wang.tx.1.cons.taxonomy', 'r'))
for otu in d_taxas:
    print otu + ':' + str(d_taxas[otu])

print d_taxas['Otu001']
print d_taxas['Otu014']
#print len(utils.uniqueID())
