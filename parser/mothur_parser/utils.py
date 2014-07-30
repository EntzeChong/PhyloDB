import uuid

def uniqueID():
    return uuid.uuid1().int

def parse_data(f, delim=','):
    return [[field.strip() for field in line.split(delim)] for line in f]
