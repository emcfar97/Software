import sys, tempfile, traceback, re
from json import load
from pathlib import Path
from imagehash import dhash
from PIL import Image, ImageGrab
from os import path, getenv, startfile
from mysql.connector import pooling, errors
from dotenv import load_dotenv, find_dotenv, set_key
from cv2 import VideoCapture, cvtColor, COLOR_BGR2RGB

# from Webscraping.utils import get_hash, get_name, get_tags, generate_tags

from PyQt6.QtGui import QAction, QActionGroup, QImage, QIcon
from PyQt6.QtCore import Qt, QRunnable, QObject, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QFormLayout, QCompleter, QLabel, QPushButton, QMenu, QLineEdit, QDialog, QDialogButtonBox, QStyle, QFileDialog, QMessageBox

load_dotenv(r'GUI\.env')
LIMIT = getenv('LIMIT', '100000')
BATCH = getenv('BATCH', '10000')
COLUMNS = int(getenv('COLUMNS', '5'))
AUTOCOMPLETE = r'GUI\managedata\autocomplete.txt'

ROOT = Path(Path().cwd().drive)
PATH = ROOT / path.expandvars(r'\Users\$USERNAME\Dropbox\ん')
SELECT = f'SELECT * FROM imagedata'
INSERT = 'INSERT INTO imagedata(path, artist, tags, rating, type, hash, src, site, href) VALUES(%s, CONCAT(" ", %s, " "), CONCAT(" ", %s, " "), %s, %s, %s, %s, %s, %s)'
UPDATE = 'UPDATE imagedata SET {} WHERE path=%s'
DELETE = 'DELETE FROM imagedata WHERE path=%s'
COMIC = 'SELECT parent FROM comic WHERE path=%s'

ENUM = {
    'All': '',
    'Photo': "type='photograph'",
    'Illus': "type='illustration'",
    'Comic': "type='comic'",
    'Explicit': 'rating<=4',
    'Questionable': 'rating<=3',
    'Sensitive': 'rating<=2',
    'General': 'rating=1',
    }
CONSTANTS = {
    'Sort': ['Rowid', 'Path', 'Artist', 'Stars', 'Hash', 'Date', 'Random'],
    'Order': ['Ascending', 'Descending'],
    'Rating': ['Explicit', 'Questionable', 'Sensitive', 'General'],
    'Type': ['All', 'Photo', 'Illus', 'Comic']
    }
MODEL = {
    'Rowid': 0,
    'Path': 1,
    'Artist': 2,
    'Tags': 3,
    'Rating': 4,
    'Stars': 5,
    'Type': 6,
    'Site': 7,
    'Date used': 8,
    'Hash': 9,
    'Href': 10,
    'Src': 11,
    }
GESTURE = {
    '30 seconds': '30', 
    '1 minute': '60', 
    '2 minutes': '120', 
    '5 minutes': '300', 
    'Custom Time': None
    }

class CONNECT(QObject):
    
    finishedTransaction = pyqtSignal(object)
    finishedSelect = pyqtSignal(object)
    finishedUpdate = pyqtSignal(object)
    finishedDelete = pyqtSignal(object)
    errorTransaction = pyqtSignal(object)

    def __init__(self, credentials):

        super(CONNECT, self).__init__()
        self.DATAB = pooling.MySQLConnectionPool(
            pool_name="mypool", pool_size=10, **credentials
            )
        self.current = ''
        self.transactions = {
                'SELECT': None,
                'INSERT': [],
                'UPDATE': [],
                'DELETE': []
                }
    
    def execute(self, statement, arguments=None, many=0, fetch=0, source=None, emit=1):
        
        type = statement.split()[0]
        
        if type == self.current: # match
            
            if type == 'SELECT' or arguments in self.transactions[type]:
                self.current = ''
                return
                
        elif type != 'SELECT': # no match
            
            self.transactions[type].append(arguments)
            self.current = type
            
        try:
            
            self.parent().setCursor(Qt.CursorShape.BusyCursor)
            
            conn = self.DATAB.get_connection()
            cursor = conn.cursor()
            
            if many: cursor.executemany(statement, arguments)
            else: cursor.execute(statement, arguments)

        except Exception as error:
            
            emit = source = None
            
            if arguments is None: error = f'{error}\n {statement}'
            else: error = f'{error}\n {statement} {arguments[0]}'
            
            self.errorTransaction.emit(error)
            
        finally:
            
            self.current = ''
            self.parent().setCursor(Qt.CursorShape.ArrowCursor)
            
            if   type == 'SELECT':
                
                self.transactions['SELECT'] = None
                
                if fetch:
                    
                    fetch = cursor.fetchall()
                    
                    cursor.close()
                    conn.close()
                    return fetch

                self.finishedSelect.emit(cursor.fetchall())
                
                cursor.close()
                conn.close()
                return
                
            elif type == 'INSERT': pass
                
            elif type == 'UPDATE':
                
                try:
                    index = self.transactions[type].index(arguments)
                    del self.transactions[type][index]
                except ValueError: pass

                self.finishedUpdate.emit(source)
                
                conn.commit()
                cursor.close()
                conn.close()
                
            elif type == 'DELETE':
                
                try:
                    index = self.transactions[type].index(arguments)
                    del self.transactions[type][index]
                except ValueError: pass

                self.finishedDelete.emit(arguments)
                
                self.cursor = cursor
                self.conn = conn

            if emit: self.finishedTransaction.emit(1)
            
    def reconnect(self, attempts=5, time=6):

        self.DATAB.reconnect(attempts, time)

    def rollback(self): self.DATAB.rollback()

    def rowcount(self):
        
        try: return self.CURSOR.rowcount
        except AttributeError: return 0

    def commit(self): self.DATAB.commit()
    
    def close(self): return; self.DATAB.close()
    
