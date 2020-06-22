import re, textwrap, queue, qimage2ndarray
from . import *
from .propertiesView import *
from PyQt5.QtCore import QAbstractTableModel, QVariant, QModelIndex, QItemSelectionModel, QItemSelection, Qt
from PyQt5.QtWidgets import QApplication, QAbstractScrollArea, QAbstractItemView, QMenu, QAction, QActionGroup, QShortcut, QPushButton, QStyle
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

RATING = {
    'Safe': 'rating=0', 'Questionable': 'rating<=1', 'Explicit': '',
    'safe': '0', 'questionable': '1', 'explicit': '2',
    0: 'safe', 1: 'questionable', 2: 'explicit'
    }
TYPE = {
    'all': [''],
    'photo': ['type=0', '0'], 
    'illus': ['type=1', '1'], 
    'comics': ['type=2', '2'],
    0: 'photograph', 1: 'illustration', 2: 'comic'
    }

class Gallery(QWidget):
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
        self.populate()
     
    def configure_gui(self):
               
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)
        size = self.parent().size()
        
        if self.parent().windowTitle() == 'Manage Data':
            self.setGeometry(
                0, 0, 
                int(size.width() // 2), size.height()
                )
            self.layout.setContentsMargins(6, 6, 9, 30)
                    
        elif self.parent().windowTitle() == 'Gesture Draw':
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
    
    def populate(self, sender=None, limit=5000, id=0):
         
        images = self.images
        images.clearSelection()
        images.table.rowsLoaded = 0

        try: 
            if id: SELECT = f'{COMIC} WHERE hash="{id}"'
            else: SELECT = f'{BASE} {self.get_filter()} LIMIT {limit}'
            CURSOR.execute(SELECT)
            images.table.images = CURSOR.fetchall()
        except: images.table.images = []

        images.table.layoutChanged.emit()
        images.resizeRowsToContents()
        images.resizeColumnsToContents()
        self.status.modify(images.total())
        
        if self.type == 'Manage Data': 
            
            self.parent().preview.show_image(None)
        
    # def populate(self, sender=None, limit=3500):
        
        # if self.type == 'Manage Data': self.parent().preview.show_image(None)
        # SELECT = f'{BASE} {self.get_filter()} LIMIT {limit}'
        # table = self.images.table
            
        # images = self.images
        # images.clearSelection()
        # images.table.rowsLoaded = 0
        # try: 
        #     CURSOR.execute(SELECT)
        #     selection = CURSOR.fetchall()
        # except: selection = []
            
        # images.table.images = selection
        # images.table.layoutChanged.emit()
        # images.resizeRowsToContents()
        # images.resizeColumnsToContents()
        # self.status.modify(images.total())

    def get_filter(self):
        
        query = ['path LIKE "C:%"']
        if self.parent().windowTitle() == 'Gesture Draw':

            query.append('date_used <= Now() - INTERVAL 2 MONTH')

        string = self.ribbon.tags.text()
        if string: self.ribbon.update(string)

        try: # Get type
            type_, = re.findall('type=(?:photo|illus|comics?)', string)
            string = string.replace(type_, '')
            type_ = re.sub('(\w+)\Z', TYPE[type_[5:]][1], type_)
        except: type_ = TYPE[self.type.checkedAction().text().lower()][0]
        finally: query.append(type_)

        try: # Get stars
            stars, = re.findall('stars[<>=!]+[0-5]', string)
            string = string.replace(stars, '')
            stars = stars.replace('==', '=')
        except ValueError: stars = ''
        finally: query.append(stars.lower())

        try: # Get rating
            rating, = re.findall(
                'rating[<>=!]+(?:safe|questionable|explicit?)', string
                )
            string = string.replace(rating, '')
            rating = re.sub(
                '(\w+)\Z', RATING[re.findall('(\w+)\Z', rating)], rating
                )
        except: rating = RATING[self.rating.checkedAction().text()]
        finally: query.append(rating.lower())
        
        try: # Get artist
            artist, = re.findall('artist:\w+', string)
            string = string.replace(artist, '')
            artist = artist.replace(':', '=')
        except: artist = ''
        query.append(artist.lower())
        
        try: # Get path
            path, =  re.findall('path:.+jpe*g|gif|webm|mp4', string)
            string = string.replace(path, '')
            path = path.replace('path:', 'path LIKE "%') + '"'
            path = re.sub('.:', 'C:', path)
        except: path = ''
        finally: query.append(path)

        query.append(self.get_tags(string.strip()))

        return f'WHERE {" AND ".join(i for i in query if i)} {self.get_order()}'
        
        return f'WHERE GROUP BY hash HAVING COUNT(hash) > 1 ORDER BY hash'

    def get_tags(self, string):
        
        if string:
            
            string = re.sub('NOT ', '-', string)
            string = re.sub('(\w+ OR \w+)', r'(\1)', string)
            string = re.sub('(\w+|\(.+\))', r'+\1', string)
            string = re.sub('(AND \+|OR )', '', string)
            string = re.sub('-\+', '-', string)
            if not re.search('\+\w+', string): string += ' qwd'

            return f'MATCH(tags, artist) AGAINST("{string}" IN BOOLEAN MODE)'

    def get_order(self, ORDER={'Ascending': 'ASC', 'Descending': 'DESC'}):
        
        order = self.order
        column = order[0].checkedAction().text()
        order = order[1].checkedAction().text()
        
        if column: 
            column = 'RAND()' if column == 'Random' else column
            return f' ORDER BY {column} {ORDER[order]}'

        return ''
    
class Ribbon(QWidget):
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
        
    def configure_gui(self):
         
        self.undo = []
        self.redo = []
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

    def create_widgets(self):
        
        parent = self.parent()

        # History navigation
        self.history = QHBoxLayout()
        self.layout.addLayout(self.history)

        self.back = QPushButton()
        self.forward = QPushButton()
        self.menu = QPushButton()

        self.back.setIcon(
            self.style().standardIcon(getattr(QStyle, 'SP_ArrowLeft'))
            )
        self.forward.setIcon(
            self.style().standardIcon(getattr(QStyle, 'SP_ArrowRight'))
            )
        self.menu.setIcon(
            self.style().standardIcon(getattr(QStyle, 'SP_ArrowDown'))
            )
        
        self.back.clicked.connect(self.go_back)
        self.forward.clicked.connect(self.go_forward)
        self.menu.clicked.connect(self.menu.showMenu)
        
        for button in [self.back, self.forward, self.menu]:
            button.setEnabled(False)
            # button.setAlignment(Qt.AlignTop)
            self.history.addWidget(button)

        # Search function
        self.select = QFormLayout()
        self.layout.addLayout(self.select)
        
        self.tags = QLineEdit(self)
        self.tags.setFixedWidth(250)
        self.timer = QTimer(self.tags)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(parent.populate)
        self.tags.textChanged.connect(
            lambda x: self.timer.start(660)
            )
        self.select.addRow('Search:', self.tags)
        
        if parent.parent().windowTitle() == 'Manage Data':
            self.tags.returnPressed.connect(parent.populate)
            
        else:
            self.time = QLineEdit(self)
            self.time.setFixedWidth(250)
            self.tags.returnPressed.connect(parent.parent().start_session)
            self.time.returnPressed.connect(parent.parent().start_session)
            self.select.addRow('Time:', self.time)
    
    def update(self, string=None):

        menu = QMenu(self)

        if string:
            if self.undo:
                if string != self.undo[-1]:
                    self.undo.append(string)
                    self.redo.clear()
            else:
                self.undo.append(string)
                self.redo.clear()

        self.back.setEnabled(bool(self.undo))
        self.forward.setEnabled(bool(self.redo))
        self.menu.setEnabled(bool(self.undo + self.redo))
        
        for num, i in enumerate(self.undo[::-1]):
            action = QAction(i, menu, checkable=True)
            if num == 0: action.setChecked(True)
            menu.addAction(action)
        for i in self.redo:
            action = QAction(i, menu, checkable=True)
            menu.addAction(action)
        
        self.menu.setMenu(menu)
        
        if not string:
            string = self.undo[-1]
            self.tags.setText(string)

    def go_back(self):
        
        if self.undo:
            self.redo.append(self.undo.pop())
            self.update()

    def go_forward(self):
        
        if self.redo:
            self.undo.append(self.redo.pop())
            self.update()

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

class imageView(QTableView):

    def __init__(self, parent):

        super().__init__(parent)
        self.menu = self.create_menu()
        # self.table = Test(self, parent.width())   
        self.table = Model(self, parent.width())   
        self.setModel(self.table)
        self.horizontalHeader().hide()      
        self.verticalHeader().hide()
        self.setGridStyle(0)

        self.doubleClicked.connect(self.open_slideshow)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuEvent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContentsOnFirstShow
            )
        self.setVerticalScrollMode(1)
        
    def selectionChanged(self, select, deselect):
        
        if not self.table.images: return
        parent = self.parent().parent()
        select, deselect = select.indexes(), deselect.indexes()
        
        if parent.windowTitle() == 'Manage Data':
            if not select:
                index = self.selectedIndexes()
                image = index[-1].data(Qt.UserRole) if index else None
            else: image = select[0].data(Qt.UserRole)
            parent.preview.show_image(image)
        
        self.parent().status.modify(
            self.total(), len(self.selectedIndexes())
            )

    def create_menu(self):
        
        menu = QMenu(self)
        parent = self.parent()

        sortMenu = QMenu('Sort by', menu)
        order = [QActionGroup(sortMenu), QActionGroup(sortMenu)]
        for i in ['Rowid', 'Path', 'Artist', 'Stars', 'Hash', 'Random']:
            action = QAction(i, sortMenu, checkable=True)
            if i == 'Rowid' and parent.parent().windowTitle() == 'Manage Data':
                action.setChecked(True)
            elif i=='Random' and parent.parent().windowTitle()=='Gesture Draw':
                action.setChecked(True)
            order[0].triggered.connect(parent.populate)
            order[0].addAction(action)
            sortMenu.addAction(action)
        else:
            sortMenu.addSeparator()
            for i in ['Ascending', 'Descending']:
                action = QAction(i, sortMenu, checkable=True)
                if i.startswith('Asc'): action.setChecked(True)
                order[1].triggered.connect(parent.populate)
                order[1].addAction(action)
                sortMenu.addAction(action)

            menu.addMenu(sortMenu)
            order[0].setExclusive(True); order[1].setExclusive(True)
            parent.order = order

        rateMenu = QMenu('Rating', menu)
        rating = QActionGroup(rateMenu)
        for i in ['Explicit', 'Questionable', 'Safe']:
            action = QAction(i, rateMenu, checkable=True)
            rating.triggered.connect(parent.populate)
            rating.addAction(action)
            rateMenu.addAction(action)
        else: 
            action.setChecked(True)
            menu.addMenu(rateMenu)
            rating.setExclusive(True)
            parent.rating = rating
        
        typeMenu = QMenu('Type', menu)
        type_ = QActionGroup(typeMenu)
        for i in ['All', 'Photo', 'Illus', 'Comics']:
            action = QAction(i, typeMenu, checkable=True)
            if i == 'All': action.setChecked(True)
            type_.triggered.connect(parent.populate)
            type_.addAction(action)
            typeMenu.addAction(action)
        else: 
            menu.addMenu(typeMenu)
            type_.setExclusive(True)
            parent.type = type_

        menu.addSeparator()
        menu.addAction(
            QAction('Copy', menu, triggered=self.copy_path)
            )
        try:
            menu.addAction(

                QAction('Delete', menu, triggered=parent.parent().delete_records)
                )
            menu.addSeparator()
            menu.addAction(
                QAction('Properties', menu, 
                triggered=lambda: Properties(parent, self.selectedIndexes()))
                )
        except AttributeError: pass

        return menu

    def contextMenuEvent(self, sender): self.menu.popup(sender)
    
    def total(self): return len(self.table.images)
    
    def copy_path(self):
    
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        
        paths = ' '.join(
            f'"{index.data(Qt.UserRole)}"' for index in self.selectedIndexes()
            )
        cb.setText(paths, mode=cb.Clipboard)

    def open_slideshow(self, index):
        
        # path, type_ = index.data(500)
        # if type_ == 2:
        #     id = path.split('\\')[-1][:-4]
        #     self.parent().populate(id=id)
        
        # else:
        parent = self.parent().parent()

        if parent.windowTitle() == 'Manage Data':
            
            parent.start_slideshow(
                self.table.images.copy(), 
                (index.row() * 5) + index.column()
                )

    def keyPressEvent(self, sender):
        
        key_press = sender.key()
        mode = QItemSelectionModel()
        selection = QItemSelection()
        modifier = sender.modifiers()
        ctrl = modifier == Qt.ControlModifier
        shift = modifier == Qt.ShiftModifier
        alt = modifier == Qt.AltModifier

        if key_press in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Right, Qt.Key_Left):
            
            index = self.currentIndex()
            row, col = index.row(), index.column()
            direction = 1 if key_press in (Qt.Key_Down, Qt.Key_Right) else -1

            if key_press in (Qt.Key_Right, Qt.Key_Left):

                if (col== 0 and direction== -1) or (col== 4 and direction== 1):
                    if not 0 <= (row + direction) < self.table.rowCount():return
                    row += direction
                col = (col + direction) % self.table.columnCount()
                new = self.table.index(row, col)

            elif key_press in (Qt.Key_Up, Qt.Key_Down):
                
                if not 0 <= (row + direction) < self.table.rowCount(): return
                row += direction 
                new = self.table.index(row, col)
            
            if shift:
                return
                selection.select(
                    index, new 
                    if index.data(250) > new.data(250) else 
                    new, index
                    )
                self.selectionModel().select(selection, mode.Toggle)

            else: self.setCurrentIndex(new)
                    
        elif key_press in (Qt.Key_PageUp, Qt.Key_PageDown):
            
            index = self.currentIndex()
            row, col = index.row(), index.column()
            sign = 1 if key_press == Qt.Key_PageDown else -1
            
            if not 0 <= (row + sign) < self.table.rowCount(): return
            row += sign * 5
            new = self.table.index(row, col)

            if shift:
                return
                selection.select(
                    index, new 
                    if index.data(250) > new.data(250) else 
                    new, index
                    )
                self.selectionModel().select(selection, mode.Toggle)

            else: self.setCurrentIndex(new)

        elif key_press in (Qt.Key_Home, Qt.Key_End):
            
            row, col = (
                (0, 0) if key_press == Qt.Key_Home else 
                (self.table.rowCount() - 1, (self.total() - 1) % self.table.columnCount())
                )
            new = self.table.index(row, col)

            if shift:
                return
                index = self.currentIndex()
                selection.select(
                    index, new 
                    if index.data(250) > new.data(250) else 
                    new, index
                    )
                self.selectionModel().select(selection, mode.Toggle)

            else: self.setCurrentIndex(new)

        elif key_press == Qt.Key_A and ctrl: self.selectAll()
                
        elif key_press == Qt.Key_C and ctrl: self.copy_path()
            
        elif key_press == Qt.Key_Return and alt:
            
            Properties(self.parent(), self.selectedIndexes())
        
        elif key_press == Qt.Key_Return:
            
            self.open_slideshow(self.currentIndex())       
        
        else: self.parent().parent().keyPressEvent(sender)

