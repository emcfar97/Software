import qimage2ndarray
from pathlib import Path
from datetime import date
from cv2 import VideoCapture
import mysql.connector as sql
from PyQt5.QtGui import QPixmap
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
                if fetch: return self.CURSOR.fetchall()
                return list()

            except (
                sql.errors.OperationalError,
                sql.errors.InterfaceError,
                sql.errors.DatabaseError
                ): 
                
                self.reconnect()
            
            except sql.errors.ProgrammingError: return list() 

        return list()

    def commit(self): self.DATAB.commit()
    
    def close(self): self.DATAB.close()

    def reconnect(self, attempts=5, time=15):

        self.DATAB.reconnect(attempts, time)

def get_frame(path):

    image = VideoCapture(path).read()[-1]
    if image is None: return QPixmap()
    return qimage2ndarray.array2qimage(image).rgbSwapped()

ROOT = Path(Path().cwd().drive)
CONNECTION = CONNECT()
path = r'''
    case type
	when 1 then CONCAT("{0}\\Users\\Emc11\\Dropbox\\ん\\エラティカ ニ\\", path)
	when 2 then CONCAT("{0}\\Users\\Emc11\\Dropbox\\ん\\エラティカ 三\\", path)
	when 3 then CONCAT("{0}\\Users\\Emc11\\Dropbox\\ん\\エラティカ 四\\", path)
    end as path
    '''.format(ROOT)
BASE = f'SELECT {path}, tags, artist, stars, rating, type, src FROM imageData'
GESTURE = f'UPDATE imageData SET date_used="{date.today()}" WHERE path=REPLACE(%s, "{ROOT}", "C:")'
MODIFY = f'UPDATE imageData SET {{}} WHERE path=SUBSTRING(%s, 34)'
DELETE = f'DELETE FROM imageData WHERE path=SUBSTRING(%s, 34)'
