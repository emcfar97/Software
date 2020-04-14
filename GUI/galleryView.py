import re
from . import *
from .imageView import *
from PyQt5.QtWidgets import QButtonGroup
    
RATING = {
    'Explicit': None,
    'Questionable': 'rating!="explicit"',
    'Safe': 'rating="safe"'
    }
TYPE = {
    'All': None,
    'Photo': 'NOT type',
    'Illus': 'type',
    }
ORDER = {
    'Ascending': 'ASC',
    'Descending': 'DESC'
    }

class Gallery(QWidget):
     
    def __init__(self, parent, type_):
         
        super().__init__(parent)
        self.type = type_
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
               
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)
        size = self.parent().size()
        
        if self.type == 'Manage Data':
            self.setGeometry(
                0, 0, 
                int(size.width() // 2), size.height()
                )
            self.layout.setContentsMargins(6, 6, 9, 30)
                    
        elif self.type == 'Gesture Draw':
            self.setGeometry(
                0, 0, 
                size.width(), size.height()
                )
            self.layout.setContentsMargins(6, 6, 9, 9)
                    
    def create_widgets(self):
        
        self.ribbon = Ribbon(self)
        self.images = imageView(self)
        self.status = StatusBar(self)
         
        self.layout.addWidget(self.ribbon)
        self.layout.addWidget(self.images)
        self.layout.addWidget(self.status)
    
    def populate(self, sender=None, limit=3500):
         
        if self.type == 'Manage Data': self.parent().preview.show_image(None)
        SELECT = f'{BASE} {self.get_filter()} LIMIT {limit}'
        
        images = self.images
        images.clearSelection()
        images.table.rowsLoaded = 0
        try: 
            CURSOR.execute(SELECT)
            selection = CURSOR.fetchall()
        except: selection = []

        images.table.images = selection
        images.table.rows = (images.total() // 5) + bool(images.total() % 5)
        images.table.layoutChanged.emit()
        images.resizeRowsToContents()
        images.resizeColumnsToContents()
        self.status.modify(images.total())
        
    # def populate(self, sender=None, images=5000):
        
        # table = self.images.table
            
        # if self.type == 'Manage Data': self.parent().preview.show_image(None)
        # self.images.table.setFilter(self.get_filter())
            
        # print(table.select(), table.lastError())
        # while table.canFetchMore(): table.fetchMore()
        # table.layoutChanged.emit()
        # self.images.resizeRowsToContents()
        # self.images.resizeColumnsToContents()

    def get_filter(self):

        string = self.ribbon.tags.text()
        type_ = re.findall('type=(photo.+|illus.+)?\s', string)
        rating = re.findall('rating=(safe|questionable|explicit)?', string)
        stars = re.findall('stars[<>=!]+[0-5]', string)

        values = [
            'NOT (ISNULL(path) OR path LIKE "_0_%")',
            self.ribbon.get_type(),
            self.ribbon.get_rating(),
            self.ribbon.get_star(),
            self.ribbon.get_tags()
            ]

        if self.type == 'Manage Data': 

            query = ' AND '.join([i for i in values if i])
            return query + self.ribbon.get_order()

        else:
            values[0] = 'path LIKE "%.jp%g"'
            values.append('date_used <= Now() - INTERVAL 2 MONTH')

            query = ' AND '.join([i for i in values if i])
            return query + ' ORDER BY RAND()'

class Ribbon(QWidget):
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
        
    def configure_gui(self):
         
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
         
    def create_widgets(self):
        
        parent = self.parent()
        self.select = QFormLayout()
        self.select.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.layout.addLayout(self.select)
        
        self.tags = QLineEdit(self)
        self.tags.textEdited.connect(parent.populate)
        self.stars = Widget(
            'combo-entry', signal=parent.populate,
            values=['', '>', '>=', '==', '<=', '<']
            )

        self.select.addRow('Search:', self.tags)
        self.select.addRow('Stars:', self.stars)
        
        if parent.type == 'Manage Data':
            self.tags.returnPressed.connect(parent.populate)
            
        else:
            self.tags.returnPressed.connect(parent.parent().start_session)
            
            self.time = QLineEdit(self)
            self.time.returnPressed.connect(parent.parent().start_session)
            self.select.insertRow(1, 'Time:', self.time)
           
    def get_tags(self, query='', ops={'AND':None, 'OR':1, 'NOT':0}):
        
        string = self.tags.text().split()[::-1]

        if string and string != ['-']:

            while string:
                token = string.pop()

                if token in ops:
                    try:
                        if ops[token] is None: query += f"+{string.pop()} "
                        else:
                            if ops[token]: query += "{string.pop()} "
                            else: query += f"-{string.pop()} "
                    except IndexError: continue
                else: 
                    if token == '-': pass
                    elif token.startswith('-'): query += f"{token} "
                    else: query += f"+{token} "

            if query:
                return f'MATCH(tags, artist) AGAINST("qwd {query}" IN BOOLEAN MODE)'

    def get_star(self):
        
        op, val = self.stars.get()
        if op and val: return f'stars{"=" if op == "==" else op}{val}'
    
    def get_rating(self):

        rating = self.rating.checkedAction()
        return RATING[rating.text()]

    def get_type(self):

        type = self.type.checkedAction()
        return TYPE[type.text()]
    
    def get_order(self):
        
        order = self.order
        column = order[0].checkedAction().text()
        order = order[1].checkedAction().text()
        
        if column: 
            column = 'RAND()' if column == 'Random' else column
            return f' ORDER BY {column} {ORDER[order]}'
        return ' ORDER BY rowid'
       
class StatusBar(QLabel):
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
 
    def configure_gui(self):
               
        self.setIndent(5)
        size = self.parent().size()
        self.setAlignment(Qt.AlignVCenter)
        self.setFixedHeight(int(size.height() * .02))
        self.setStyleSheet('background: #f0f0ff; font: 8pt')
        
    def modify(self, total=0, select=0):
         
        total = f'{total} image' if (total == 1) else f'{total} images'
        if select:
            select = f'{select} image selected' if (select == 1) else f'{select} images selected'
        else: select = ''
         
        self.setText(f'{total}     {select}')

class Widget(QWidget):
    
    def __init__(self, type_, **kwargs):
        
        super().__init__()
        self.type = type_
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        if self.type == 'entry':

            self.left = QLineEdit()
            if 'signal' in kwargs:
                if kwargs['connect'] == 'return':
                    self.left.returnPressed.connect(kwargs['signal'])
                elif kwargs['connect'] == 'edit':
                    self.left.textEdited.connect(kwargs['signal'])
            
        elif self.type == 'combo':

            self.left = QComboBox()
            # self.left.setStyleSheet('background: white')
            if 'values' in kwargs:
                self.left.addItems(kwargs['values'])
        
        elif self.type == 'combo-entry':

            self.left = QComboBox()
            self.right = QLineEdit()
            
            # self.left.setStyleSheet('background: white')
            if 'values' in kwargs:
                self.left.addItems(kwargs['values'])
            
            if 'signal' in kwargs:
                self.right.returnPressed.connect(kwargs['signal'])
                
        elif self.type == 'combo-combo':

            self.left = QComboBox()
            self.right = QComboBox()
            
            self.left.addItems(kwargs['values'][0])
            self.right.addItems(kwargs['values'][1])
            
            # self.left.setStyleSheet('background: white')
            # self.right.setStyleSheet('background: white')
            
        self.layout.addWidget(self.left)
        if '-' in self.type: self.layout.addWidget(self.right)
         
    def modify(self, **kwargs):
        
        for key, val in kwargs.items():
            
            if key == 'title':
                self.label.setText(val)
            elif key == 'values':
                self.right.addItems(val)
            elif key == 'signal':
                if kwargs['connect'] == 'return':
                    self.left.returnPressed.connect(val)
                elif kwargs['connect'] == 'edit':
                    self.left.textEdited.connect(val)
            
    def get(self):
        
        if self.type == 'entry': 
            return self.left.text()
        elif self.type == 'combo': 
            return self.left.currentText()
        elif self.type == 'combo-entry': 
            return self.left.currentText(), self.right.text()
        elif self.type == 'combo-combo': 
            return self.left.currentText(), self.right.currentText() 
    
    def clear(self):
        
        if self.type == 'entry': 
            self.left.clear()
        elif self.type == 'combo': 
            self.left.itemText(0)
        elif self.type == 'combo-entry': 
            self.left.itemText(0), self.right.clear()
        elif self.type == 'combo-combo': 
            self.left.itemText(0), self.right.itemText(0) 
