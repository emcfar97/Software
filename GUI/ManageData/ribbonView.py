import re
from PyQt6.QtGui import QAction, QUndoStack
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QCheckBox, QStyle, QMenu, QUndoView

from GUI.utils import SELECT, AUTOCOMPLETE, LIMIT, ENUM, Completer

class Ribbon(QWidget):
     
    selection_mode = pyqtSignal(bool)
    query_updated = pyqtSignal(object)

    def __init__(self, parent, test=False):
         
        super(Ribbon, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
        
        if not test:
            
            self.tags.returnPressed.connect(self.update_query)
            self.timer.timeout.connect(self.update_query)
            self.refresh.clicked.connect(self.update_query)
        
    def configure_gui(self):
        
        self.order = {
            'sort': 'ORDER BY rowid ASC',
            'column': {
                'rating': 'General',
                'type': 'All',
                }
            }
        self.undo = ['']
        self.redo = []
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 5, 0)

    def create_widgets(self):
        
        # History navigation
        self.history = QHBoxLayout()
        self.layout.addLayout(self.history)
        self.undoStack = QUndoStack(self)

        self.back = QPushButton()
        self.forward = QPushButton()
        self.menu = QPushButton()
        
        for button, event, icon in zip(
            [self.back, self.forward, self.menu],
            [self.go_back, self.go_forward, self.menu.showMenu],
            ['SP_ArrowBack', 'SP_ArrowForward', 'SP_ArrowDown']
            ):
            
            button.clicked.connect(event)
            button.setEnabled(False)
            pixmap = getattr(QStyle.StandardPixmap, icon)
            button.setIcon(self.style().standardIcon(pixmap))
            self.history.addWidget(button)

        # Search function
        self.tags = QLineEdit(self)
        self.tags.setPlaceholderText('Enter tags')
        with open(AUTOCOMPLETE, encoding='utf8') as file:
            self.tags.setCompleter(Completer(file.read().split()))
                
        self.timer = QTimer(self.tags)
        self.timer.setSingleShot(True)
        self.tags.textChanged.connect(lambda: self.timer.start(1000))
        
        self.refresh = QPushButton(self)
        pixmap = getattr(QStyle.StandardPixmap, 'SP_BrowserReload')
        self.refresh.setIcon(self.style().standardIcon(pixmap))
                
        self.multi = QCheckBox('Multi-selection', self)
        self.multi.clicked.connect(self.selection_mode.emit)
        
        self.layout.addWidget(self.tags)
        self.layout.addWidget(self.refresh)
        self.layout.addWidget(self.multi)
        self.tags.setFocus()
        
    def update_query(self, gesture=False, limit=LIMIT, op='[<>=!]=?'):
        
        query = {}
        join = ''
        where = ''
        having = ''
        string = self.tags.text()
        if string: self.update_history(string)
        if gesture: query['gesture'] = ['date_used <= Now() - INTERVAL 2 MONTH']
        order = self.order['sort']
        
        # query parsing
        for token in re.findall(f'\w+{op}[\w\*\.\-\(\)/]+', string):
            
            string = string.replace(token, '')
            col, val = re.split(op, token)

            if col == 'comic':
                
                token = f"comic.parent='{val}'"
                join = 'JOIN comic ON comic.path=imagedata.path'
            
            elif col == 'order':

                order = f'ORDER BY {val}'
                continue
            
            elif col == 'limit':
                
                limit = val
                
            elif col in ('date', 'date_used'):
                
                operator = token.replace(col, '').replace(val, '')
                token = f'date_used{operator}"{val}"'
             
            elif re.search('\*', val):
                
                token = f'{col} LIKE "{val.replace("*", "%")}"'
            
            elif val == 'NULL':
                
                neg = 'NOT ' if '!' in token else ''
                token = f'{neg}IS{val}({col})'

            elif re.search('\D', val):

                token = re.sub(f'(\w+{op})([/\w]+)', r'\1"\2"', token)
            
            query[col] = query.get(col, []) + [token]
        
        # menu parsing
        for col, val in self.order['column'].items():
            
            if col not in query and val in ENUM: 
                
                if ENUM[val]: query[col] = [ENUM[val]]
            
            if col == 'type' and 'comic' not in query and 'comic' in query.get(col, [''])[0]:

                join = 'JOIN comic ON comic.path=imagedata.path'
                query['comic'] = ['comic.parent=imagedata.path']

        # tag parsing
        if string.strip():
            
            query['tags'] = [
                f'MATCH(tags, artist) AGAINST("{self.tag_parser(string)}" IN BOOLEAN MODE)'
                ]
        
        if query:
            where = 'WHERE ' + ' AND '.join(
                f'({" OR ".join(val)})' for val in query.values() if val
                )
        
        query = f'{SELECT} {join} {where} {having} {order} LIMIT {limit}'

        self.query_updated.emit(query)
    
    def tag_parser(self, string):
    
        # string = re.sub('([-*]?\w+( OR [-*]?\w+)+)', r'(\1)', string)

        string = re.sub('([-*]?\w+( OR [-*]?\w+)+\*)', r'(\1)', string)
        # replace NOT with '-' char
        string = re.sub('NOT ', '-', string.strip())
        # add '+' char
        string = re.sub('([*]?\w+|\([^()]*\))', r'+\1', string)
        string = re.sub('(\+AND|OR) ', '', string)
        string = re.sub('-\+', '-', string)
        if not re.search('\+[\w+\*\(]', string): string += ' qwd'
        
        string = string.replace('++', '+')
        string = string.replace('_+(', '_(')

        return string
    
    def update_order(self, data):  self.order = data
            
    def update_history(self, string='', check=1):

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
            if update: self.update_history()

    def go_forward(self, event=None, update=True):
        
        if self.redo:
            
            self.undo.append(self.redo.pop())
            if update: self.update_history()
    
    def text(self): return self.tags.text()
    
    def setText(self, text): self.tags.setText(text)

    def menuEvent(self, event):

        action = event.text()

        match event.text():
                
            case self.undo:

                while action != self.undo[-1]: 
                    
                    self.go_back(update=False)

            case self.redo:

                while action in self.redo: 
                    
                    self.go_forward(update=False)
            
        self.update_history()

    def keyPressEvent(self, event):
    
        match event.key():
            
            case (Qt.Key.Key_Return|Qt.Key.Key_Enter): pass

            case _: self.parent().parent().keyPressEvent(event)