import re, textwrap
from . import MYSQL, BASE, COMIC, get_frame
from .propertiesView import Properties
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QAbstractTableModel, QItemSelection, QObject, QThread, QTimer, QVariant, Qt, QSize, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QFormLayout, QTableView, QAbstractItemView, QMenu, QAction, QActionGroup, QPushButton, QCheckBox, QMessageBox, QStyle, QCompleter

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

    def populate(self, event=None, limit=10000, op='[<>=!]=?'):
        
        self.query = {}
        join = ''
        order = self.get_order()
        self.images.clearSelection()
        string = self.ribbon.tags.text()
        if string: self.ribbon.update(string)
        
        if self.title == 'Gesture Draw':
            
            self.query['gesture'] = ['date_used <= Now() - INTERVAL 2 MONTH']
        else: self.parent().parent().preview.show_image(None)

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
        
        self.thread.statement = f'{BASE} {join} WHERE {filter} {order} LIMIT {limit}'
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
        autocomplete = open(r'GUI\autocomplete.txt').read()
        self.tags.setCompleter(
            QCompleter(autocomplete.split())
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

class ImageView(QTableView):

    def __init__(self, parent):

        super(QTableView, self).__init__(parent)
        self.table = Model(self)   
        self.setModel(self.table)
        self.menu = self.create_menu()
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
        
    def create_menu(self):
        
        menu = QMenu(self)
        parent = self.parent()
        self.comic = QAction('Read comic', menu, triggered=self.read_comic)
        
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
                QAction('Delete', menu, triggered=self.delete)
                )                
            menu.addSeparator()
            self.artist = QAction(
                'Find more by artist', menu, triggered=self.find_by_artist
                )
            menu.addAction(self.artist)
            menu.addSeparator()
            menu.addAction(
                QAction(
                    'Properties', menu, triggered=self.openPersistentEditor
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
    
    def delete(self, event):

        random = 'RANDOM' in self.parent().get_order()

        self.parent().parent().parent().delete_records(
            self.selectedIndexes(), not random
            )

    def find_by_artist(self, event):

        artist = self.currentIndex().data(Qt.UserRole)[2]
        if artist: 
            artist = ' OR '.join(artist.pop().split())
            self.parent().ribbon.tags.setText(artist)
        else: QMessageBox.information(
            self, 'Artist', 'This image has no artist'
            )

    def read_comic(self, event):

        path = self.currentIndex().data(Qt.UserRole)[0].pop()
        parent, = MYSQL.execute(COMIC, (path,), fetch=1)
        self.parent().ribbon.tags.setText(f'comic={parent[0]}')
    
    def copy_path(self):
        
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        
        paths = ' '.join(
            f'"{index.data(Qt.UserRole)[0].pop()}"' 
            for index in self.selectedIndexes()
            )
        cb.setText(paths, mode=cb.Clipboard)

    def total(self): return len(self.table.images)

    def update(self, images):
        
        if isinstance(images, bool): images = list()
        self.parent().statusbar(MYSQL.rowcount)
        self.table.images = images
    
    def openPersistentEditor(self):
        
        gallery = [
            index.data(Qt.UserRole) for index in self.selectedIndexes() 
            if index.data(Qt.UserRole) is not None
            ]
        Properties(self.parent().parent().parent(), gallery)
    
    def selectionChanged(self, select, deselect):
        
        if self.table.images:
            
            if self.parent().title == 'Manage Data':

                if select := select.indexes():
                    image = select[0]
                
                elif self.selectedIndexes(): 
                    image = min(self.selectedIndexes())
                
                else: image = None

                preview = self.parent().parent().parent().preview
                try: preview.show_image(image)
                except: preview.show_image(None)
            
            self.parent().statusbar(self.total(), len(self.selectedIndexes()))

    def mouseDoubleClickEvent(self, event):

        parent = self.parent()
        if parent.title == 'Manage Data':

            if 'comic' in parent.query.get('type', [''])[0] and '3' not in parent.query:
                
                self.read_comic(None)
            
            else: parent.parent().parent().start_slideshow()

    def contextMenuEvent(self, event):
        
        title = self.parent().title == 'Manage Data'
        index = self.currentIndex().data(Qt.UserRole)
        
        if index and title and index[5].pop() == 'Comic':
            self.menu.insertAction(self.artist, self.comic)
        else: self.menu.removeAction(self.comic)
        
        self.menu.popup(self.mapToGlobal(event))
    
    def keyPressEvent(self, event):
        
        key_press = event.key()
        mode = self.selectionModel()
        modifier = event.modifiers()
        ctrl = modifier == Qt.ControlModifier
        shift = modifier == Qt.ShiftModifier
        alt = modifier == Qt.AltModifier

        if alt:
            
            if self.selectedIndexes() and key_press in (Qt.Key_Return, Qt.Key_Enter):
            
                self.openPersistentEditor()
            
            else: self.parent().keyPressEvent(event)
        
        elif ctrl:

            if shift:
                if key_press == Qt.Key_A: self.clearSelection()

            elif key_press == Qt.Key_A: self.selectAll()
                    
            elif key_press == Qt.Key_C: self.copy_path()
            
            else: self.parent().keyPressEvent(event)
            
        elif key_press in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Right, Qt.Key_Left):
            
            index = self.currentIndex()
            row1, col1 = index.row(), index.column()
            sign = 1 if key_press in (Qt.Key_Down, Qt.Key_Right) else -1

            if key_press in (Qt.Key_Right, Qt.Key_Left):
                
                row2 = row1
                
                if (col1 == 0 and sign < 0) or (col1 == 4 and sign > 0):
                    if not 0 <= (row1 + sign) < self.table.rowCount():
                        return
                    row2 = row1 + sign

                col2 = (col1 + sign) % self.table.columnCount()
                
            elif key_press in (Qt.Key_Up, Qt.Key_Down):
                
                col2 = col1

                if not 0 <= (row1 + sign) < self.table.rowCount(): return
                
                row2 = row1 + sign 
                
            new = self.table.index(row2, col2)
            
            if shift:
                
                if row1 == row2: selection = QItemSelection(index, new)
                    
                else:

                    start, end = (0, 4) if (sign < 0) else (4, 0)
                    selection = QItemSelection(
                        index, self.table.index(row2, start)
                        )
                    selection.merge(QItemSelection(
                        new,  self.table.index(row2, end)
                        ), self.selectionModel().Select
                        )

                self.selectionModel().select(selection, mode.Select)
                self.selectionModel().setCurrentIndex(new, mode.NoUpdate)

            else: self.setCurrentIndex(new)
                    
        elif key_press in (Qt.Key_PageUp, Qt.Key_PageDown):
            
            index = self.currentIndex()
            row1, col1 = index.row(), index.column()
            sign = 1 if key_press == Qt.Key_PageDown else -1
            
            row2 = row1 + (sign * 5)
            if 0 > row2: row2, col2 = 0, 0
            elif row2 > self.table.rowCount():
                row2, col2 = self.table.rowCount() - 1, 4
            else: col2 = col1
            
            new = self.table.index(row2, col2)

            if shift:
                
                selection = QItemSelection(
                    self.table.index(row1, 4), 
                    self.table.index(row1, col1)
                    )
                selection.merge(QItemSelection(
                    self.table.index(row1 + sign, 0), 
                    self.table.index(row2 - sign, 4)
                    ), self.selectionModel().Select
                    )
                selection.merge(QItemSelection(
                    self.table.index(row2, col1), 
                    self.table.index(row2, 0)
                    ), self.selectionModel().Select
                    )

                self.selectionModel().select(selection, mode.Select)
                self.selectionModel().setCurrentIndex(new, mode.NoUpdate)

            else: self.setCurrentIndex(new)

        elif key_press in (Qt.Key_Home, Qt.Key_End):
            
            sign = 1 if key_press == Qt.Key_End else -1

            row1, col1 = (
                (0, 0) if sign < 0 else 
                (
                    self.table.rowCount() - 1, 
                    (self.total() - 1) % self.table.columnCount()
                    )
                )
            new = self.table.index(row1, col1)

            if shift:

                index = self.currentIndex()
                row2, col2 = index.row(), index.column()

                selection = QItemSelection(
                    self.table.index(index.row(), col1), 
                    index
                    )
                selection.merge(QItemSelection(
                    self.table.index(row2 + sign, 0), 
                    self.table.index(row1 - sign, 4)
                    ), self.selectionModel().Select
                    )
                selection.merge(QItemSelection(
                    self.table.index(row1, 0), 
                    self.table.index(row1, 4)
                    ), self.selectionModel().Select
                    )

                self.selectionModel().select(selection, mode.Select)
                self.selectionModel().setCurrentIndex(new, mode.NoUpdate)

            else: self.setCurrentIndex(new)
        
        elif self.parent().title == 'Manage Data' and 'comic' in self.parent().query.get('type', [''])[0] and '3' not in self.parent().query:
        
            if key_press in (Qt.Key_Return, Qt.Key_Enter): self.read_comic(None)
            else: self.parent().keyPressEvent(event)

        else: self.parent().keyPressEvent(event)

class Model(QAbstractTableModel):

    def __init__(self, parent, size=5.18):

        QAbstractTableModel.__init__(self, parent)
        self.wrapper = textwrap.TextWrapper(width=70)
        self.images = []
        self.size = size
        self.width = self.parent().parent().width() // self.size
        
    def flags(self, index): return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def rowCount(self, parent=None):

        rows, cols = divmod(len(self.images), self.columnCount())

        return rows + bool(cols)

    def columnCount(self, parent=None): return 5

    # def canFetchMore(self, index):
        
        # return MYSQL.rowcount > len(self.images)

    # def fetchMore(self, index, fetch=10000):
        
        # self.beginInsertRows(
        #     index, len(self.images), len(self.images) + fetch
        #     )
        # self.images += MYSQL.CURSOR.fetchmany(fetch)
        # self.endInsertRows()
        # self.numberPopulated.emit(self.images[:-fetch])

    def data(self, index, role):
        
        ind = (index.row() * 5) + index.column()

        if ind >= len(self.images) or not self.images[ind][0]:

            return QVariant()
            
        if role == Qt.DecorationRole:
            
            path = self.images[ind][0]
            image = (
                get_frame(path) 
                if path.endswith(('.mp4', '.webm')) else 
                QImage(path)
                )

            image = image.scaled(
                self.width, self.width, Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
                
            return QPixmap(image)

        if role == Qt.EditRole:
            
            data = self.images[ind]
            
            path = {data[0]}
            artist = set(data[1].split())
            tags = set(data[2].split())
            rating = {data[3]}
            stars = {data[4]}
            type = {data[5]}
            site = {data[6]}

            tags.discard('qwd')
            
            return path, tags, artist, stars, rating, type, site

        if role == Qt.ToolTipRole:
            
            art, tag, rat, sta, typ, sit, = self.images[ind][1:7]
            
            tags = self.wrapper.wrap(
                ' '.join(sorted(tag.replace(' qwd ', ' ').split()))
                )
            rest = self.wrapper.wrap(
                f'Artist: {art.strip()} Rating: {rat.lower()} Stars: {sta} Type: {typ.lower()} Site: {sit}'
                )
            return '\n'.join(tags + rest)

        if role == Qt.SizeHintRole: return QSize(self.width, self.width)
        
        if role == Qt.UserRole:
            
            data = self.images[ind]
            
            path = {data[0]}
            artist = set(data[1].split())
            tags = set(data[2].split())
            rating = {data[3]}
            stars = {data[4]}
            type = {data[5]}
            site = {data[6]}

            tags.discard('qwd')
            
            return path, tags, artist, stars, rating, type, site
        
        if role == 100: return (index.row() * 5), index.column()
        
        if role == 300: return ind
        
        return QVariant()
    
    def setData(self, index, value, role):
        
        if role == Qt.EditRole and index.isValid():
            
            self.dataChanged.emit(index, index, [Qt.DisplayRole])

class Worker_(QObject):

    finished = pyqtSignal()

    def run(self):
        
        rows = MYSQL.execute(self.statement, fetch=1)
        self.parent().images.update(rows)
        self.finished.emit()

    def __init__(self, parent):
        
        super(Worker, self).__init__(parent)

class Worker(QThread):
    
    def __init__(self, parent):
        
        super(Worker, self).__init__(parent)
    
    def run(self):
    
        self.parent().images.update(
            MYSQL.execute(self.statement, fetch=1)
            )