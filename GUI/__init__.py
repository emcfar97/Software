from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QFormLayout, QLabel, QLineEdit, QComboBox, QMessageBox, QDesktopWidget, QStatusBar
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

from datetime import date
from cv2 import VideoCapture
import mysql.connector as sql
from pathlib import Path

class CONNECT:
    
    def __init__(self):

        self.DATAB = sql.connect(
            user='root', password='SchooL1@', database='userData', 
            host='127.0.0.1' if ROOT.drive == 'C:' else '192.168.1.43'
            )
        self.CURSOR = self.DATAB.cursor(buffered=True)

    def execute(self, statement, arguments=None, many=0, commit=0, fetch=0):
        
        for _ in range(20):

            try:
                if many: self.CURSOR.executemany(statement, arguments)
                else: self.CURSOR.execute(statement, arguments)

                if commit: return self.DATAB.commit()
                elif fetch: return self.CURSOR.fetchall()

            except sql.errors.OperationalError: continue
            
            except sql.errors.DatabaseError: self.__init__()

            except Exception as error: print(error)

    def commit(self): self.DATAB.commit()
    
    def close(self): self.DATAB.close()

ROOT = pathlib.Path().cwd().parent
CONNECTION = CONNECT()
BASE = f'SELECT REPLACE(path, "C:", "{ROOT}"), tags, artist, stars, rating, type FROM imageData'
COMIC = 'SELECT path FROM comics'
UPDATE = f'UPDATE imageData SET date_used="{date.today()}" WHERE path=REPLACE(%s, "{ROOT}", "C:")'
MODIFY = f'UPDATE imageData SET {{}} WHERE path=REPLACE(%s, "{ROOT}", "C:")'
DELETE = f'DELETE FROM imageData WHERE path=REPLACE(%s, "{ROOT}", "C:")'
NEZUMI = rf'{ROOT}\Program Files (x86)\Lazy Nezumi Pro\LazyNezumiPro.exe'
