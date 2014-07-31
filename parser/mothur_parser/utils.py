import uuid

def uniqueID():
    return str(uuid.uuid1().int)

def parse_data(f, delim=','):
    return [[field.strip() for field in line.split(delim)] for line in f][1:]

def build_sql(table, attributes):
    lst_attr = attributes[len(attributes) - 1]
    r_str = 'insert into ' + table + ' values('
    for attr in attributes:
        r_str += '\''+ attr +'\');' if attr is lst_attr else '\''+ attr +'\', '    
    return r_str
