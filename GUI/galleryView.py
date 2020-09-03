import re, textwrap, qimage2ndarray
from . import *
from .propertiesView import Properties
from PyQt5.QtCore import QAbstractTableModel, QItemSelectionModel, QItemSelection, QThread, QVariant, QModelIndex, Qt, QSize, pyqtSignal
from PyQt5.QtWidgets import QAbstractScrollArea, QTableView, QAbstractItemView, QMenu, QAction, QActionGroup, QPushButton, QRadioButton, QStyle
# from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

RATING = {
    'Safe': 'rating=1', 
    'Questionable': 'rating<=2', 
    'Explicit': '',
    }
TYPE = {
    'all': '',
    'photo': 'type=1', 
    'illus': 'type=2', 
    'comic': 'type=3',
    }

class Gallery(QWidget):
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.title = parent.windowTitle()
        self.configure_gui()
        self.create_widgets()
     
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
            self.layout.setContentsMargins(6, 6, 6, 47)
                    
        elif self.parent().windowTitle() == 'Gesture Draw':

            self.setGeometry(
                0, 0, 
                size.width(), size.height()
                )
            self.layout.setContentsMargins(6, 6, 6, 9)
                    
    def create_widgets(self):
        
        self.properties = set()
        self.ribbon = Ribbon(self)
        self.images = ImageView(self)
         
        self.layout.addWidget(self.ribbon)
        self.layout.addWidget(self.images)
    
    def populate(self, sender=None, limit=7500):
        
        self.images.clearSelection()
        SELECT = f'{BASE} {self.get_filter()} LIMIT {limit}'
        self.images.table.images = CONNECTION.execute(SELECT, fetch=1)

        self.images.table.layoutChanged.emit()
        self.images.resizeRowsToContents()
        self.images.resizeColumnsToContents()
        self.statusbar(self.images.total())

    def get_filter(self, i=0):
        
        string = self.ribbon.tags.text()
        if string: self.ribbon.update(string)

        query = ['path LIKE "C:%"']
        
        if self.title == 'Gesture Draw':
            
            query.append('date_used <= Now() - INTERVAL 2 MONTH')

        try: # Get type
            type_, = re.findall('type=(?:photo|illus|comic?)', string)
            string = string.replace(type_, '')
            type_ = TYPE[type_[5:].capitalize()]
        except: type_ = TYPE[self.type.checkedAction().text().lower()]
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
            rating = RATING[rating.capitalize()]
        except: rating = RATING[self.rating.checkedAction().text()]
        finally: query.append(rating.lower())
        
        try: # Get artist
            artist, = re.findall('artist=\w+', string)
            string = string.replace(artist, '')
            artist = re.sub('artist=(.+)', r'artist LIKE "%\1%"', artist)
        except: artist = ''
        finally: query.append(artist.lower())
        
        try: # Get path
            path, =  re.findall('path=\w+', string, re.IGNORECASE)
            string = string.replace(path, '')

            if re.search('jpg|gif|webm|mp4/Z', path): sub = r'%\1'
            elif re.search('path=.:', path): 
                sub = r'\1%'
                path = re.sub('.:', 'C:', path)
            else: sub = r'%\1%'
            
            path = re.sub('path=(.+)', f'path LIKE "{sub}"', path)
        except: path = ''
        finally: query.append(path)
                
        try: # Get site
            site, =  re.findall('site=\w+', string, re.IGNORECASE)
            string = string.replace(site, '')
            site = re.sub('site=(.+)', r'site="\1"', site)
        except: site = ''
        finally: query.append(site.lower())

        try: # Read comic
            comic, =  re.findall('comic:\w+', string, re.IGNORECASE)
            string = string.replace(comic, '')
            comic = re.sub('comic:(.+)', r'src="\1"', comic)
            i = 1
            query[3] = ''
        except: comic = ''
        finally: query.append(comic.lower())
        
        if string.strip(): # Get tags
    
            string = re.sub('NOT ', '-', string.strip())
            string = re.sub('(-?\w+( OR -?\w+)+)', r'(\1)', string)
            string = re.sub('([*]?\w+|\([^()]*\))', r'+\1', string)
            string = re.sub('(\+AND|OR) ', '', string)
            string = re.sub('-\+', '-', string)
            if not re.search('\+\w+', string): string += ' qwd'

            query.append(
                f'MATCH(tags, artist) AGAINST("{string}" IN BOOLEAN MODE)'
                )

        return f'WHERE {" AND ".join(i for i in query if i)} {self.get_order(i)}'
        
        return f'WHERE GROUP BY hash HAVING COUNT(hash) > 1 ORDER BY hash'

    def get_order(self, type_, ORDER={'Ascending': 'ASC', 'Descending':'DESC'}):
        
        order = self.order
        if type_: column = 'page'
        else: column = order[0].checkedAction().text()
        order = order[1].checkedAction().text()
        
        if column:
            column = 'RAND()' if column == 'Random' else column
            return f' ORDER BY {column} {ORDER[order]}'

        return ''
            
    def statusbar(self, total=0, select=0):
         
        total = f'{total} image' if (total == 1) else f'{total} images'
        if select:
            select = f'{select} image selected' if (select == 1) else f'{select} images selected'
        else: select = ''
        
        try: self.parent().statusbar.showMessage(f'   {total}     {select}')
        except: self.parent().parent().statusbar.showMessage(f'   {total}     {select}')
    
    def keyPressEvent(self, sender):
    
        key_press = sender.key()
        modifiers = sender.modifiers()
        alt = modifiers == Qt.AltModifier

        if alt:
            
            if key_press == Qt.Key_Left: self.ribbon.go_back()
                
            elif key_press == Qt.Key_Right: self.ribbon.go_forward()

        elif key_press == Qt.Key_F4: self.ribbon.tags.setFocus()
        
        elif key_press == Qt.Key_F5: self.populate()

        else: self.parent().keyPressEvent(sender)

