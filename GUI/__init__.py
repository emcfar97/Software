import qimage2ndarray, traceback
from os import path
from pathlib import Path
from cv2 import VideoCapture
import mysql.connector as sql
from mysql.connector import pooling
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRunnable, Qt, QObject, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QCompleter, QLabel, QMenu, QAction, QActionGroup, QFileDialog, QMessageBox

BATCH = 10000
CREDENTIALS = r'GUI\credentials.ini'
AUTOCOMPLETE = r'GUI\autocomplete.txt'

ROOT = Path(Path().cwd().drive)
PATH = ROOT / path.expandvars(r'\Users\$USERNAME\Dropbox\ん')
parts = ", ".join([f"'{part}'" for part in PATH.parts]).replace('\\', '')
BASE = f'SELECT full_path(imagedata.path, {parts}), artist, tags, rating, stars, type, site FROM imagedata'
COMIC = 'SELECT parent FROM comic WHERE path=get_name(%s)'
UPDATE = 'UPDATE imagedata SET {} WHERE path=get_name(%s)'
DELETE = 'DELETE FROM imagedata WHERE path=get_name(%s)'

class CONNECT(QObject):
    
    finishedTransaction = pyqtSignal(object)
    finishedSelect = pyqtSignal(object)
    finishedUpdate = pyqtSignal(object)
    finishedDelete = pyqtSignal(object)

    def __init__(self, parent):

        super(CONNECT, self).__init__(parent)
        self.DATAB = pooling.MySQLConnectionPool(
            pool_name="mypool", pool_size=10,
            pool_reset_session=True,
            option_files=CREDENTIALS
            )
        self.current = ''
        self.transactions = {
            'SELECT': None,
            'UPDATE': [],
            'DELETE': []
            }
    
    def execute(self, statement, arguments=None, many=0, fetch=0, source=None, emit=1):
        
        type = statement.split()[0]
        match = type == self.current
        
        if match:
            
            if type == 'SELECT': return
            
            elif arguments in self.transactions[type]: return
                
        elif type != 'SELECT': self.transactions[type].append(arguments)
        
        try:
            self.current = type
            conn = self.DATAB.get_connection()
            cursor = conn.cursor()
            
            if many: cursor.executemany(statement, arguments)
            else: cursor.execute(statement, arguments)
            self.current = ''

        except sql.errors.ProgrammingError as error:
            
            message = QMessageBox(
                QMessageBox.warning, str(error.errno), str(error)
                )
            message.show()
            return

        # except sql.errors.DatabaseError as error:

            # print('Database', error)
            # if error.errno == 1205: return
            # self.reconnect(1, 3)
            
            # return

        except sql.errors.InterfaceError as error:

            print('Interface', error)
            # self.reconnect(1, 3)

            return
            
        except Exception as error:
        
            print('Error', error)
            return
        
        finally:
                
            if   statement.startswith('SELECT'):
                
                self.transactions[type] = None
                
                if fetch: 
                    fetch = cursor.fetchall()
                    cursor.close()
                    conn.close()
                    return fetch

                self.finishedSelect.emit(cursor.fetchall())
                cursor.close()
                conn.close()
                return
                
            elif statement.startswith('UPDATE'):
                
                index = self.transactions[type].index(arguments)
                del self.transactions[type][index]

                self.finishedUpdate.emit(source)
                
                conn.commit()
                cursor.close()
                conn.close()
                
            elif statement.startswith('DELETE'):
                
                index = self.transactions[type].index(arguments)
                del self.transactions[type][index]

                self.finishedDelete.emit(arguments)
                
                self.cursor = cursor
                self.conn = conn

            if emit: self.finishedTransaction.emit(1)
            
    def rollback(self): self.DATAB.rollback()

    def reconnect(self, attempts=5, time=6):

        self.DATAB.reconnect(attempts, time)

    def commit(self): self.DATAB.commit()
    
    def rowcount(self): return self.CURSOR.rowcount

    def close(self): return; self.DATAB.close()
    
