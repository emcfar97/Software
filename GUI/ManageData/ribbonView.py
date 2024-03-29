import re
from PyQt6.QtGui import QAction, QUndoStack
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QCheckBox, QStyle, QMenu, QCompleter

from GUI.utils import BASE, AUTOCOMPLETE, LIMIT

ENUM = {
    'All': '',
    'Photo': "type='photograph'",
    'Illus': "type='illustration'",
    'Comic': "type='comic'",
    'Explicit': '',
    'Questionable': 'rating<3',
    'Safe': 'rating=1',
    }

class Ribbon(QWidget):
     
    selection_mode = pyqtSignal(bool)

    def __init__(self, parent):
         
        super(Ribbon, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
        
    def configure_gui(self):
        
        self.query = ''
        self.undo = ['']
        self.redo = []
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 5, 0)

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
        self.tags.setCompleter(
            QCompleter(open(AUTOCOMPLETE).read().split())
            )
        self.tags.returnPressed.connect(self.parent().select_records)
                
        self.timer = QTimer(self.tags)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.parent().select_records)
        self.tags.textChanged.connect(lambda: self.timer.start(1000))
        
        self.refresh = QPushButton(self)
        pixmap = getattr(QStyle.StandardPixmap, 'SP_BrowserReload')
        self.refresh.setIcon(self.style().standardIcon(pixmap))
        self.refresh.clicked.connect(self.parent().select_records)
                
        self.multi = QCheckBox('Multi-selection', self)
        self.multi.clicked.connect(self.selection_mode.emit)
        
        self.layout.addWidget(self.tags)
        self.layout.addWidget(self.refresh)
        self.layout.addWidget(self.multi)
        
    def update_query(self, event=None, op='[<>=!]=?'):
        
        query = {}
        join = ''
        order = self.get_order()
        string = self.tags.text()
        if string: self.update_history(string)
        if event: query['gesture'] = ['date_used <= Now() - INTERVAL 2 MONTH']
        enums = self.parent().parent().gallery.enums
        
        # query parsing
        for token in re.findall(f'\w+{op}[\w\*\.]+', string):
            
            string = string.replace(token, '')
            col, val = re.split(op, token)

            if col == 'comic':
                
                token = f"comic.parent='{val}'"
                join = 'JOIN comic ON comic.path=imagedata.path'
            
            elif col == 'order':

                order = f'ORDER BY {val}'
                continue

            elif re.search('\*', val):
                
                token = f'{col} LIKE "{val.replace("*", "%")}"'

            elif val == 'NULL':
                
                neg = 'NOT ' if '!' in token else ''
                token = f'{neg}IS{val}({col})'

            elif re.search('\D', val):

                token = re.sub(f'(\w+{op})(\w+)', r'\1"\2"', token)

            query[col] = query.get(col, []) + [token]
        
        # menu parsing
        for text, col in zip(['type', 'rating'], [enums['type'], enums['rating']]):

            if (val:=ENUM[col.checkedAction().text()]) and text not in query:
                query[text] = [val]
            if text == 'type' and 'comic' not in query and 'comic' in query.get(text, [''])[0]:

                join = 'JOIN comic ON comic.path=imagedata.path'
                query['comic'] = ['comic.parent=imagedata.path']

        # tag parsing
        if string.strip():
            
            query['tags'] = [
                f'MATCH(tags, artist) AGAINST("{self.tag_parser(string)}" IN BOOLEAN MODE)'
                ]
        
        # remove null paths
        if not any(query) or 'type' in query:
            
            query[''] = ['NOT ISNULL(imagedata.path)']

        filter = " AND ".join(
            f'({" OR ".join(val)})' for val in query.values() if val
            )
        
        self.query = f'{BASE} {join} WHERE {filter} {order} LIMIT {LIMIT}'

        return self.query
    
    def tag_parser(self, string):
    
        # string = re.sub('([-*]?\w+( OR [-*]?\w+)+)', r'(\1)', string)

        string = re.sub('([-*]?\w+( OR [-*]?\w+)+\*)', r'(\1)', string)
        string = re.sub('NOT ', '-', string.strip())
        string = re.sub('([*]?\w+|\([^()]*\))', r'+\1', string)
        string = re.sub('(\+AND|OR) ', '', string)
        string = re.sub('-\+', '-', string)
        if not re.search('\+(\w+|\*|\()', string): string += ' qwd'
        
        string = string.replace('++', '+')

        return string
    
    def get_order(self, ORDER={'Ascending':'ASC','Descending':'DESC'}):
        
        enums = self.parent().parent().gallery.enums
        column = enums['order'][0].checkedAction().text()
        
        if column:
            
            column = 'RAND()' if column == 'Random' else column
            column = 'date_used' if column == 'Date' else column
            order = enums['order'][1].checkedAction().text()
            
            return f'ORDER BY {column} {ORDER[order]}'

        return ''
            
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