class Ribbon(QWidget):
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
        
    def configure_gui(self):
         
        self.undo = ['']
        self.redo = []
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

    def create_widgets(self):
        
        # History navigation
        self.history = QHBoxLayout()
        self.layout.addLayout(self.history)

        self.back = QPushButton()
        self.forward = QPushButton()
        self.menu = QPushButton()
        
        for button, icon, event in zip(
            [self.back, self.forward, self.menu],
            ['SP_ArrowBack', 'SP_ArrowForward', 'SP_ArrowDown'],
            [self.go_back, self.go_forward, self.menu.showMenu]
            ):
            
            button.setIcon(
                self.style().standardIcon(getattr(QStyle, icon))
                )
            button.clicked.connect(event)
            button.setEnabled(False)
            self.history.addWidget(button)

        # Search function
        self.select = QFormLayout()
        self.layout.addLayout(self.select, 0)
        
        self.tags = QLineEdit(self)
        self.tags.setFixedWidth(300)
        self.timer = QTimer(self.tags)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.parent().populate)
        self.tags.textChanged.connect(lambda x: self.timer.start(750))
        self.select.addRow('Search:', self.tags)
        
        if self.parent().parent().windowTitle() == 'Manage Data':
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
    
        self.refresh = QPushButton()
        self.refresh.setIcon(
            self.style().standardIcon(getattr(QStyle, 'SP_BrowserReload'))
            )
        self.refresh.clicked.connect(self.parent().populate)
        self.layout.addWidget(self.refresh, 1, Qt.AlignLeft)
        
    def update(self, string=''):

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
        for state in reversed(self.undo + self.redo[::-1]):
            
            action = QAction(state, menu, checkable=True)
            if state == self.tags.text(): action.setChecked(True)
            menu.addAction(action)

        else: self.menu.setMenu(menu)

        # if string == '':

        #     string = self.undo[-1] if self.undo else ''
        #     self.tags.setText(string)

    def menuEvent(self, sender):

        action = sender.text()

        if action in self.undo:                

            while action != self.undo[-1]: self.go_back(False)

        elif action in self.redo:                

            while action in self.redo: self.go_forward(False)
        
        self.update()

    def go_back(self, update=True):
        
        if self.undo:
            self.redo.append(self.undo.pop())
            if update: self.update()

    def go_forward(self, update=True):
        
        if self.redo:
            self.undo.append(self.redo.pop())
            if update: self.update()

