import uuid
from collections import defaultdict
from django.db import connection

PATH_TO_DB = '../dbMicrobe'
PROJECT = 'database_project'
SAMPLE = 'database_sample'
TAXONOMY = 'database_taxonomy'


def uniqueID():
    return str(uuid.uuid1().int)


def parse_to_list(f, delim='\t'):
    return [[field.strip() for field in line.split(delim)] for line in f][1:]


def parse_to_defaultdict(f_in, hash_index=0):
    d = defaultdict(list)
    for record in parse_to_list(f_in):
        d[record[hash_index]].append(record[hash_index + 1:])
    return d


def build_sql(table, attributes):
    lst_attr = attributes[len(attributes) - 1]
    r_str = 'insert into ' + table + ' values('
    for attr in attributes:
        value = str(attr)
        r_str += '\'' + value + '\');' if attr is lst_attr else '\'' + value + '\', '
    return r_str


def execute_sql(sql_stmt):
    cursor = connection.cursor()
    cursor.execute(sql_stmt)


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text
