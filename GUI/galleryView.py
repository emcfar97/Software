import re
from . import *
from .imageView import *
from PyQt5.QtWidgets import QButtonGroup
    
RATING = {
    'Explicit': '',
    'Questionable': 'rating!="explicit"',
    'Safe': 'rating="safe"'
    }
TYPE = {
    'All': '',
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
        
        try:
            type_, = re.findall('type=(?:photo.+|illus.+\b?)', string)
            string = string.replace(type_, '')
            type_ = TYPE[re.findall('photo|illus', type_)[0].capitalize()] 
        except ValueError: type_ = self.ribbon.get_type()

        try:
            rating, = re.findall('rating=(?:safe|questionable|explicit?)', string)
            string = string.replace(rating, '')
            rating = re.sub('(\w+)\Z', r'"\1"', rating)
        except ValueError: rating = self.ribbon.get_rating()

        try:
            stars, = re.findall('stars[<>=!]+[0-5]', string)
            string = string.replace(stars, '')
            stars = stars.replace('==', '=')
        except ValueError: stars = ''

        query = [
            'NOT (ISNULL(path) OR path LIKE "_0_%")',
            type_, rating, stars, self.ribbon.get_tags(string)
            ]

        if self.type == 'Manage Data': 

            return f'{" AND ".join(i for i in query if i)} {self.ribbon.get_order()}'

        else:
            query[0] = 'path LIKE "%.jp%g"'
            query.append('date_used <= Now() - INTERVAL 2 MONTH')

            return f'{" AND ".join(i for i in query if i)} ORDER BY RAND()'

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
        self.select.addRow('Search:', self.tags)
        
        if parent.type == 'Manage Data':
            self.tags.returnPressed.connect(parent.populate)
            
        else:
            self.time = QLineEdit(self)
            self.tags.returnPressed.connect(parent.parent().start_session)
            self.time.returnPressed.connect(parent.parent().start_session)
            self.select.insertRow(1, 'Time:', self.time)
           
    def get_tags(self, string, query='', ops={'AND':None, 'OR':1, 'NOT':0}):
        
        string = string.split()[::-1]

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
            
        return ''

    def get_rating(self):

        return RATING[self.rating.checkedAction().text()]

    def get_type(self):

        return TYPE[self.type.checkedAction().text()]
    
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