class ImageView(QTableView):

    def __init__(self, parent):

        super().__init__(parent)
        self.menu = self.create_menu()
        # self.table = Test(self, parent.width())   
        self.table = Model(self, parent.width())   
        self.setModel(self.table)
        self.horizontalHeader().hide()      
        self.verticalHeader().hide()
        self.setGridStyle(0)

        if parent.parent().windowTitle() == 'Manage Data':
            self.doubleClicked.connect(parent.parent().open_slideshow)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuEvent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContentsOnFirstShow
            )
        self.setVerticalScrollMode(1)
        
    def create_menu(self):
        
        menu = QMenu(self)
        parent = self.parent()
        
        temp_menu, sortMenu = self.create_submenu(
            menu, 'Sort by', 
            ['Rowid', 'Path', 'Artist', 'Stars', 'Hash', 'Random'], 
            check=0 if parent.parent().windowTitle() == 'Manage Data' else 5,
            get_menu=True
            )
        sortMenu.addSeparator()
        parent.order = [temp_menu, self.create_submenu(
            sortMenu, None, ['Ascending', 'Descending'], check=0
            )]
        parent.rating = self.create_submenu(
            menu, 'Rating', ['Explicit', 'Questionable', 'Safe'], check=2
            )
        parent.type = self.create_submenu(
            menu, 'Type', ['All', 'Photo', 'Illus', 'Comic'], check=0
            )

        menu.addSeparator()
        menu.addAction(QAction('Copy', menu, triggered=self.copy_path))
        try:
            menu.addAction(
                QAction(
                    'Delete', menu, triggered=parent.parent().delete_records
                    )
                )                
            menu.addSeparator()
            menu.addAction(
                QAction(
                    'Find more by artist', menu, triggered=self.find_by_artist
                    )
                )
            menu.addAction(
                QAction(
                    'Read comic', menu, triggered=self.read_comic                    
                    )
                )
            menu.addSeparator()
            menu.addAction(
                QAction(
                    'Properties', menu, triggered=lambda: Properties(parent, self.selectedIndexes())
                    )
                )
        except AttributeError: pass

        return menu

    def create_submenu(self, parent, name, items, check=None, get_menu=False): 
        
        if name is None: menu = parent
        else: menu = QMenu(name, parent)
        action_group = QActionGroup(menu)

        for num, item in enumerate(items):
            action = QAction(item, menu, checkable=True)
            if num == check: action.setChecked(True)
            action_group.triggered.connect(self.parent().populate)
            action_group.addAction(action)
            menu.addAction(action)

        else:
            if name is not None: parent.addMenu(menu)
            action_group.setExclusive(True)
        
        if get_menu: return action_group, menu
        return action_group

    def find_by_artist(self, sender):

        artist = self.currentIndex().data(1000)[2].pop()
        if artist: self.parent().ribbon.tags.setText(artist)
        else: QMessageBox.Information(
            self, 'Artist', 'This image has no artist'
            )

    def read_comic(self, sender):

        self.parent().ribbon.tags.setText(
            f'comic:{self.currentIndex().data(200)}'
            )
    
    def copy_path(self):
    
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        
        paths = ' '.join(
            f'"{index.data(Qt.UserRole)}"' for index in self.selectedIndexes()
            )
        cb.setText(paths, mode=cb.Clipboard)

    def total(self): return len(self.table.images)
    
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
        
        self.parent().statusbar(self.total(), len(self.selectedIndexes()))

    def contextMenuEvent(self, sender): self.menu.popup(sender)
    
    def keyPressEvent(self, sender):
        
        key_press = sender.key()
        mode = QItemSelectionModel()
        selection = QItemSelection()
        modifier = sender.modifiers()
        ctrl = modifier == Qt.ControlModifier
        shift = modifier == Qt.ShiftModifier
        alt = modifier == Qt.AltModifier

        if alt:
            
            if key_press == Qt.Key_Return and self.selectedIndexes():
            
                Properties(self.parent(), self.selectedIndexes())
            
            elif key_press in (Qt.Key_Right, Qt.Key_Left): 
                
                self.parent().keyPressEvent(sender)
        
        elif ctrl:

            if key_press == Qt.Key_A: self.selectAll()
                    
            elif key_press == Qt.Key_C: self.copy_path()
            
        elif key_press in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Right, Qt.Key_Left):
            
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
                selection.select(
                    *(index, new) if index > new else (new, index)
                    )
                self.selectionModel().select(selection, mode.ToggleCurrent)
                self.selectionModel().setCurrentIndex(new, mode.NoUpdate)

            else: self.setCurrentIndex(new)
                    
        elif key_press in (Qt.Key_PageUp, Qt.Key_PageDown):
            
            index = self.currentIndex()
            row, col = index.row(), index.column()
            sign = 1 if key_press == Qt.Key_PageDown else -1
            
            row += sign * 5
            if 0 > row: row = 0
            elif row > self.table.rowCount(): row = self.table.rowCount() - 1
            new = self.table.index(row, col)

            if shift:
                selection.select(
                    *(index, new) if index > new else (new, index)
                    )
                self.selectionModel().select(selection, mode.ToggleCurrent)
                self.selectionModel().setCurrentIndex(new, mode.NoUpdate)

            else: self.setCurrentIndex(new)

        elif key_press in (Qt.Key_Home, Qt.Key_End):
            
            row, col = (
                (0, 0) if key_press == Qt.Key_Home else 
                (self.table.rowCount() - 1, (self.total() - 1) % self.table.columnCount())
                )
            new = self.table.index(row, col)

            if shift:
                index = self.currentIndex()
                selection.select(
                    *(index, new) if index > new else (new, index)
                    )
                self.selectionModel().select(selection, mode.ToggleCurrent)
                self.selectionModel().setCurrentIndex(new, mode.NoUpdate)

            else: self.setCurrentIndex(new)

        else: self.parent().keyPressEvent(sender)

