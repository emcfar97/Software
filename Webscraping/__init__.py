import os
import mysql.connector as sql

def connect():

    DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
    CURSOR = DATAB.cursor(buffered=True)

    return DATAB, CURSOR
    
ROOT = os.getcwd()[:2].upper()
PATH = rf'{ROOT}\Users\Emc11\Dropbox\Videos\ん'

def execute(statement, arguments=None, many=0, commit=0, fetch=0):

    for _ in range(10):
        try:
            if many: CURSOR.executemany(statement, arguments)
            else: CURSOR.execute(statement, arguments)
            if commit: DATAB.commit()
            elif fetch: return CURSOR.fetchall()
            return 1
        except sql.errors.OperationalError: continue
