import textwrap
from PyQt6.QtGui import QImage, QPixmap, QAction
from PyQt6.QtWidgets import QApplication, QTableView, QAbstractItemView, QMenu
from PyQt6.QtCore import QAbstractTableModel, QItemSelection, QVariant, QModelIndex, Qt, QSize, pyqtSignal

from GUI.utils import BATCH, get_frame, create_submenu
from GUI.propertiesView import Properties

COLUMNS = 5.18

class Gallery(QTableView):
    
    selection = pyqtSignal(QItemSelection, QItemSelection)
    find_artist = pyqtSignal(QModelIndex)
    load_comic = pyqtSignal(object)
    delete = pyqtSignal(list)

    def __init__(self, parent):

        super(QTableView, self).__init__(parent)
        self.table = Model(self)   
        self.setModel(self.table)
        self.create_menu()
        
        for header in [self.horizontalHeader(), self.verticalHeader()]:
            header.setSectionResizeMode(header.ResizeMode.Stretch)
            header.hide()
        else: header.setSectionResizeMode(header.ResizeMode.ResizeToContents)
        
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setGridStyle(Qt.PenStyle.NoPen)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuEvent)
        
    def create_menu(self):
        
        self.menu = QMenu(self)
        self.enums = {}
        self.comic = QAction('Read comic', self.menu)
        
        temp_menu, sortMenu = create_submenu(
            self.menu, 'Sort by', 
            ['Rowid', 'Path', 'Artist', 'Stars', 'Hash', 'Random'], 
            trigger=self.menuPressEvent, get_menu=True
            )
        sortMenu.addSeparator()
        self.enums['order'] = [temp_menu, create_submenu(
            sortMenu, None, ['Ascending', 'Descending'], 
            trigger=self.parent().populateGallery.emit,
            )]
        
        self.enums['rating'] = create_submenu(
            self.menu, 'Rating', ['Explicit', 'Questionable', 'Safe'], trigger=self.parent().populateGallery.emit, check=2
            )
        self.enums['type'] = create_submenu(
            self.menu, 'Type', ['All', 'Photo', 'Illus', 'Comic'], 
            trigger=self.parent().populateGallery.emit,
            )

        self.menu.addSeparator()
        self.menu.addAction(QAction('Copy', self.menu))
        self.menu.addAction(QAction('Delete', self.menu))
                   
        self.menu.addSeparator()
        self.artist = QAction('Find more by artist', self.menu)
        self.menu.addAction(self.artist)
        
        self.menu.addSeparator()
        self.menu.addAction(QAction('Properties', self.menu))

        self.menu.triggered.connect(self.menuPressEvent)
        
    def copy_path(self):
        
        clipboard = QApplication.clipboard()
        clipboard.clear(mode=clipboard.Clipboard)
        
        paths = ', '.join(
            f"{index.data(Qt.ItemDataRole.UserRole)[0]}" 
            for index in self.selectedIndexes()
            if index.data(300) is not None
            )
        clipboard.setText(paths, mode=clipboard.Clipboard)

    def total(self): return len(self.table.images)

    def update(self, images):
        
        self.table.images = images
        self.table.layoutChanged.emit()
    
    def openPersistentEditor(self):
        
        gallery = [
            index.data(Qt.ItemDataRole.EditRole) for index in self.selectedIndexes() 
            if index.data(Qt.ItemDataRole.EditRole) is not None
            ]
        Properties(self.parent().parent(), gallery)
    
    def selectionChanged(self, select, deselect):
        
        self.selection.emit(select, deselect)

    def mouseDoubleClickEvent(self, event):

        self.load_comic.emit([self.currentIndex(), 0])

    def contextMenuEvent(self, event):
        
        index = self.currentIndex().data(Qt.ItemDataRole.EditRole)
        
        if index and index[5].pop() == 'Comic':
            
            self.menu.insertAction(self.artist, self.comic)
            
        else: self.menu.removeAction(self.comic)
        
        self.menu.popup(self.mapToGlobal(event))
            
    def menuPressEvent(self, event):

        match event.text():
            
            case 'Copy': self.copy_path()

            case 'Delete':

                self.delete.emit(self.selectedIndexes())

            case 'Read comic':
            
                self.load_comic.emit(self.currentIndex())

            case 'Find more by artist':

                self.find_artist.emit(self.currentIndex())

            case 'Properties': self.openPersistentEditor()
            
            case _: print(event.text())
        
    def keyPressEvent(self, event):
        
        key_press = event.key()
        mode = self.selectionModel()
        modifier = event.modifiers()
        ctrl = modifier == Qt.KeyboardModifier.ControlModifier
        shift = modifier == Qt.KeyboardModifier.ShiftModifier
        alt = modifier == Qt.KeyboardModifier.AltModifier

        if alt:
            
            if self.selectedIndexes() and key_press in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            
                self.openPersistentEditor()
            
            else: self.parent().keyPressEvent(event)
        
        elif ctrl:

            if shift:
                if key_press == Qt.Key.Key_A: self.clearSelection()

            elif key_press == Qt.Key.Key_A: self.selectAll()
                    
            elif key_press == Qt.Key.Key_C: self.copy_path()
            
            else: self.parent().keyPressEvent(event)
            
        elif key_press in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Right, Qt.Key.Key_Left):
            
            index = self.currentIndex()
            row1, col1 = index.row(), index.column()
            sign = 1 if key_press in (Qt.Key.Key_Down, Qt.Key.Key_Right) else -1

            if key_press in (Qt.Key.Key_Right, Qt.Key.Key_Left):
                
                row2 = row1
                
                if (col1 == 0 and sign < 0) or (col1 == 4 and sign > 0):
                    if not 0 <= (row1 + sign) < self.table.rowCount():
                        return
                    row2 = row1 + sign

                col2 = (col1 + sign) % self.table.columnCount()
                
            elif key_press in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                
                col2 = col1

                if not 0 <= (row1 + sign) < self.table.rowCount(): return
                
                row2 = row1 + sign 
                
            new = self.table.index(row2, col2)
            
            if shift:
                
                if row1 == row2: selection = QItemSelection(index, new)
                
                elif key_press in (Qt.Key.Key_Right, Qt.Key.Key_Left):
                    
                    selection = QItemSelection(index, new)

                elif key_press in (Qt.Key.Key_Up, Qt.Key.Key_Down):

                    start, end = (0, 4) if (sign < 0) else (4, 0)
                    selection = QItemSelection(
                        index, self.table.index(row1, start)
                        )
                    selection.merge(QItemSelection(
                        new,  self.table.index(row2, end)
                        ), self.selectionModel().Select
                        )

                self.selectionModel().select(selection, mode.Select)
                self.selectionModel().setCurrentIndex(new, mode.NoUpdate)

            else: self.setCurrentIndex(new)
                    
        elif key_press in (Qt.Key.Key_PageUp, Qt.Key.Key_PageDown):
            
            index = self.currentIndex()
            row1, col1 = index.row(), index.column()
            sign = 1 if key_press == Qt.Key.Key_PageDown else -1
            
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

        elif key_press in (Qt.Key.Key_Home, Qt.Key.Key_End):
            
            sign = 1 if key_press == Qt.Key.Key_End else -1

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
        
        elif key_press in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            
            self.load_comic.emit(self.currentIndex())

        else: self.parent().parent().keyPressEvent(event)

    def resizeEvent(self, event):

        self.table.width = int(event.size().width() // COLUMNS)
 
class Model(QAbstractTableModel):

    def __init__(self, parent):

        QAbstractTableModel.__init__(self, parent)
        self.wrapper = textwrap.TextWrapper(width=70)
        self.width = int(self.parent().parent().width() // COLUMNS)
        self.images = []
        
    def flags(self, index): 
        
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
    
    def rowCount(self, parent=None):

        rows, cols = divmod(len(self.images), self.columnCount())

        return rows + bool(cols)

    def columnCount(self, parent=None): return 5

    # def canFetchMore(self, index):
        
        # if index.isValid():
        #     return False

        # mysql = self.parent().parent().parent().mysql
        # return mysql.rowcount() > len(self.images)

    # def fetchMore(self, index, fetch=BATCH):

        # mysql = self.parent().parent().parent().mysql
        # start = len(self.images)
        # remainder = mysql.rowcount() - start
        # items_to_fetch = min(fetch, remainder)

        # self.beginInsertRows(QModelIndex(), start, start + items_to_fetch)

        # self.images += mysql.CURSOR.fetchmany(fetch)

        # self.endInsertRows()
    
    def data(self, index, role):
        
        ind = (index.row() * 5) + index.column()

        if ind >= len(self.images) or not any(self.images[ind]):

            return QVariant()
        
        data = self.images[ind]

        match role:
            
            case Qt.ItemDataRole.DecorationRole:
                
                path = data[0]

                image = (
                    get_frame(path) 
                    if path.endswith(('.mp4', '.webm')) else 
                    QImage(path)
                    )

                image = image.scaled(
                    self.width, self.width, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    transformMode=Qt.TransformationMode.SmoothTransformation
                    )
                    
                return QPixmap(image)

            case Qt.ItemDataRole.EditRole:
                
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

            case Qt.ItemDataRole.ToolTipRole:
                
                art, tag, rat, sta, typ, sit, = data[1:7]
                
                tags = self.wrapper.wrap(
                    ' '.join(sorted(tag.replace(' qwd ', ' ').split()))
                    )
                rest = self.wrapper.wrap(
                    f'Artist: {art.strip()} Rating: {rat.lower()} Stars: {sta} Type: {typ.lower()} Site: {sit}'
                    )
                return '\n'.join(tags + rest)

            case Qt.ItemDataRole.SizeHintRole:
                
                return QSize(self.width, self.width)
            
            case Qt.ItemDataRole.UserRole: return data
            
            case 100: return (index.row() * 5), index.column()
            
            case 300: return ind
        
        return QVariant()
    
    def setData(self, index, value, role):
        
        if role == Qt.ItemDataRole.EditRole and index.isValid():
            
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

            return True
            
        return False