class Model(QAbstractTableModel):

    def __init__(self, parent, width):

        QAbstractTableModel.__init__(self, parent)
        self.wrapper = textwrap.TextWrapper(width=70)
        self.size = int(width * .1889)
        self.images = []

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
                
                tag, art, sta, rat, typ, = self.images[ind][1:6]

                tags = self.wrapper.wrap(
                    ' '.join(sorted(tag.replace('qwd ', '').split()))
                    )
                rest = self.wrapper.wrap(
                    f'Artist: {art.strip()} Rating: {rat.lower()} Stars: {sta} Type: {typ.lower()}'
                    )
                return '\n'.join(tags + rest)

            elif role == Qt.UserRole: return QVariant(self.images[ind][0])
            
            elif role == 100: return (index.row() * 5), index.column()
            
            elif role == 200: return self.images[ind][6]
                
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

# class Thread(QtCore.QThread):
    
    # sig1 = pyqtSignal(str)
    
    # def __init__(self, parent=None):

    #     QThread.__init__(self, parent)
    
    # def run(self):
    
    #     self.running = True
    #     while self.running:
    #         self.sig1.emit(self.source_txt)

    
    # def __init__(self, *args, **kwargs):

    #     super(Test, self).__init__(*args, **kwargs)
    #     self.database = open_database()
    #     self.setEditStrategy(QSqlTableModel.OnManualSubmit)
    #     self.setTable('imageData')
    #     self.setQuery(
    #         QSqlQuery('SELECT path, tags, artist, rating, stars FROM imageData')
    #         )
    #     self.select()

    # def open_database(self):
         
    #     datab = QSqlDatabase.addDatabase('QODBC')
    #     datab.setUserName(USER)
    #     datab.setPassword(PASS)
    #     datab.setDatabaseName('userData')
    #     datab.setHostName(
    #         '192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    #         )
    #     datab.open()
        
    #     return datab

    # def data(self, index, role=Qt.DisplayRole):

    #     value = super(Test, self).data(index)
    #     if index.column() in self.booleanSet:
    #         if role == Qt.CheckStateRole:
    #             return Qt.Unchecked if value == 2 else Qt.Checked
    #         else:
    #             return QVariant()
    #     return QSqlTableModel.data(self, index, role)

    # def flags(self, index):
    #     if not index.isValid():
    #         return Qt.NoItemFlags
    #     if index.column() in self.booleanSet:
    #         return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable
    #     elif index.column() in self.readOnlySet:
    #         return Qt.ItemIsSelectable | Qt.ItemIsEnabled
    #     else:
    #         return QSqlTableModel.flags(self, index)