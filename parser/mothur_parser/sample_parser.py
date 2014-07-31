from collections import defaultdict
import utils

NAME = 0
ORGANISM, TITLE, SEQ_METHODS, DATE, BIOME, FEATURE, LOC, LAT_LON, MATERIAL, DEPTH, ELEV = 0,1,2,3,4,5,6,7,8,9,10

def parse(f_in):
    d = defaultdict(list)
    for record in utils.parse_data(f_in):
        d[record[NAME]].append(record[NAME+1:])
    return d
