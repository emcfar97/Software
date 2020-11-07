import re, textwrap
from . import CONNECTION, BASE, get_frame
from .propertiesView import Properties
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QAbstractTableModel, QItemSelectionModel, QItemSelection, QThread, QTimer, QVariant, Qt, QSize, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QFormLayout, QTableView, QAbstractItemView, QMenu, QAction, QActionGroup, QPushButton, QMessageBox, QStyle

TYPE = {
    'All': '',
    'Photo': 'type=1', 
    'Illus': 'type=2', 
    'Comic': 'type=3',
    }
RATING = {
    'Explicit': '',
    'Questionable': 'rating<3',
    'Safe': 'rating=1' 
    }

class Gallery(QWidget):
     
    def __init__(self, parent):
         
        super(Gallery, self).__init__(parent)
        self.title = parent.windowTitle()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 0, 0, 0)
        self.create_widgets()
                    
    def create_widgets(self):
        
        self.windows = set()
        self.ribbon = Ribbon(self)
        self.images = ImageView(self)
        self.thread = Worker(self)
         
        self.layout.addWidget(self.ribbon)
        self.layout.addWidget(self.images)
        self.thread.finished.connect(
            self.images.table.layoutChanged.emit
            )

    def populate(self, event=None, limit=50000, op='[<>=!]=?'):
        
        self.images.clearSelection()
        string = self.ribbon.tags.text()
        if string: self.ribbon.update(string)
        
        self.query = {
            'type': TYPE[self.type.checkedAction().text()],
            'rating': RATING[self.rating.checkedAction().text()],
            }
        order = self.get_order()
        
        if self.title == 'Gesture Draw':
            
            self.query['gesture'] = 'date_used <= Now() - INTERVAL 2 MONTH'
        else: self.parent().parent().preview.show_image(None)

        for token in re.findall(f'\w+{op}[\w\*]+', string):
            
            string = string.replace(token, '')
            col, val = re.split(op, token)
            
            if re.search('\*', val): 
                
                token = f'{col} LIKE "{val.replace("*", "%")}"'

            elif re.search('\D', val):

                token = re.sub(f'(\w+{op})(\w+)', r'\1"\2"', token)
            
            elif col == 'comic': 
                
                token = f'src={val}'
                order = self.get_order(1)

            self.query[col] = token
        
        if string.strip():
    
            string = re.sub('(-?\w+( OR -?\w+)+)', r'(\1)', string)
            string = re.sub('NOT ', '-', string.strip())
            string = re.sub('([*]?\w+|\([^()]*\))', r'+\1', string)
            string = re.sub('(\+AND|OR) ', '', string)
            string = re.sub('-\+', '-', string)
            if not re.search('\+\w+', string): string += ' qwd'

            self.query['tags'] = (
                f'MATCH(tags, artist) AGAINST("{string}" IN BOOLEAN MODE)'
                )

        if not any(self.query.values()): self.query[''] = 'NOT ISNULL(path)'
        
        filter = " AND ".join(val for val in self.query.values() if val)
        
        self.thread.statement = f'{BASE} WHERE {filter} {order} LIMIT {limit}'
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

        elif key_press == Qt.Key_F4: self.ribbon.tags.setFocus()
        
        elif key_press == Qt.Key_F5: self.populate()

        else: self.parent().keyPressEvent(event)

class Ribbon(QWidget):
     
    def __init__(self, parent):
         
        super().__init__(parent)
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
        self.timer = QTimer(self.tags)
        
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.parent().populate)
        self.tags.textChanged.connect(lambda: self.timer.start(750))
        self.select.addRow('Search:', self.tags)
        
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
    
        self.refresh = QPushButton()
        self.refresh.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.refresh.clicked.connect(self.parent().populate)
        self.layout.addWidget(self.refresh, 1, Qt.AlignLeft)
        
        self.tags.setFocus()
        
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
        for state in reversed(self.undo[1:] + self.redo[::-1]):
            
            action = QAction(state, menu, checkable=True)
            if state == string: action.setChecked(True)
            menu.addAction(action)

        else: self.menu.setMenu(menu)
        
        self.tags.setText(self.undo[-1])
        
    def menuEvent(self, event):

        action = event.text()

        if action in self.undo:

            while action != self.undo[-1]: self.go_back(update=False)

        elif action in self.redo:

            while action in self.redo: self.go_forward(update=False)
        
        self.update()

    def go_back(self, event=None, update=True):
        
        if len(self.undo) > 1:
            self.redo.append(self.undo.pop())
            if update: self.update()

    def go_forward(self, event=None, update=True):
        
        if self.redo:
            self.undo.append(self.redo.pop())
            if update: self.update()
    
    def keyPressEvent(self, event):
    
        key_press = event.key()

        if key_press == Qt.Key_Return: pass

        else: self.parent().keyPressEvent(event)