class Model(QAbstractTableModel):

    def __init__(self, parent, width):

        QAbstractTableModel.__init__(self, parent)
        self.wrapper = textwrap.TextWrapper(width=70)
        self.size = int(width * .1888)
        self.images = []
        self.rowsLoaded = 0

    def flags(self, index): return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def rowCount(self, parent=None): 

        rows, cols = divmod(len(self.images), self.columnCount())

        return rows + bool(cols)

    def columnCount(self, parent=None): return 5

    def data(self, index, role, type=0):
        
        ind = (index.row() * 5) + index.column()

        if not index.isValid() or ind >= len(self.images): return QVariant()
        try: 
        
            if role == Qt.SizeHintRole: return QSize(self.size, self.size)
            
            elif role == Qt.DecorationRole:
        
                path = self.images[ind][0]
                if path.endswith(('.mp4', '.webm')):
                    
                    image = VideoCapture(path).read()[-1]
                    image = qimage2ndarray.array2qimage(image).rgbSwapped()
                    
                else: image = QImage(path)

                image = image.scaled(
                    self.size, self.size, Qt.KeepAspectRatio, 
                    transformMode=Qt.SmoothTransformation
                    )
                
                return QPixmap.fromImage(image)

            elif role == Qt.ToolTipRole:
                
                tag, art, sta, rat, typ, = self.images[ind][1:]

                rat = RATING[rat].lower()
                typ = TYPE[typ]
                tags = self.wrapper.wrap(f'{tag}'.strip().replace('qwd', ''))
                rest = self.wrapper.wrap(
                    f'Artist: {art.strip()} Rating: {rat} Stars: {sta} Type: {typ}'
                    )
                return '\n'.join(tags + rest)

            elif role == Qt.UserRole: return QVariant(self.images[ind][0])
            
            elif role == 250: return ind
            
            elif role == 500: return self.images[ind][:6:5]

            elif role == 1000:
                
                data = self.images[ind]
                path = {data[0]} if data[0] else set()
                tags = set(data[1].split()) if data[1] else set()
                artist = set(data[2].split()) if data[2] else set()
                stars = {data[3]}
                rating = {data[4]}
                type = {data[5]}
                tags.discard('qwd')
                
                return path, tags, artist, stars, rating, type
            
        except (IndexError, ValueError): pass

        return QVariant()
   
    # def canFetchMore(self, index):

    #     return self.rowsLoaded < len(self.images)

    # def fetchMore(self, index, batch=100):

    #     remainder = self.rowsLoaded - len(self.images)
    #     itemsToFetch = min(batch, remainder)
    #     self.beginInsertRows(
    #         QModelIndex(), self.rowsLoaded,
    #         self.rowsLoaded + itemsToFetch - 1
    #         )
    #     self.rowsLoaded += itemsToFetch
    #     self.endInsertRows()

