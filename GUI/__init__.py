from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QTableView, QLabel, QLabel, QFormLayout, QLineEdit, QRadioButton, QComboBox, QMessageBox, QDesktopWidget, QStatusBar
from PyQt5.QtCore import Qt, QTimer, QSize, QUrl
from PyQt5.QtGui import QImage, QPixmap, QMovie

from datetime import date
from cv2 import VideoCapture
import mysql.connector as sql
from os import getcwd

ROOT = getcwd()[:2].upper()
DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor(buffered=True)
BASE = f'SELECT REPLACE(path, "C:", "{ROOT}"), tags, artist, stars, rating, type FROM imageData'
COMIC = 'SELECT path FROM comics'
UPDATE = f'UPDATE imageData SET date_used="{date.today()}" WHERE path=REPLACE(%s, "{ROOT}", "C:")'
MODIFY = f'UPDATE imageData SET {{}} WHERE path=REPLACE(%s, "{ROOT}", "C:")'
DELETE = f'DELETE FROM imageData WHERE path=REPLACE(%s, "{ROOT}", "C:")'
NEZUMI = rf'{ROOT}:\Program Files (x86)\Lazy Nezumi Pro\LazyNezumiPro.exe'