class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    '''

    def __init__(self, fn, *args, **kwargs):
        
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try: result = self.fn(*self.args, **self.kwargs)
        except: traceback.print_exc()

class Timer(QLabel):
    
    def __init__(self, parent, toplevel):
        
        super(QLabel, self).__init__(parent)
        
        self.toplevel = toplevel
        self.timer = QTimer()
        self.timer.timeout.connect(self.countdown)
        self.setAlignment(Qt.AlignCenter)

    def start(self, gallery,  time):
        
        parent = self.parent()
        self.gallery = iter(gallery)
        self.image = next(self.gallery)
        parent.update(self.image)
        
        self.setGeometry(
            int(parent.width() * .85), 
            int(parent.height() * .85), 
            75, 75
            )
        self.setStyleSheet('background: white; font: 20px')
        
        self.time, self.current = time, time
        self.updateText()
        self.timer.start(1000)

    def pause(self):

        if self.timer.isActive(): self.timer.stop()
        else: self.timer.start(1000)

    def updateText(self, delta=1):

        self.current = (self.current - delta) % self.time
        self.setText('{}:{:02}'.format(*divmod(self.current, 60)))
        self.setStyleSheet(f'''
            background: white; font: 20px;
            color: {"red" if self.current <= 5 else "black"}
            ''')
           
    def countdown(self):
        
        if self.current: self.updateText()
        
        else:

            worker = Worker(
                self.toplevel.mysql.execute, 
                UPDATE.format(f'date_used=CURDATE()'),
                [self.image.data(Qt.UserRole)[0]],
                emit=0
                )
            self.toplevel.threadpool.start(worker)
            self.updateText()
        
            try:
                self.image = next(self.gallery)
                self.parent().update(self.image)

            except StopIteration:

                self.timer.stop()
                self.parent().update()
                self.setText('End of session')
                self.setStyleSheet(
                    'background: black; color: white; font: 20px'
                    )
                self.setGeometry(
                        int(self.parent().width() * .4),
                        int(self.parent().height() * .1),
                        125, 75
                        )
class Completer(QCompleter):

    def __init__(self, model, parent=None):

        super(Completer, self).__init__(model, parent)

        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setWrapAround(False)

    # # Add texts instead of replace
    # def pathFromIndex(self, index):

    #     path = QCompleter.pathFromIndex(self, index)

    #     lst = str(self.widget().text()).split(',')

    #     if len(lst) > 1:
    #         path = '%s, %s' % (','.join(lst[:-1]), path)

    #     return path

    # # Add operator to separate between texts
    # def splitPath(self, path):

    #     path = str(path.split(',')[-1]).lstrip(' ')
        
    #     return [path]
        
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

def get_frame(path):

    image = VideoCapture(path).read()[-1]
    if image is None: return QPixmap()
    return qimage2ndarray.array2qimage(image).rgbSwapped()

def update_autocomplete():

    from pathlib import Path
    from Webscraping import CONNECT

    MYSQL = CONNECT()
    
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

def remove_redundancies():

    from Webscraping import CONNECT

    MYSQL = CONNECT()  
    SELECT = 'SELECT path, artist, tags FROM imagedata WHERE NOT ISNULL(path)'
    UPDATE = 'UPDATE imagedata SET artist=%s, tags=%s WHERE path=%s'

    for (path, artist, tags,) in MYSQL.execute(SELECT, fetch=1):

        artist = f' {" ".join(set(artist.split()))} '.replace('-', '_')
        tags = f' {" ".join(set(tags.split()))} '.replace('-', '_')
        MYSQL.execute(UPDATE, (artist, tags, path))

    MYSQL.commit()
    MYSQL.close()

def copy_to(widget, images, sym=False):

        paths = [
            Path(index.data(Qt.UserRole)[0])
            for index in images
            if index.data(300) is not None
            ]
            
        folder = Path(QFileDialog.getExistingDirectory(
            widget, 'Open Directory', str(PATH.parent),
            ))

        for path in paths:

            name = folder / path.name
            if sym and not name.exists(): name.symlink_to(path)
            else: name.write_bytes(path.read_bytes())