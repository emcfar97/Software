import textwrap
from PyQt5.QtGui import QImage, QPixmap, QDrag
from PyQt5.QtCore import QAbstractTableModel, QItemSelection, QVariant, QModelIndex, Qt, QSize, QMimeData, pyqtSignal, QRect, QPoint
from PyQt5.QtWidgets import QApplication, QTableView, QAbstractItemView, QMenu, QAction, QStyledItemDelegate

from .. import COLUMNS, get_frame, create_submenu, create_submenu_
from ..propertiesView import Properties

CONSTANTS = {
    'Sort': ['Rowid', 'Path', 'Artist', 'Stars', 'Hash', 'Random'],
    'Order': ['Ascending', 'Descending'],
    'Rating': ['Explicit', 'Questionable', 'Safe'],
    'Type': ['All', 'Photo', 'Illus', 'Comic']
    }

class Gallery(QTableView):
    
    selection = pyqtSignal(QItemSelection, QItemSelection)
    find_artist = pyqtSignal(QModelIndex)
    delete = pyqtSignal(list)
    load_comic = pyqtSignal(object)

    def __init__(self, parent):

        super(QTableView, self).__init__(parent)
        self.setItemDelegate(PaintDelegate(self))
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
        
        self.setStyleSheet('''
            QTableView {
                outline: 0;
            }
            QTableView::item:selected {   
                background: #CDE8FF;
                border: 1px solid #99D1FF
            }
            QTableView::item:!selected:hover
            {   
                background: #E5F3FF;
            }
        ''')
        
    def create_menu(self):
        
        menu = QMenu(self)
        parent = self.parent()
        self.comic = QAction('Read comic', menu)
        
        temp_menu, sortMenu = create_submenu(
            menu, 'Sort by', 
            ['Rowid', 'Path', 'Artist', 'Stars', 'Hash', 'Random'], 
            check=0, trigger=parent.select_records, get_menu=True
            )
        sortMenu.addSeparator()
        parent.order = [temp_menu, create_submenu(
            sortMenu, None, ['Ascending', 'Descending'], check=0, trigger=parent.select_records
            )]
        parent.rating = create_submenu(
            menu, 'Rating', ['Explicit', 'Questionable', 'Safe'], check=2, trigger=parent.select_records
            )
        parent.type = create_submenu(
            menu, 'Type', ['All', 'Photo', 'Illus', 'Comic'], check=0, trigger=parent.select_records
            )
        
        # sortMenu, temp_menu = create_submenu_(
        #     menu, 'Sort by', CONSTANTS['Sort'], 
        #     trigger=parent.select_records, check=0
        #     )
        # sortMenu.addSeparator()
        # parent.order = [temp_menu, create_submenu_(
        #     sortMenu, None, CONSTANTS['Order'],
        #     trigger=parent.select_records, check=0
        #     )[1]
        #     ]
        # parent.rating = create_submenu_(
        #     menu, 'Rating', CONSTANTS['Rating'],
        #     trigger=parent.select_records, check=2
        #     )[1]
        # parent.type = create_submenu_(
        #     menu, 'Type', CONSTANTS['Type'],
        #     trigger=parent.select_records
        #     )[1]

        menu.addSeparator()
        menu.addAction(QAction('Copy', menu))
        menu.addAction(QAction('Delete', menu))            
        menu.addSeparator()
        self.artist = QAction('Find more by artist', menu)
        menu.addAction(self.artist)
        menu.addSeparator()
        menu.addAction(QAction('Properties', menu))

        menu.triggered.connect(self.menuPressEvent)

        return menu
    
    def copy_path(self):
        
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        
        paths = ', '.join(
            f"{index.data(Qt.UserRole)[0]}" 
            for index in self.selectedIndexes()
            if index.data(300) is not None
            )
        cb.setText(paths, mode=cb.Clipboard)

    def total(self): return len(self.table.images)

    def update(self, images):
        
        self.table.images = images
        self.table.layoutChanged.emit()
    
    # def pixmap(self):
        
        # # for image in self.selectedIndexes()[0]:
        
        # path = self.currentIndex().data(Qt.UserRole)[0]
        # image = (
        #     get_frame(path) 
        #     if path.endswith(('.mp4', '.webm')) else 
        #     QImage(path)
        #     )

        # image = image.scaled(
        #     100, 100, Qt.KeepAspectRatio, 
        #     transformMode=Qt.SmoothTransformation
        #     )
            
        # return QPixmap(image)
            
    def openPersistentEditor(self):
        
        gallery = [
            index.data(Qt.EditRole) for index in self.selectedIndexes() 
            if index.data(Qt.EditRole) is not None
            ]
        Properties(self.parent().parent(), gallery)
    
    def selectionChanged(self, select, deselect):
            
        self.selection.emit(select, deselect)

    def mouseDoubleClickEvent(self, event):

        self.load_comic.emit([self.currentIndex(), 0])

    # def mouseReleaseEvent(self, event):
        
        # button_press = event.button()
        
        # self.parent().parent().mousePressEvent(event)
        
    # def mouseMoveEvent(self, event):
        
        # drag = QDrag(self)
        # mimeData = QMimeData()
        # mimeData.setUrls([self.currentIndex().data(Qt.UserRole)[0]])
        
        # drag.setMimeData(mimeData)
        # drag.setPixmap(self.pixmap())
        # drag.setHotSpot(event.pos())
        # drag.exec_(Qt.MoveAction)
            
    def contextMenuEvent(self, event):
        
        index = self.currentIndex().data(Qt.EditRole)
        
        if index and index[5].pop() == 'Comic':
            self.menu.insertAction(self.artist, self.comic)
        else: self.menu.removeAction(self.comic)
        
        self.menu.popup(self.mapToGlobal(event))
    
    def menuPressEvent(self, event):

        action = event.text()
        
        if action == 'Copy': self.copy_path()

        elif action == 'Delete':

            self.delete.emit(self.selectedIndexes())

        elif action == 'Read comic':
            
            self.load_comic.emit([self.currentIndex(), 1])

        elif action == 'Find more by artist':

            self.find_artist.emit(self.currentIndex())

        elif action == 'Properties':

            self.openPersistentEditor()

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
                
                elif key_press in (Qt.Key_Right, Qt.Key_Left):
                    
                    selection = QItemSelection(index, new)

                elif key_press in (Qt.Key_Up, Qt.Key_Down):

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
            
            self.load_comic.emit([self.currentIndex(), 2])

        else: self.parent().parent().keyPressEvent(event)

    def resizeEvent(self, event):

        self.table.width = int(event.size().width() // COLUMNS)

class Model(QAbstractTableModel):
    
    number_populated = pyqtSignal(int)

    def __init__(self, parent):

        QAbstractTableModel.__init__(self, parent)
        self.wrapper = textwrap.TextWrapper(width=70)
        self.width = int(self.parent().parent().width() // COLUMNS)
        self.images = []
        
    def flags(self, index):
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
    
    def rowCount(self, parent=None):

        rows, cols = divmod(len(self.images), self.columnCount())

        return rows + bool(cols)

    def columnCount(self, parent=None): return COLUMNS

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

        # if items_to_fetch <= 0:
        #     return
        
        # self.beginInsertRows(QModelIndex(), start, start + items_to_fetch)

        # self.images += mysql.CURSOR.fetchmany(fetch)

        # self.endInsertRows()
        
        # self.number_populated.emit(items_to_fetch)
    
    def data(self, index, role):
        
        ind = (index.row() * 5) + index.column()

        if ind >= len(self.images) or not any(self.images[ind]):

            return QVariant()
        
        data = self.images[ind]

        if role == Qt.DecorationRole: return data[0]

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
    
    def setData(self, index, value, role=Qt.EditRole):
        
        if role == Qt.EditRole and index.isValid():
            
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)

            return True
            
        return False

class PaintDelegate(QStyledItemDelegate):
    
    def paint(self, painter, option, index):

        QStyledItemDelegate.paint(self, painter, option, index)

        if index.data(Qt.DecorationRole) is not None:

            path = index.data(Qt.DecorationRole)
            width = self.parent().table.width
            rect = QPoint(width, width)
                      
            painter.save()

            image = (
                get_frame(path) 
                if path.endswith(('.mp4', '.webm')) else 
                QImage(path)
                )
            image = image.scaled(
                rect.x() - 10, rect.x() - 10, Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
            
            offset = rect - QPoint(image.size().width(), image.size().height())
            painter.drawImage(option.rect.topLeft() + offset/2, image)
            painter.restore()