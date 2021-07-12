import re
from .. import BASE
from .imageView import ImageView, Worker
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QFormLayout, QAbstractItemView, QMenu, QAction, QPushButton, QCheckBox, QStyle, QCompleter

AUTOCOMPLETE = r'GUI\autocomplete.txt'
ENUM = {
    'All': '',
    'Photo': 'type=1', 
    'Illus': 'type=2', 
    'Comic': 'type=3',
    'Explicit': '',
    'Questionable': 'rating<3',
    'Safe': 'rating=1',
    }

class Gallery(QWidget):
     
    def __init__(self, parent, margins=(5, 0, 0, 0)):
         
        super(Gallery, self).__init__(parent)
        self.title = parent.windowTitle()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(*margins)
        self.create_widgets()
                    
    def create_widgets(self):
        
        self.ribbon = Ribbon(self)
        self.images = ImageView(self)
        self.thread = Worker(self)
         
        self.layout.addWidget(self.ribbon)
        self.layout.addWidget(self.images)
        self.thread.finished.connect(
            self.images.table.layoutChanged.emit
            )

    def populate(self, event=None, op='[<>=!]=?'):
        
        self.query = {}
        join = ''
        order = self.get_order()
        self.images.clearSelection()
        string = self.ribbon.tags.text()
        if string: self.ribbon.update(string)
        
        if self.title == 'Gesture Draw':
            
            self.query['gesture'] = ['date_used <= Now() - INTERVAL 2 MONTH']

        # query parsing
        for token in re.findall(f'\w+{op}[\w\*\.]+', string):
            
            string = string.replace(token, '')
            col, val = re.split(op, token)

            if col == 'comic':
                
                token = f'parent="{val}"'
                order = self.get_order(1)
                join = 'JOIN comic ON comic.path_=imageData.path'
            
            elif col == 'order':

                order = f'ORDER BY {val}'

            elif re.search('\*', val):
                
                token = f'{col} LIKE "{val.replace("*", "%")}"'

            elif val == 'NULL':
                
                neg = 'NOT ' if '!' in token else ''
                token = f'{neg}IS{val}({col})'

            elif re.search('\D', val):

                token = re.sub(f'(\w+{op})(\w+)', r'\1"\2"', token)

            self.query[col] = self.query.get(col, []) + [token]
        
        # tag parsing
        if string.strip():
    
            string = re.sub('(-?\w+( OR -?\w+)+)', r'(\1)', string)
            string = re.sub('NOT ', '-', string.strip())
            string = re.sub('([*]?\w+|\([^()]*\))', r'+\1', string)
            string = re.sub('(\+AND|OR) ', '', string)
            string = re.sub('-\+', '-', string)
            if not re.search('\+(\w+|\*|\()', string): string += ' qwd'

            self.query['tags'] = [
                f'MATCH(tags, artist) AGAINST("{string}" IN BOOLEAN MODE)'
                ]
        
        for text, col in zip(['type', 'rating'], [self.type, self.rating]):
            if (val:=ENUM[col.checkedAction().text()]) and text not in self.query:
                self.query[text] = [val]
        
         # comic functionality
        
        if 'comic' in self.query.get('type', [''])[0] and '3' not in self.query:
            join = 'JOIN comic ON comic.path_=imageData.path'
            self.query['pages'] = ['page=0']

        if not any(self.query): self.query[''] = ['NOT ISNULL(path)']

        filter = " AND ".join(
            f'({" OR ".join(val)})' for val in self.query.values() if val
            )
        
        self.statement = f'{BASE} {join} WHERE {filter} {order}'
        
        self.thread.statement = self.statement
        self.thread.start()
        
    def get_order(self, type_=0, ORDER={'Ascending':'ASC','Descending':'DESC'}):
        
        order = self.order[1].checkedAction().text()
        column = self.order[0].checkedAction().text()
        if type_: column = 'page'
        
        if column:
            column = 'RAND()' if column == 'Random' else column
            return f'ORDER BY {column} {ORDER[order]}'

        return ''
            
    def statusbar(self, total=0, select=0):
         
        total = f'{total} image' if (total == 1) else f'{total} images'
        if select:
            select = (
                f'{select} image selected' 
                if (select == 1) else 
                f'{select} images selected'
                )
        else: select = ''
        
        self.parent().parent().statusbar.showMessage(f'   {total}     {select}')
    
    def keyPressEvent(self, event):
    
        key_press = event.key()
        modifiers = event.modifiers()
        alt = modifiers == Qt.AltModifier

        if alt:
            
            if key_press == Qt.Key_Left: self.ribbon.go_back()
                
            elif key_press == Qt.Key_Right: self.ribbon.go_forward()
            
            else: self.parent().keyPressEvent(event)

        elif key_press == Qt.Key_F4: self.ribbon.tags.setFocus()
        
        elif key_press == Qt.Key_F5: self.populate()

        else: self.parent().keyPressEvent(event)

    def resizeEvent(self, event):

        table = self.images.table
        table.width = event.size().width() // table.size
    
