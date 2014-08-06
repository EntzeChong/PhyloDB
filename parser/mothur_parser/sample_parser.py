from utils import parse_to_defaultlist

NAME = 0  # csv hash index
ORGANISM, TITLE, SEQ_METHODS, DATE, BIOME, FEATURE, LOC, LAT_LON, MATERIAL, DEPTH, ELEV = \
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10  # dict indexes


# hash 1st attribute with the rest of the record
def parse(f_in):
    return parse_to_defaultlist(f_in, NAME)
