from pathlib import Path
from datetime import date
import mysql.connector as sql
from configparser import ConfigParser

class CONNECT:
    
    def __init__(self):
    
        credentials = ConfigParser(delimiters='=') 
        credentials.read('credentials.ini')

        self.DATAB = sql.connect(
            user=credentials.get('mysql', 'username'), 
            password=credentials.get('mysql', 'password'), 
            database=credentials.get('mysql', 'database'), 
            host=credentials.get('mysql', 'hostname')
            )
        self.CURSOR = self.DATAB.cursor(buffered=True)

    def execute(self, statement, arguments=None, many=0, commit=0, fetch=0):
        
        for _ in range(10):

            try:
                if many: self.CURSOR.executemany(statement, arguments)
                else: self.CURSOR.execute(statement, arguments)

                if commit: return self.DATAB.commit()
                elif fetch: return self.CURSOR.fetchall()
                else: return list()

            except sql.errors.OperationalError as error: continue
            
            except sql.errors.ProgrammingError: return list()
            
            except sql.errors.DatabaseError: self.__init__()

            except Exception as error: print(error)

    def commit(self): self.DATAB.commit()
    
    def close(self): self.DATAB.close()

ROOT = Path().cwd().drive
CONNECTION = CONNECT()
BASE = f'SELECT REPLACE(path, "C:", "{ROOT}"), tags, artist, stars, rating, type, src FROM imageData'
UPDATE = f'UPDATE imageData SET date_used="{date.today()}" WHERE path=REPLACE(%s, "{ROOT}", "C:")'
MODIFY = f'UPDATE imageData SET {{}} WHERE path=REPLACE(%s, "{ROOT}", "C:")'
DELETE = f'DELETE FROM imageData WHERE path=REPLACE(%s, "{ROOT}", "C:")'
NEZUMI = rf'{ROOT}\Program Files (x86)\Lazy Nezumi Pro\LazyNezumiPro.exe'