class Ribbon(QWidget):
     
    def __init__(self, parent):
         
        super(Ribbon, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
        
    def configure_gui(self):
         
        self.undo = ['']
        self.redo = []
        self.layout = QHBoxLayout(self)

    def create_widgets(self):
        
        # History navigation
        self.history = QHBoxLayout()
        self.layout.addLayout(self.history)

        self.back = QPushButton()
        self.forward = QPushButton()
        self.menu = QPushButton()
        
        for button, event, icon in zip(
            [self.back, self.forward, self.menu],
            [self.go_back, self.go_forward, self.menu.showMenu],
            [QStyle.SP_ArrowBack, QStyle.SP_ArrowForward, QStyle.SP_ArrowDown]
            ):
            
            button.setIcon(self.style().standardIcon(icon))
            button.clicked.connect(event)
            button.setEnabled(False)
            self.history.addWidget(button)

        # Search function
        self.select = QFormLayout()
        self.layout.addLayout(self.select, 0)
        
        self.tags = QLineEdit(self)
        self.tags.setFixedWidth(250)
        self.tags.setPlaceholderText('Enter tags')
        self.tags.setCompleter(
            QCompleter(open(AUTOCOMPLETE).read().split())
            )
        self.select.addRow('Search:', self.tags)
        
        self.timer = QTimer(self.tags)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.parent().populate)
        self.tags.textChanged.connect(lambda: self.timer.start(1000))
        
        if self.parent().title == 'Manage Data':
            self.tags.returnPressed.connect(self.parent().populate)
            
        else:
            self.time = QLineEdit(self)
            self.time.setFixedWidth(250)
            self.tags.returnPressed.connect(
                self.parent().parent().start_session
                )
            self.time.returnPressed.connect(
                self.parent().parent().start_session
                )
            self.select.addRow('Time:', self.time)
    
        self.refresh = QPushButton(self)
        self.refresh.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.refresh.clicked.connect(self.parent().populate)
        self.layout.addWidget(self.refresh, 1, Qt.AlignLeft)
        
        self.multi = QCheckBox('Multi-selection', self)
        self.multi.clicked.connect(self.changeSelectionMode)
        self.layout.addWidget(self.multi, 1, Qt.AlignLeft)

        self.tags.setFocus()
        
    def update(self, string='', check=1):

        if string:

            if self.undo:
                if string != self.undo[-1]:
                    self.undo.append(string)
                    self.redo.clear()
            else:
                self.undo.append(string)
                self.redo.clear()

        self.back.setEnabled(bool(self.undo[1:]))
        self.forward.setEnabled(bool(self.redo))
        self.menu.setEnabled(bool(self.undo + self.redo))

        menu = QMenu(self, triggered=self.menuEvent)
        for state in reversed(self.undo[1:] + self.redo[::-1]):
            
            action = QAction(state, menu, checkable=True)
            if state == string and check: 
                action.setChecked(True)
                check=0
            menu.addAction(action)

        else: self.menu.setMenu(menu)
        
        self.tags.setText(self.undo[-1])
    
    def go_back(self, event=None, update=True):
        
        if len(self.undo) > 1:
            self.redo.append(self.undo.pop())
            if update: self.update()

    def go_forward(self, event=None, update=True):
        
        if self.redo:
            self.undo.append(self.redo.pop())
            if update: self.update()
    
    def changeSelectionMode(self, event):
        
        if event:
            self.parent().images.setSelectionMode(
                QAbstractItemView.MultiSelection
                )
        else:
            self.parent().images.setSelectionMode(
                QAbstractItemView.ExtendedSelection
                )
            self.parent().images.clearSelection()
    
    def menuEvent(self, event):

        action = event.text()

        if action in self.undo:

            while action != self.undo[-1]: self.go_back(update=False)

        elif action in self.redo:

            while action in self.redo: self.go_forward(update=False)
        
        self.update()

    def keyPressEvent(self, event):
    
        key_press = event.key()

        if key_press in (Qt.Key_Return, Qt.Key_Enter): pass

        else: self.parent().keyPressEvent(event)