import uuid
from collections import defaultdict


def uniqueID():
    return str(uuid.uuid1().int)


def parse_to_list(f, delim=','):
    return [[field.strip() for field in line.split(delim)] for line in f][1:]


# reads a file into a defaultdict using hash_index attribute as the hash and the remaining attributes as the list
def parse_to_defaultlist(f_in, hash_index):
    d = defaultdict(list)
    for record in parse_to_list(f_in):
        d[record[hash_index]].append(record[hash_index + 1:])
    return d


def build_sql(table, attributes):
    lst_attr = attributes[len(attributes) - 1]
    r_str = 'insert into ' + table + ' values('
    for attr in attributes:
        r_str += '\'' + attr + '\');' if attr is lst_attr else '\'' + attr + '\', '
    return r_str
