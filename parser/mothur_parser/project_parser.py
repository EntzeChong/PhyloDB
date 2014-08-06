'''
* parses information out of a *project*.csv file to dbMicrobe
* does _no_ error checking as of now, so don't try to trick it with invalid input
'''
from utils import parse_to_list, build_sql, uniqueID
from database import execute, PROJECT as TABLE


def parse_and_import(f_in):
    uuids = list()
    for record in parse_to_list(f_in):
        uuid = uniqueID()
        record.insert(0, uuid)
        execute(build_sql(TABLE, record))
        uuids.append(uuid)
    return uuids
