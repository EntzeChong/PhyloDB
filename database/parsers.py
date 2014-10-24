import re
from django.db import connection
from uuid import uuid4
from numpy import genfromtxt, savetxt


PATH_TO_DB = '../dbMicrobe'
PROJECT = 'database_project'
SAMPLE = 'database_sample'
TAXONOMY = 'database_taxonomy'


def parse_project(filepath, filename, upload_date, projectid):
    path = "/".join([str(filepath), str(filename)])
    f = open(path, 'r')
    f_in = parse_to_list(f, ',')
    for record in f_in:
        record.insert(0, upload_date)
        record.insert(0, filepath)
        record.insert(0, projectid)
        sql_project = build_sql(PROJECT, record)
        execute_sql(sql_project)


def parse_sample(filepath, filename, projectid):
    path = "/".join([str(filepath), str(filename)])
    f = open(path, 'r')
    f_in = parse_to_list(f, ',')
    for record in f_in:
        record.insert(0, projectid)
        s_uuid = uuid4().hex
        record.insert(0, s_uuid)
        sql_sample = build_sql(SAMPLE, record)
        execute_sql(sql_sample)


def transpose(filename):
    data = genfromtxt(filename)
    outfile = ".".join([str(filename), "tr"])
    savetxt(outfile, data.T)


def parse_taxonomy(filepath, filename):
    path = "/".join([str(filepath), str(filename)])
    f = open(path, 'r')
    f2 = strip_parens(f)
    f_in = parse_to_list(f2, ';')
    print f_in
    #for record in f_in:
    #    sql_sample = build_sql(TAXONOMY, record)
    #    execute_sql(sql_sample)

def parse_to_list(f, delim='\t'):
    return [[field.strip() for field in line.split(delim)] for line in f][1:]

def parse_to_list2(f, delim='\t'):
    return [[field.strip() for field[2] in line.split(delim)] for line in f][1:]

def strip_parens(txt):
    return re.sub(r'\(.*?\)', '', txt)

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
