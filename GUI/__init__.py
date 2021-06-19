import qimage2ndarray
from os import path
from pathlib import Path
from datetime import date
from cv2 import VideoCapture
import mysql.connector as sql
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QCompleter

class CONNECT:
    
    def __init__(self):

        self.DATAB = sql.connect(option_files=r'GUI\credentials.ini')
        self.CURSOR = self.DATAB.cursor(buffered=True)
        self.transaction = False
        self.rowcount = 0

    def execute(self, statement, arguments=None, many=0, commit=0, fetch=0):
        
        if self.transaction: return self.transaction

        self.transaction = True

        for _ in range(10):
            try:
                if many: self.CURSOR.executemany(statement, arguments)
                else: self.CURSOR.execute(statement, arguments)
                self.transaction = False

                if statement.startswith('SELECT'):
                    self.rowcount = self.CURSOR.rowcount
                else: self.rowcount = 0

                if commit: return self.DATAB.commit()
                if fetch: return self.CURSOR.fetchall()
                return list()
            
            except sql.errors.DatabaseError: self.reconnect()

        self.transaction = False
        return list()

    def rollback(self): self.DATAB.rollback()

    def reconnect(self, attempts=5, time=6):

        self.DATAB.reconnect(attempts, time)

    def commit(self): self.DATAB.commit()
    
    def close(self): self.DATAB.close()

class MyCompleter(QCompleter):

    def __def__(self, *args):
        
        super(MyCompleter, self).__init__(*args)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.PopupCompletion)
        # self.setWrapAround(False)

    # Add texts instead of replace
    def pathFromIndex(self, index):
        
        path = QCompleter.pathFromIndex(self, index)

        lst = str(self.widget().text()).split(',')

        if len(lst) > 1:
            path = '%s, %s' % (','.join(lst[:-1]), path)

        return path

    # Add operator to separate between texts
    def splitPath(self, path):
        
        path = str(path.split(',')[-1]).lstrip(' ')
        
        return [path]

def get_frame(path):

    image = VideoCapture(path).read()[-1]
    if image is None: return QPixmap()
    return qimage2ndarray.array2qimage(image).rgbSwapped()

def create_menu():

    pass

MYSQL = CONNECT()
ROOT = Path(Path().cwd().drive)
PATH = ROOT / path.expandvars(r'\Users\$USERNAME\Dropbox\ん')
parts = ", ".join([f"'{part}'" for part in PATH.parts]).replace('\\', '')
BASE = f'SELECT full_path(path, {parts}), artist, tags, rating, stars, type, site FROM imageData'
COMIC = 'SELECT parent FROM comic WHERE path_=SUBSTRING(%s, 32)'
GESTURE = f'UPDATE imageData SET date_used="{date.today()}" WHERE path=SUBSTRING(%s, 32)'
MODIFY = f'UPDATE imageData SET {{}} WHERE path=SUBSTRING(%s, 32)'
DELETE = 'DELETE FROM imageData WHERE path=SUBSTRING(%s, 32)'