'''
* parses information out of a *project*.csv file to dbMicrobe
* does _no_ error checking as of now, so don't try to trick it with invalid input
'''
from utils import parse_to_list, build_sql, uniqueID
from database import execute, PROJECT as TABLE

# attributes of the .csv
PNAME, DESC, START, END, LNAME, FNAME, AFFIL, EMAIL, PHONE = 0,1,2,3,4,5,6,7,8

def parse_and_import(f_in):
    for record in parse_to_list(f_in):
        record.insert(0, uniqueID())
        execute(build_sql(TABLE, record))