class ImageView(QTableView):

    def __init__(self, parent):

        super(QTableView, self).__init__(parent)
        self.menu = self.create_menu()
        self.table = Model(self)   
        self.setModel(self.table)
        for header in [self.horizontalHeader(), self.verticalHeader()]:
            header.setSectionResizeMode(header.Stretch)
            header.hide()
        else: header.setSectionResizeMode(header.ResizeToContents)
        
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setVerticalScrollMode(1)
        self.setGridStyle(0)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuEvent)
        if parent.title == 'Manage Data':
            self.doubleClicked.connect(parent.parent().start_slideshow)
        
    def create_menu(self):
        
        menu = QMenu(self)
        parent = self.parent()
        
        temp_menu, sortMenu = self.create_submenu(
            menu, 'Sort by', 
            ['Rowid', 'Path', 'Artist', 'Stars', 'Hash', 'Random'], 
            check=0 if parent.title == 'Manage Data' else 5,
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
    
    def find_by_artist(self, event):

        artist = self.currentIndex().data(1000)[2].pop()
        if artist: self.parent().ribbon.tags.setText(artist)
        else: QMessageBox.Information(
            self, 'Artist', 'This image has no artist'
            )

    def read_comic(self, event):

        self.parent().ribbon.tags.setText(
            f'comic:{self.currentIndex().data(200)}'
            )
    
    def duplicates(self):

        self.parent().ribbon.tags.setText(f'duplicates:True')

    def copy_path(self):
    
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        
        paths = ' '.join(
            f'"{index.data(Qt.UserRole)}"' for index in self.selectedIndexes()
            )
        cb.setText(paths, mode=cb.Clipboard)

    def total(self): return len(self.table.images)

    def update(self, images):
        
        self.table.images = images
        self.parent().statusbar(len(images))
    
    def selectionChanged(self, select, deselect):
        
        if self.table.images:

            if self.parent().title == 'Manage Data':

                if select := select.indexes(): 
                    image = select[0].data(Qt.UserRole)
                else: 
                    index = sorted(
                        self.selectedIndexes(), key=lambda x: x.data(300)
                        )
                    image = index[0].data(Qt.UserRole) if index else None

                self.parent().parent().parent().preview.show_image(image)
            
            self.parent().statusbar(self.total(), len(self.selectedIndexes()))

    def contextMenuEvent(self, event):
        
        self.menu.popup(self.mapToGlobal(event))
    
    def keyPressEvent(self, event):
        
        key_press = event.key()
        mode = QItemSelectionModel()
        selection = QItemSelection()
        modifier = event.modifiers()
        ctrl = modifier == Qt.ControlModifier
        shift = modifier == Qt.ShiftModifier
        alt = modifier == Qt.AltModifier

        if alt:
            
            if key_press == Qt.Key_Return and self.selectedIndexes():
            
                Properties(self.parent(), self.selectedIndexes())
            
            elif key_press in (Qt.Key_Right, Qt.Key_Left): 
                
                self.parent().keyPressEvent(event)
        
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

        else: self.parent().keyPressEvent(event)

class Model(QAbstractTableModel):

    def __init__(self, parent):

        QAbstractTableModel.__init__(self, parent)
        self.wrapper = textwrap.TextWrapper(width=70)
        self.images = []
        self.size = 5.18
        
    def flags(self, index): return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def rowCount(self, parent=None):

        rows, cols = divmod(len(self.images), self.columnCount())

        return rows + bool(cols)

    def columnCount(self, parent=None): return 5

    def data(self, index, role):
        
        ind = (index.row() * 5) + index.column()

        if not index.isValid() or ind >= len(self.images): return QVariant()
        
        if role == Qt.SizeHintRole:
            
            width = self.parent().parent().width() // self.size
            
            return QSize(width, width)
        
        elif role == Qt.DecorationRole:
    
            if path := self.images[ind][0]: 

                width = self.parent().parent().width() // self.size
                
                image = (
                    get_frame(path) 
                    if path.endswith(('.mp4', '.webm')) else 
                    QImage(path)
                    )

                image = image.scaled(
                    width, width, Qt.KeepAspectRatio, 
                    transformMode=Qt.SmoothTransformation
                    )
                
                return QPixmap(image)

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
        
        elif role == 300: return ind    
        
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
        
        return QVariant()

class Worker(QThread):
    
    def __init__(self, parent): 
        
        super(Worker, self).__init__(parent)

    def run(self):
    
        self.parent().images.update(
            CONNECTION.execute(self.statement, fetch=1)
            )