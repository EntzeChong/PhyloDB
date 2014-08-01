# in future optimize to not connect to db for every statement
import sqlite3 as sq

PATH_TO_DB = '../../dbMicrobe'
PROJECT = 'database_project'
SAMPLE = 'database_sample'
TAXONOMY = 'database_taxonomy'

def execute(sql_stmt=None):
    conn = sq.connect(PATH_TO_DB)
    cursor = conn.cursor()
    cursor.execute(sql_stmt)
    cursor.execute("SELECT * FROM database_project;")
    #cursor.execute("PRAGMA table_info(" + PROJECT + ");")
    #cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())
