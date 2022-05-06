import os, dotenv, traceback, sys
from pathlib import Path
import mysql.connector as sql
from mysql.connector import pooling
from cv2 import VideoCapture, cvtColor, COLOR_BGR2RGB

from PyQt6.QtGui import QAction, QActionGroup, QImage, QPixmap
from PyQt6.QtCore import QRunnable, Qt, QObject, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QFormLayout, QLabel, QMenu, QLineEdit, QDialog, QDialogButtonBox, QFileDialog, QMessageBox

BATCH = 10000
AUTOCOMPLETE = r'GUInew\managedata\autocomplete.txt'

ROOT = Path(Path().cwd().drive)
PATH = ROOT / os.path.expandvars(r'\Users\$USERNAME\Dropbox\ん')
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

    def __init__(self, credentials):

        super(CONNECT, self).__init__()
        self.DATAB = pooling.MySQLConnectionPool(
            pool_name="mypool", pool_size=10,
            pool_reset_session=True, **credentials
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
            
            if arguments in self.transactions[type]: return
            
            # elif type == 'SELECT': return
                
        self.transactions[type].append(arguments)
        # elif type != 'SELECT': self.transactions[type].append(arguments)
        
        try:
            self.current = type
            conn = self.DATAB.get_connection()
            cursor = conn.cursor()
            
            if many: cursor.executemany(statement, arguments)
            else: cursor.execute(statement, arguments)
            self.current = ''
                
        except Exception as error:
            
            QMessageBox.warning(self, str(error.errno), str(error))
            cursor.close()
            conn.close()
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

    def rowcount(self): return self.CURSOR.rowcount

    def commit(self): self.DATAB.commit()
    
    def close(self): return; self.DATAB.close()
    
class Authenticate(QDialog):
    
    def success(self):

        try: 
            cred = {
                'user': os.getenv('USER'),
                'password': os.getenv('PASS'),
                'host': os.getenv('HOST'),
                'database': os.getenv('DATA'),
                }
            return CONNECT(cred)

        except (sql.errors.InterfaceError, sql.errors.ProgrammingError, UnicodeError):
            self.start()
    
    def start(self):

        super().__init__()

        self.setWindowTitle("Enter your credentials")

        QBtn = QDialogButtonBox.StandardButton.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        password = QLineEdit()
        password.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout = QFormLayout()
        self.layout.addRow('Username:', QLineEdit())
        self.layout.addRow('Password:', password)
        self.layout.addRow('Hostname:', QLineEdit())
        self.layout.addRow('Database:', QLineEdit())

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.exec()
        
        if QBtn == QDialogButtonBox.StandardButton.Ok:

            cred = {
                'user': self.layout.itemAt(1).widget().text(),
                'password': self.layout.itemAt(3).widget().text(),
                'host': self.layout.itemAt(5).widget().text(),
                'database': self.layout.itemAt(7).widget().text()
                }

            try:

                success = CONNECT(cred)
                env = dotenv.find_dotenv()
                dotenv.set_key(env, 'USER', cred['user'])
                dotenv.set_key(env, 'PASS', cred['password'])
                dotenv.set_key(env, 'HOST', cred['host'])
                dotenv.set_key(env, 'DATA', cred['database'])

                return success
    
            except (sql.errors.InterfaceError, ValueError):

                message = QMessageBox(self)
                message.setWindowTitle('Error')
                message.setText('The entered credentials are incorrect')
                message.setStandardButtons(QMessageBox.StandardButton.Ok)
                
                if message == QMessageBox.StandardButton.Ok:
                    self.start()

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
        self.current = next(self.gallery)
        parent.update(self.current)
        
        self.setGeometry(
            int(parent.width() * .85), 
            int(parent.height() * .85), 
            75, 75
            )
        self.setStyleSheet('background: white; font: 20px')
        
        self.time, self.current = time, time
        self.updateText()
        self.timer.start(1000)

    def updateText(self):

        self.current = (self.current - 1) % self.time
        self.setText('{}:{:02}'.format(*divmod(self.current, 60)))
        self.setStyleSheet(f'''
            background: white; font: 20px;
            color: {"red" if self.current <= 5 else "black"}
            ''')
        
    def pause(self):

        if self.timer.isActive(): self.timer.stop()
        else: self.timer.start(1000)
           
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
        
def center(widget):
    'Return center coordinates for a given widget'
    
    fr = widget.frameGeometry()
    cp = widget.screen().availableGeometry().center()

    qr.moveCenter(cp)
    qr.topLeft()

    return qr.topLeft()
        
def create_submenu(parent, name, items, trigger, check=0, get_menu=False):
        
    if name is None: menu = parent
    else: menu = QMenu(name, parent)
    action_group = QActionGroup(menu)

    for num, item in enumerate(items):
        
        action = QAction(item, menu, checkable=True)
        if num == check: action.setChecked(True)
        action.triggered.connect(trigger)
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
    
    image = cvtColor(image, COLOR_BGR2RGB)
    h, w, ch = image.shape
    bytes_per_line = ch * w
    image = QImage(
        image.data, w, h, bytes_per_line, 
        QImage.Format.Format_RGB888
        )
    
    return QPixmap.fromImage(image)

def update_autocomplete():

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
    Path(AUTOCOMPLETE).write_text(text.decode())
    
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

def copy_to(widget, images):

        env = dotenv.find_dotenv()
        directory = os.getenv('COPY_DIR')

        paths = [
            Path(index.data(Qt.ItemDataRole.UserRole)[0])
            for index in images
            if index.data(300) is not None
            ]
            
        folder = Path(QFileDialog.getExistingDirectory(
            widget, 'Open Directory', directory
            ))

        for path in paths:

            name = folder / path.name
            name.write_bytes(path.read_bytes())

        dotenv.set_key(env, 'COPY_DIR', folder)