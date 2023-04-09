import textwrap
from PyQt6.QtGui import QPixmap, QAction#, QDrag
from PyQt6.QtWidgets import QApplication, QTableView, QAbstractItemView, QMenu, QStyledItemDelegate
from PyQt6.QtCore import QAbstractTableModel, QItemSelection, QVariant, QModelIndex, Qt, QPoint, QSize, pyqtSignal#, QMimeData

from GUI.utils import COLUMNS, get_frame, create_submenu, create_submenu_, copy_path
from GUI.propertiesView import Properties

CONSTANTS = {
    'Sort': ['Rowid', 'Path', 'Artist', 'Stars', 'Hash', 'Date', 'Random'],
    'Order': ['Ascending', 'Descending'],
    'Rating': ['Explicit', 'Questionable', 'Safe'],
    'Type': ['All', 'Photo', 'Illus', 'Comic']
    }

class Gallery(QTableView):
    
    selection = pyqtSignal(QItemSelection, QItemSelection)
    find_artist = pyqtSignal(QModelIndex)
    load_comic = pyqtSignal(object)
    delete = pyqtSignal(list)

    def __init__(self, parent):

        super(QTableView, self).__init__(parent)
        self.setItemDelegate(PaintDelegate(self))
        self.table = Model(self)   
        self.setModel(self.table)
        self.create_menu()
        
        for header in [self.horizontalHeader(), self.verticalHeader()]:
            header.setSectionResizeMode(header.ResizeMode.Stretch)
            header.hide()
        else: header.setSectionResizeMode(header.ResizeMode.ResizeToContents)
        
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        self.setGridStyle(Qt.PenStyle.NoPen)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
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
        
        self.enums = {}
        self.menu = QMenu(self)
        parent = self.parent()
        self.comic = QAction('Read comic', self.menu)
        
        temp_menu, sortMenu = create_submenu(
            self.menu, 'Sort by', 
            ['Rowid', 'Path', 'Artist', 'Stars', 'Hash', 'Date', 'Random'], check=0, trigger=self.menuPressEvent, get_menu=True
            )
        sortMenu.addSeparator()
        self.enums['order'] = [temp_menu, create_submenu(
            sortMenu, None, ['Ascending', 'Descending'], check=0,          trigger=parent.populateGallery.emit,
            )]
        
        self.enums['rating'] = create_submenu(
            self.menu, 'Rating', ['Explicit', 'Questionable', 'Safe'], check=2,trigger=parent.populateGallery.emit
            )
        self.enums['type'] = create_submenu(
            self.menu, 'Type', ['All', 'Photo', 'Illus', 'Comic'], check=0,trigger=parent.populateGallery.emit,
            )

        # sortMenu, temp_menu = create_submenu_(
        #     menu, 'Sort by', CONSTANTS['Sort'], 
        #     trigger=parent.populateGallery.emit, check=0
        #     )
        # sortMenu.addSeparator()
        # parent.order = [temp_menu, create_submenu_(
        #     sortMenu, None, CONSTANTS['Order'],
        #     trigger=parent.populateGallery.emit, check=0
        #     )[1]
        #     ]
        # parent.rating = create_submenu_(
        #     menu, 'Rating', CONSTANTS['Rating'],
        #     trigger=parent.populateGallery.emit, check=2
        #     )[1]
        # parent.type = create_submenu_(
        #     menu, 'Type', CONSTANTS['Type'],
        #     trigger=parent.populateGallery.emit
        #     )[1]
        
        self.menu.addSeparator()
        self.menu.addAction(QAction('Copy', self.menu))
        self.menu.addAction(QAction('Delete', self.menu))
                   
        self.menu.addSeparator()
        self.artist = QAction('Find more by artist', self.menu)
        self.menu.addAction(self.artist)
        
        self.menu.addSeparator()
        self.menu.addAction(QAction('Properties', self.menu))

        self.menu.triggered.connect(self.menuPressEvent)
        
    def total(self): return len(self.table.images)

    def update(self, images):
        
        self.table.images = images
        self.table.layoutChanged.emit()
    
    # def pixmap(self):
        
        # for image in self.selectedIndexes()[0]:
        
        # image = (
        #     get_frame(path) 
        #     if path.endswith(('.mp4', '.webm')) else 
        #     QPixmap(path)
        #     )
        # image = image.scaled(
        #     100, 100, 
        #     Qt.AspectRatioMode.KeepAspectRatio, 
        #     transformMode=Qt.TransformationMode.SmoothTransformation
        #     )
        
        # return image
        
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
        
        index = self.currentIndex().data(Qt.ItemDataRole.EditRole)
        
        if index and index[5].pop() == 'Comic':
            
            self.menu.insertAction(self.artist, self.comic)
            
        else: self.menu.removeAction(self.comic)
        
        self.menu.popup(self.mapToGlobal(event))
            
    def menuPressEvent(self, event):

        if isinstance(event, bool): return
        
        match event.text():
            
            case 'Copy': copy_path(self.selectedIndexes())

            case 'Delete':

                self.delete.emit(self.selectedIndexes())

            case 'Read comic':
            
                self.load_comic.emit([self.currentIndex(), 1])

            case 'Find more by artist':

                self.find_artist.emit(self.currentIndex())

            case 'Properties': self.openPersistentEditor()
            
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
                    
            elif key_press == Qt.Key.Key_C: copy_path(self.selectedIndexes())
            
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
                        ), self.selectionModel().select
                        )

                self.selectionModel().select(selection, mode.select)
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
                    ), self.selectionModel().select
                    )
                selection.merge(QItemSelection(
                    self.table.index(row2, col1), 
                    self.table.index(row2, 0)
                    ), self.selectionModel().select
                    )

                self.selectionModel().select(selection, mode.select)
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
                    ), self.selectionModel().select
                    )
                selection.merge(QItemSelection(
                    self.table.index(row1, 0), 
                    self.table.index(row1, 4)
                    ), self.selectionModel().select
                    )

                self.selectionModel().select(selection, mode.select)
                self.selectionModel().setCurrentIndex(new, mode.NoUpdate)

            else: self.setCurrentIndex(new)
        
        elif key_press in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            
            self.load_comic.emit(self.currentIndex())

        else: self.parent().parent().keyPressEvent(event)

    def resizeEvent(self, event):

        self.table.width = int(event.size().width() // COLUMNS)
        self.table.layoutChanged.emit()
 
class Model(QAbstractTableModel):
    
    number_populated = pyqtSignal(int)

    def __init__(self, parent):

        QAbstractTableModel.__init__(self, parent)
        self.wrapper = textwrap.TextWrapper(width=70)
        self.width = int(self.parent().parent().width() // COLUMNS)
        self.images = []
        
    def flags(self, index):
        
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
    
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

        match role:
            
            case Qt.ItemDataRole.DecorationRole: return data[1]

            case Qt.ItemDataRole.EditRole:
                
                data = data
                
                path = {data[1]}
                artist = set(data[2].split())
                tags = set(data[3].split())
                rating = {data[4]}
                stars = {data[5]}
                type = {data[6]}
                site = {data[7]}

                tags.discard('qwd')
                
                return path, tags, artist, stars, rating, type, site

            case Qt.ItemDataRole.ToolTipRole:
                
                art, tag, rat, sta, typ, sit, = data[2:8]
                
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
            
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            
            return True
            
        return False
    
class PaintDelegate(QStyledItemDelegate):
    
    def paint(self, painter, option, index):

        QStyledItemDelegate.paint(self, painter, option, index)

        if index.data(Qt.ItemDataRole.DecorationRole) is not None:

            path = index.data(Qt.ItemDataRole.DecorationRole)
            width = self.parent().table.width
            rect = QPoint(width, width)
                      
            painter.save()
            
            image = (
                get_frame(path) 
                if path.endswith(('.mp4', '.webm')) else 
                QPixmap(path)
                )
            image = image.scaled(
                rect.x() - 10, rect.x() - 10, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                transformMode=Qt.TransformationMode.SmoothTransformation
                )
            
            offset = rect - QPoint(image.size().width(), image.size().height())
            painter.drawPixmap(option.rect.topLeft() + (offset / 2), image)
            painter.restore()