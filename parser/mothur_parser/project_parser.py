import utils
# parses information out of a *project*.csv file

# attributes of the .csv
PNAME, DESC, START, END, LNAME, FNAME, AFFIL, EMAIL, PHONE = 0,1,2,3,4,5,6,7,8

def parse(f_in, f_out):
    for record in parse_data(f_in):
        print record[PNAME]
