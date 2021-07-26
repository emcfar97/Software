import qimage2ndarray
from os import path
from pathlib import Path
from datetime import date
from functools import wraps
from cv2 import VideoCapture
import mysql.connector as sql
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QCompleter, QMenu, QAction, QActionGroup

class CONNECT:
    
    def __init__(self):

        self.DATAB = sql.connect(option_files=r'GUI\credentials.ini')
        self.CURSOR = self.DATAB.cursor(buffered=True)
        self.transaction = False
        self.rowcount = 0

    def execute(self, statement, arguments=None, many=0, commit=0, fetch=0):
        
        if self.transaction: return self.transaction

        self.transaction = True

        for _ in range(5):
            try:
                if many: self.CURSOR.executemany(statement, arguments)
                else: self.CURSOR.execute(statement, arguments)
                self.transaction = False

                if statement.startswith('SELECT'):
                    self.rowcount = self.CURSOR.rowcount
                else: self.rowcount = 0

                if commit: return self.DATAB.commit()
                if fetch: return self.CURSOR.fetchall()
            
            except (sql.errors.DatabaseError, sql.errors.InterfaceError):
                
                self.reconnect()
        
        self.transaction = False
        return list()

    def rollback(self): self.DATAB.rollback()

    def reconnect(self, attempts=10, time=6):

        self.DATAB.reconnect(attempts, time)

    def commit(self): self.DATAB.commit()
    
    def close(self): self.DATAB.close()

class Worker(QThread):

    def __init__(self, target, *args, **kwargs):

        super().__init__()
        self._target = target
        self._args = args
        self._kwargs = kwargs

    def run(self):

        self._target(*self._args, **self._kwargs)

def run(func):

    @wraps(func)
    def async_func(*args, **kwargs):

        runner = Worker(func, *args, **kwargs)
        func.__runner = runner
        runner.start()

    return async_func
    
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

def create_submenu(parent, name, items, check=None, get_menu=False):
        
    if name is None: menu = parent
    else: menu = QMenu(name, parent)
    action_group = QActionGroup(menu)

    for num, item in enumerate(items):
        action = QAction(item, menu, checkable=True)
        if num == check: action.setChecked(True)
        action_group.triggered.connect(parent.parent().parent().populate)
        action_group.addAction(action)
        menu.addAction(action)

    else:
        if name is not None: parent.addMenu(menu)
        action_group.setExclusive(True)
    
    if get_menu: return action_group, menu
    return action_group

def remove_redundancies():

    from Webscraping import CONNECT

    MYSQL = CONNECT()  
    SELECT = 'SELECT path, artist, tags FROM imagedata WHERE NOT ISNULL(path)'
    UPDATE = 'UPDATE imagedata SET artist=%s, tags=%s WHERE path=%s'

    for (path, artist, tags,) in MYSQL.execute(SELECT, fetch=1):

        artist = f' {" ".join(set(artist.split()))} '
        tags = f' {" ".join(set(tags.split()))} '
        MYSQL.execute(UPDATE, (artist, tags, path))

    MYSQL.commit()
    MYSQL.close()

def update_autocomplete():

    from pathlib import Path
    from Webscraping import CONNECT

    MYSQL = CONNECT()
    
    MYSQL.execute('SET GLOBAL group_concat_max_len=10000000')
    artist, tags = MYSQL.execute(
        '''SELECT 
        GROUP_CONCAT(DISTINCT artist ORDER BY artist SEPARATOR ""), 
        GROUP_CONCAT(DISTINCT tags ORDER BY tags SEPARATOR "") 
        FROM imagedata''',
        fetch=1)[0]
    text = (
        ' '.join(sorted(set(artist.split()))), 
        ' '.join(sorted(set(tags.split())))
        )
    text = ('\n'.join(text)).encode('ascii', 'ignore')
    Path(r'GUI\autocomplete.txt').write_text(text.decode())
    
    MYSQL.close()

BATCH = 10000
ROOT = Path(Path().cwd().drive)
PATH = ROOT / path.expandvars(r'\Users\$USERNAME\Dropbox\ん')
parts = ", ".join([f"'{part}'" for part in PATH.parts]).replace('\\', '')
BASE = f'SELECT full_path(path, {parts}), artist, tags, rating, stars, type, site FROM imagedata'
COMIC = 'SELECT parent FROM comic WHERE path_=get_name(%s)'
GESTURE = f'UPDATE imagedata SET date_used="{date.today()}" WHERE path=get_name(%s)'
MODIFY = 'UPDATE imagedata SET {} WHERE path=get_name(%s)'
DELETE = 'DELETE FROM imagedata WHERE path=get_name(%s)'