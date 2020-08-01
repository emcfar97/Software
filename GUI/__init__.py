from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QFormLayout, QLabel, QLineEdit, QComboBox, QMessageBox, QDesktopWidget, QStatusBar
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

from datetime import date
from cv2 import VideoCapture
import mysql.connector as sql
from os import getcwd

class CONNECT:

    def __init__(self):

        self.DATAB, self.CURSOR = self.connect()

    def connect(self):

        DATAB = sql.connect(
            user='root', password='SchooL1@', database='userData', 
            host='127.0.0.1' if ROOT == 'C:' else '192.168.1.43'
            )
        CURSOR = DATAB.cursor(buffered=True)

        return DATAB, CURSOR

    def execute(self, statement, arguments=None, many=0, commit=0):
        
        for _ in range(20):
            try:
                if many: self.CURSOR.executemany(statement, arguments)
                else: self.CURSOR.execute(statement, arguments)

                if commit: self.DATAB.commit()
                else: return self.CURSOR.fetchall()

            except sql.errors.OperationalError: continue
            
            except sql.errors.ProgrammingError: return list()

            except: self.DATAB, self.CURSOR = self.connect()

    def close(self): self.DATAB.close()

ROOT = getcwd()[:2].upper()
CONNECTION = CONNECT()
BASE = f'SELECT REPLACE(path, "C:", "{ROOT}"), tags, artist, stars, rating, type FROM imageData'
COMIC = 'SELECT path FROM comics'
UPDATE = f'UPDATE imageData SET date_used="{date.today()}" WHERE path=REPLACE(%s, "{ROOT}", "C:")'
MODIFY = f'UPDATE imageData SET {{}} WHERE path=REPLACE(%s, "{ROOT}", "C:")'
DELETE = f'DELETE FROM imageData WHERE path=REPLACE(%s, "{ROOT}", "C:")'
NEZUMI = rf'{ROOT}\Program Files (x86)\Lazy Nezumi Pro\LazyNezumiPro.exe'
