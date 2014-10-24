from django.db import connection
from uuid import uuid4


PATH_TO_DB = '../dbMicrobe'
PROJECT = 'database_project'
SAMPLE = 'database_sample'
TAXONOMY = 'database_taxonomy'


def parse_project(filepath, filename, projectid):
    path = "/".join([str(filepath), str(filename)])
    f = open(path, 'r')
    f_in = parse_to_list(f, ',')
    for record in f_in:
        p_uuid = projectid
        record.insert(0, p_uuid)
        sql_project = build_sql(PROJECT, record)
        execute_sql(sql_project)


def parse_sample(filepath, filename, projectid):
    path = "/".join([str(filepath), str(filename)])
    f = open(path, 'r')
    f_in = parse_to_list(f, ',')
    for record in f_in:
        p_uuid = projectid
        record.insert(0, p_uuid)
        s_uuid = uuid4().hex
        record.insert(0, s_uuid)
        sql_sample = build_sql(SAMPLE, record)
        execute_sql(sql_sample)


def parse_to_list(f, delim='\t'):
    return [[field.strip() for field in line.split(delim)] for line in f][1:]


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