class Test(QSqlTableModel):

    def __init__(self, parent, width):

        QSqlTableModel.__init__(self, parent)
        self.database = open_database()
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.setTable('imageData')
        self.setQuery(
            QSqlQuery('SELECT path, tags, artist, rating, stars FROM imageData')
            )

        self.wrapper = textwrap.TextWrapper(width=70)
        self.size = int(width * .1888)
        self.images = []
        self.rowsLoaded = 0

    def open_database(self):
         
        datab = QSqlDatabase.addDatabase('QODBC')
        datab.setUserName('root')
        datab.setPassword('SchooL1@')
        datab.setDatabaseName('userData')
        datab.setHostName(
            '192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
            )
        datab.open()
        
        return datab

    def flags(self, index): return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def rowCount(self, parent): return self.rows

    def columnCount(self, parent): return 5

    def data(self, index, role, type=0):
        
        ind = (index.row() * 5) + index.column()

        if not index.isValid() or ind >= len(self.images): return QVariant()
        try: 
        
            if role == Qt.SizeHintRole: return QSize(self.size, self.size)
            
            elif role == Qt.DecorationRole:
        
                path = self.images[ind][0]
                if path.endswith(('.mp4', '.webm')):
                    
                    image = VideoCapture(path).read()[-1]
                    image = qimage2ndarray.array2qimage(image).rgbSwapped()
                    
                else: image = QImage(path)

                image = image.scaled(
                    self.size, self.size, Qt.KeepAspectRatio, 
                    transformMode=Qt.SmoothTransformation
                    )
                
                return self.create_label(QPixmap.fromImage(image))

            elif role == Qt.ToolTipRole:
                
                tag, art, sta, rat, typ, = self.images[ind][1:]
                typ = 'Illustration' if typ else 'Photograph'
                tags = self.wrapper.wrap(f'{tag}'.strip().replace('qwd', ''))
                rest = self.wrapper.wrap(
                    f'Artist:{art}Rating: {rat} Stars: {sta} {typ}'
                    )
                return '\n'.join(tags + rest)

            elif role == Qt.UserRole: return QVariant(self.images[ind][0])

            elif role == 1000: 
                
                data = self.images[ind]
                path = {data[0]} if data[0] else set()
                tags = set(data[1].split()) if data[1] else set()
                artist = set(data[2].split()) if data[2] else set()
                stars = {data[3]}
                rating = {data[4]}
                type = {data[5]}
                tags.discard('qwd')
                
                return path, tags, artist, stars, rating, type

        except (IndexError, ValueError): pass

        return QVariant()
   
    def create_label(self, image):

        label = QLabel()
        label.setFixedSize(self.size, self.size)
        label.setAlignment(Qt.AlignCenter)
        label.setPixmap(image)

        return label

    # def canFetchMore(self, index):

    #     return self.rowsLoaded < 1000

    # def fetchMore(self, index, batch=100):

    #     remainder = self.rowsLoaded - len(self.images)
    #     itemsToFetch = min(batch, remainder)
    #     self.beginInsertRows(
    #         QModelIndex(), self.rowsLoaded,
    #         self.rowsLoaded + itemsToFetch - 1
    #         )
    #     self.rowsLoaded += itemsToFetch
    #     self.endInsertRows()

class Test(QSqlTableModel):
    
    def __init__(self, *args, **kwargs):

        super(Test, self).__init__(*args, **kwargs)
        self.database = open_database()
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.setTable('imageData')
        self.setQuery(
            QSqlQuery('SELECT path, tags, artist, rating, stars FROM imageData')
            )
        self.select()

    def open_database(self):
         
        datab = QSqlDatabase.addDatabase('QODBC')
        datab.setUserName('root')
        datab.setPassword('SchooL1@')
        datab.setDatabaseName('userData')
        datab.setHostName(
            '192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
            )
        datab.open()
        
        return datab

    def data(self, index, role=Qt.DisplayRole):

        value = super(Test, self).data(index)
        if index.column() in self.booleanSet:
            if role == Qt.CheckStateRole:
                return Qt.Unchecked if value == 2 else Qt.Checked
            else:
                return QVariant()
        return QSqlTableModel.data(self, index, role)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() in self.booleanSet:
            return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        elif index.column() in self.readOnlySet:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        else:
            return QSqlTableModel.flags(self, index)