class Authenticate(QDialog):
    
    def success(self):
        
        try:
            cred = {
                'user': getenv('USER'),
                'password': getenv('PASS'),
                'host': getenv('HOST'),
                'database': getenv('DATA'),
                }
            return CONNECT(cred)

        except (errors.InterfaceError, errors.ProgrammingError, UnicodeError):
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
                env = find_dotenv()
                set_key(env, 'USER', cred['user'])
                set_key(env, 'PASS', cred['password'])
                set_key(env, 'HOST', cred['host'])
                set_key(env, 'DATA', cred['database'])
                load_dotenv()
                
                return success
    
            except Exception as error:

                message = QMessageBox.warning(self, str(error.errno), str(error))
                message.setStandardButtons(QMessageBox.StandardButton.Ok)
                
                if message == QMessageBox.StandardButton.Ok:
                    self.start()

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
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        if 'callback' in self.kwargs:
            
            self.kwargs['callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try: result = self.fn(*self.args, **self.kwargs)
        except:
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else: self.signals.result.emit(result)
        finally: self.signals.finished.emit()
         
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class Timer(QLabel):
    
    def __init__(self, parent, toplevel):
        
        super(QLabel, self).__init__(parent)
        self.toplevel = toplevel
        self.timer = QTimer()
        self.timer.timeout.connect(self.countdown)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

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

    def pause(self):

        if self.timer.isActive(): self.timer.stop()
        else: self.timer.start(1000)
    
    def reset(self): self.timer.start(1000)
           
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
                (self.image.data(Qt.ItemDataRole.DecorationRole),),
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

        self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.setWrapAround(False)

    # Add texts instead of replace
    def pathFromIndex(self, index):
        
        path = QCompleter.pathFromIndex(self, index)
        text = self.widget().text()
        
        if path in text: return text
        
        cursor = self.widget().cursorPosition()
        left = text[:cursor].split(' ')[:-1]
        right = text[cursor:].split(' ')
        
        return ' '.join(left + [path] + right)

    # Add operator to separate between texts
    def splitPath(self, path):
        
        cursor = self.widget().cursorPosition()
        path = str(path[:cursor].split(' ')[-1]).lstrip(' ')
        
        # prevents single space from being matched
        if len(path) == 0: return ['~|~']
        
        return [path]
        
def create_submenu(parent, name, items, trigger=None, check=None, get_menu=False):
    '''Create submenu based on parent widget, name, items'''
        
    if name is None: menu = parent
    else: menu = QMenu(name, parent)
    action_group = QActionGroup(menu)

    for num, item in enumerate(items):
        
        action = QAction(item, menu, checkable=True)
        if num == check: action.setChecked(True)
        action_group.addAction(action)
        menu.addAction(action)

    else:
        if name is not None: parent.addMenu(menu)
        if trigger: action_group.triggered.connect(trigger)
        action_group.setExclusive(True)
    
    if get_menu: return action_group, menu
    return action_group

def create_submenu_(parent, name, items, trigger=None, check=None):
    '''Create submenu based on parent widget, name, items'''
        
    if name is None: menu = parent
    else: menu = QMenu(name, parent)
    action_group = QActionGroup(menu)
    action_group.setExclusive(True)
    if trigger: action_group.triggered.connect(trigger)

    for num, item in enumerate(items):
        
        if isinstance(item, list):
            
            action = create_submenu_(menu, None, item[:-1], trigger, item[-1])[0]
            menu.addMenu(action)
        
        elif item is None:
            
            menu.addSeparator(); continue
        
        else:
            
            action = QAction(item, menu, checkable=(check is not None))
            if num == check: action.setChecked(True)
            action_group.addAction(action)
            menu.addAction(action)

    return menu, action_group

def create_button(parent, icon, slot, lamb=None):

    button = QPushButton(parent)
    if lamb: button.clicked.connect(lambda: slot(lamb))
    else: button.clicked.connect(slot)
    
    pixmap = getattr(QStyle, icon)
    button.setIcon(QIcon(button.style().standardIcon(pixmap)))
    button.setToolTip(re.sub('SP_Media', '', icon))
    
    return button

def get_frame(path):

    capture = VideoCapture(path)
    image = capture.read()[-1]
    capture.release()
    
    if image is None: return QImage()
    
    height, width, channel = image.shape
    bytesPerLine = 3 * width
    
    return QImage(
        image.data, width, height, bytesPerLine, QImage.Format.Format_BGR888
        )

def get_path(name): return PATH / name[0:2] / name[2:4] / name

# def get_values(path):

#     name = get_name(path)
#     tags, rating = generate_tags(
#         general=get_tags(path, True), 
#         custom=True, rating=True
#         )
    
#     return (name.name, '', ' '.join((tags)), rating, 1, get_hash(path))

def update_autocomplete(mysql):

    artist, tags = mysql.execute(
        '''SELECT 
        GROUP_CONCAT(DISTINCT artist SEPARATOR ""), 
        GROUP_CONCAT(DISTINCT tags SEPARATOR "") 
        FROM imagedata''',
        fetch=1)[0]
    text = (
        ' '.join(sorted(set(artist.split()))), 
        ' '.join(sorted(set(tags.split())))
        )
    text = '\n'.join(text).lower()
    
    with open(AUTOCOMPLETE, 'w', encoding='utf8') as file:
        
        file.write(text)
    
def remove_redundancies(mysql):

    data = load(open(r'Webscraping\constants.json', encoding='utf-8'))
    REPLACE = data['REPLACE']
    SELECT = 'SELECT path, artist, tags FROM imagedata'
    UPDATE = 'UPDATE imagedata SET artist=%s, tags=%s WHERE path=%s'

    for (path, artist, tags,) in mysql.execute(SELECT, fetch=1):

        artist = set(artist.lower().split())
        artist = re.sub('-|__', '_', f' {" ".join(artist)} ')
            
        for key, value in REPLACE.items():
            
            tags = re.sub(f' {value} ', f' {key} ', tags.lower())
            
        tags = list(set(tags.split()))
        tags = [tag for tag in tags if len(tag) >= 3]
        tags = re.sub('-|__', '_', f' {" ".join(tags)} ')
        
        mysql.execute(UPDATE, (artist, tags, path), commit=1, emit=0)

def copy_path(paths):
    
    for num, index in enumerate(paths):
        
        path = index.data(Qt.ItemDataRole.DecorationRole)
        
        if path.suffix == '.webm':

            paths[num] = tempfile.mktemp(suffix='.png')
            image = ImageGrab.grab(
                # (0, 0, self.width(),self.height())
                )
            image.save(paths[num])
        
        else: paths[num] = path

    paths = ', '.join(f'"{path}"' for path in paths)
    
    cb = QApplication.clipboard()
    cb.clear(mode=cb.Mode.Clipboard)
    cb.setText(paths, mode=cb.Mode.Clipboard)

def copy_to(widget, images):
    
    copy_dir = ROOT / getenv('COPY_DIR', '*')
    folder = QFileDialog.getExistingDirectory(
        widget, 'Open Directory', str(copy_dir)
        )
    if not folder or folder == ('', ''): return
    else: folder = Path(folder)
    
    paths = [
        index.data(Qt.ItemDataRole.DecorationRole)
        for index in images
        if index.data(Qt.ItemDataRole.FontRole) is not None
        ]
    
    for path in paths:
    
        name = folder / path.name
        name.write_bytes(path.read_bytes())
            
    set_key(r'GUI\.env', 'COPY_DIR', str(folder))
    load_dotenv(r'GUI\.env', override=True)

def open_file(index):
 
    name = index.data(Qt.ItemDataRole.DecorationRole)
    # folder = PATH / name[0:2] / name [2:4]
    startfile(name.parent)
    
def find_match(widget):
    
    filename = Path(QFileDialog.getOpenFileName(
        widget, 'Open File', directory='', 
        filter='''
            Image Files (*.png *.jpg *.webp);;
            Video Files (*.gif *.mp4 *.webm);;
            All Files (*)
            ''',
        initialFilter='Image Files (*.png *.jpg *.webp)'
        )[0])
    
    try:
        
        if re.search('jp.*g|png|webp|gif', filename.suffix, re.IGNORECASE):
            
            image = Image.open(filename)

        elif re.search('webm|mp4', filename.suffix, re.IGNORECASE):
            
            video_capture = VideoCapture(str(filename)).read()[-1]
            image = cvtColor(video_capture, COLOR_BGR2RGB)
            image = Image.fromarray(image)
        
        else: 
            
            raise TypeError(f'The extension *{filename.suffix} is not supported')
    
    except Exception as error: 
        
        QMessageBox.information(widget, 'Find Matching Image', str(error))
    
    image.thumbnail([32, 32])
    image = image.convert('L')

    return f'{SELECT} HAVING BIT_COUNT("{dhash(image)}" ^ hash) < 5'