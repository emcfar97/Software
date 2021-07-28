import textwrap, re
from .. import COMIC, BATCH, get_frame
from ..propertiesView import Properties
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QAbstractTableModel, QItemSelection, QVariant, QModelIndex, Qt, QSize
from PyQt5.QtWidgets import QApplication, QTableView, QAbstractItemView, QMenu, QAction, QActionGroup, QMessageBox

class Gallery(QTableView):

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
            check=0 if parent.windowTitle() == 'Manage Data' else 5,
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
            action_group.triggered.connect(self.parent().ribbon.update_query)
            action_group.addAction(action)
            menu.addAction(action)

        else:
            if name is not None: parent.addMenu(menu)
            action_group.setExclusive(True)
        
        if get_menu: return action_group, menu
        return action_group
    
    def find_by_artist(self, event):

        artist = self.currentIndex().data(Qt.UserRole)[1]
        if artist: 
            artist = ' OR '.join(artist.split())
            self.parent().ribbon.tags.setText(artist)
        else: QMessageBox.information(
            self, 'Artist', 'This image has no artist'
            )

    def read_comic(self, event=None):
        
        parent = self.parent().parent()
        path = self.currentIndex().data(Qt.UserRole)[0]
        parent_, = parent.MYSQL.execute(COMIC, (path,), fetch=1)[0]
        parent.ribbon.tags.setText(f'comic={parent_}')
    
    def copy_path(self):
        
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        
        paths = ' '.join(
            f'"{index.data(Qt.UserRole)[0]}"' 
            for index in self.selectedIndexes()
            )
        cb.setText(paths, mode=cb.Clipboard)

    def total(self): return len(self.table.images)

    def update(self, images):
        
        parent = self.parent().parent()
        self.clearSelection()
        if not isinstance(images, list): images = list()
        parent.update_statusbar(parent.MYSQL.rowcount)
        self.table.images = images
        self.table.layoutChanged.emit()
    
    def delete(self, event):

        self.parent().parent().delete_records(
            self.selectedIndexes()
            )

    def openPersistentEditor(self):
        
        gallery = [
            index.data(Qt.EditRole) for index in self.selectedIndexes() 
            if index.data(Qt.EditRole) is not None
            ]
        Properties(self.parent().parent(), gallery)
    
    def selectionChanged(self, select, deselect):
        
        if self.table.images:
            
            if self.parent().parent().windowTitle() == 'Manage Data':

                if select := select.indexes():
                    image = select[0]
                
                elif self.selectedIndexes():
                    image = min(self.selectedIndexes())
                
                else: image = None

                self.parent().parent().preview.update(image)
            
            self.parent().parent().update_statusbar(
                self.total(), len(self.selectedIndexes())
                )

    def mouseDoubleClickEvent(self, event):

        parent = self.parent().parent()

        if re.match('type=.comic.', parent.ribbon.query):
            
            self.read_comic()
        
        else: parent.start_slideshow()

    def contextMenuEvent(self, event):
        
        title = self.parent().parent().windowTitle() == 'Manage Data'
        index = self.currentIndex().data(Qt.EditRole)
        
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
        
        elif key_press in (Qt.Key_Return, Qt.Key_Enter):
            
            ribbon = self.parent().parent().ribbon
            if re.match('type=.comic.', ribbon.query):
        
                self.read_comic()

        else: self.parent().keyPressEvent(event)

    def resizeEvent(self, event):

        self.table.width = event.size().width() // self.table.size

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

    def canFetchMore(self, index):
        
        if index.isValid():
            return False

        mysql = self.parent().parent().parent().MYSQL
        return mysql.rowcount > len(self.images)

    def fetchMore(self, index, fetch=BATCH):

        start = len(self.images)
        remainder = self.parent().mysql.rowcount - start
        items_to_fetch = min(fetch, remainder)

        self.beginInsertRows(QModelIndex(), start, start + items_to_fetch)

        self.images += self.parent().mysql.CURSOR.fetchmany(fetch)

        self.endInsertRows()
    
    def data(self, index, role):
        
        ind = (index.row() * 5) + index.column()

        if ind >= len(self.images) or not any(self.images[ind]):

            return QVariant()
        
        data = self.images[ind]

        if role == Qt.DecorationRole:
            
            path = data[0]

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
            
            data = data[:7]
            
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
            
            art, tag, rat, sta, typ, sit, = data[1:7]
            
            tags = self.wrapper.wrap(
                ' '.join(sorted(tag.replace(' qwd ', ' ').split()))
                )
            rest = self.wrapper.wrap(
                f'Artist: {art.strip()} Rating: {rat.lower()} Stars: {sta} Type: {typ.lower()} Site: {sit}'
                )
            return '\n'.join(tags + rest)

        if role == Qt.SizeHintRole: return QSize(self.width, self.width)
        
        if role == Qt.UserRole: return data
        
        if role == 100: return (index.row() * 5), index.column()
        
        if role == 300: return ind
        
        return QVariant()
    
    def setData(self, index, value, role):
        
        if role == Qt.EditRole and index.isValid():
            
            self.dataChanged.emit(index, index, [Qt.DisplayRole])

            return True
            
        return False