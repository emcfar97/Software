import textwrap
from PyQt6.QtGui import QImage, QAction#, QDrag
from PyQt6.QtWidgets import QApplication, QTableView, QAbstractItemView, QMenu, QStyledItemDelegate
from PyQt6.QtCore import QAbstractTableModel, QItemSelection, QVariant, QModelIndex, Qt, QPoint, QSize, pyqtSignal#, QMimeData
from PyQt6.QtSql import QSqlRelationalTableModel, QSqlRelationalDelegate, QSqlTableModel

from GUI.utils import COLUMNS, BATCH, CONSTANTS, MODEL, get_frame, get_path, create_submenu, create_submenu_, copy_path
from GUI.propertiesView import Properties

ORDER = {'Ascending':'ASC', 'Descending':'DESC'}

class Gallery(QTableView):
    
    selection = pyqtSignal(QItemSelection, QItemSelection)
    order_updated = pyqtSignal(dict)
    find_artist = pyqtSignal(QModelIndex)
    load_comic = pyqtSignal(list)
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
        
        self.menu = QMenu(self)
        self.comic = QAction('Read comic', self.menu)
        
        temp_menu, sortMenu = create_submenu(
            self.menu, 'Sort by', CONSTANTS['Sort'], check=0, get_menu=True
            )
        sortMenu.addSeparator()
        self.order = [temp_menu, create_submenu(
            sortMenu, None, CONSTANTS['Order'], check=0
            )]
        self.rating = create_submenu(
            self.menu, 'Rating', CONSTANTS['Rating'], check=3
            )
        self.type = create_submenu(
            self.menu, 'Type', CONSTANTS['Type'], check=0
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
        
    def update_gallery(self, images):
        
        self.table.images = images
        self.table.layoutChanged.emit()
    
    def update_order(self, mode=0):
        
        order = self.order[1].checkedAction().text()
        column = self.order[0].checkedAction().text()
        
        column = 'RAND()' if column == 'Random' else column
        column = 'date_used' if column == 'Date' else column
        
        data = {
            'sort': f'ORDER BY {column} {ORDER[order]}',
            'column': {
                'rating': self.rating.checkedAction().text(),
                'type': self.type.checkedAction().text()
                }
            }
        
        if mode: return data
        
        self.order_updated.emit(data)
        
    def total(self): return len(self.table.images)
        
    def openPersistentEditor(self):
        
        indexes = self.selectedIndexes()
        
        if indexes:
            
            Properties(self.parent().parent(), self.table, indexes)
    
    def selectionChanged(self, select, deselect):
        
        self.selection.emit(select, deselect)

    def mouseDoubleClickEvent(self, event):

        self.load_comic.emit([self.currentIndex(), 0])
      
    def contextMenuEvent(self, event):
        
        index = self.currentIndex().data(Qt.ItemDataRole.EditRole)
        
        if index and index[6].pop() == 'Comic':
            
            self.menu.insertAction(self.artist, self.comic)
            
        else: self.menu.removeAction(self.comic)
        
        self.menu.popup(self.mapToGlobal(event))
            
    def menuPressEvent(self, event):

        if isinstance(event, bool): return
        
        action = event.text()
        
        if action in CONSTANTS['Sort'] or action in CONSTANTS['Order'] or action in CONSTANTS['Rating'] or action in CONSTANTS['Type']:
            
            self.update_order()
            
        match action:
            
            case 'Copy': copy_path(self.selectedIndexes())

            case 'Delete':

                self.delete.emit(self.selectedIndexes())

            case 'Read comic':
            
                self.load_comic.emit([self.currentIndex(), 1])

            case 'Find more by artist':

                self.find_artist.emit(self.currentIndex())

            case 'Properties': self.openPersistentEditor()
                
    def mousePressEvent(self, event):
        
        button_press = event.button()
        
        if button_press in (Qt.MouseButton.XButton1, Qt.MouseButton.XButton2):
        
            self.parent().parent().mousePressEvent(event)
        
        else:
            
            return super().mousePressEvent(event)
           
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
                        ), self.selectionModel().SelectionFlag.Select
                        )

                self.selectionModel().select(selection, mode.SelectionFlag.Select)
                self.selectionModel().setCurrentIndex(new, mode.SelectionFlag.NoUpdate)

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
                    ), self.selectionModel().SelectionFlag.Select
                    )
                selection.merge(QItemSelection(
                    self.table.index(row2, col1), 
                    self.table.index(row2, 0)
                    ), self.selectionModel().SelectionFlag.Select
                    )

                self.selectionModel().select(selection, mode.SelectionFlag.Select)
                self.selectionModel().setCurrentIndex(new, mode.SelectionFlag.NoUpdate)

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
                    ), self.selectionModel().SelectionFlag.Select
                    )
                selection.merge(QItemSelection(
                    self.table.index(row1, 0), 
                    self.table.index(row1, 4)
                    ), self.selectionModel().SelectionFlag.Select
                    )

                self.selectionModel().select(selection, mode.SelectionFlag.Select)
                self.selectionModel().setCurrentIndex(new, mode.SelectionFlag.NoUpdate)

            else: self.setCurrentIndex(new)
        
        elif key_press in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            
            self.load_comic.emit([self.currentIndex(), 0])

        else: self.parent().parent().keyPressEvent(event)

    def resizeEvent(self, event):

        self.table.width = int(event.size().width() // COLUMNS)
        self.table.layoutChanged.emit()
 
class Model(QSqlRelationalTableModel):
    
    number_populated = pyqtSignal(int)

    def __init__(self, parent):

        # QSqlRelationalTableModel.__init__(self, parent)
        QAbstractTableModel.__init__(self, parent)
        self.wrapper = textwrap.TextWrapper(width=70)
        self.width = int(self.parent().parent().width() // COLUMNS)
        self.images = []
        # self.setTable('imagedata')
        # self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        
    def flags(self, index):
        
        ind = (index.row() * 5) + index.column()

        if ind >= len(self.images) or not any(self.images[ind]):
            
            return Qt.ItemFlag.ItemIsEnabled

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
    
    def rowCount(self, parent=None):

        rows, cols = divmod(len(self.images), self.columnCount())

        return rows + bool(cols)

    def columnCount(self, parent=None): return COLUMNS
    
    def canFetchMore(self, index):
        
        if index.isValid():
            
            return False

        mysql = self.parent().parent().parent().mysql
        
        return mysql.rowcount() > len(self.images)

    def fetchMore(self, index, fetch=BATCH):

        mysql = self.parent().parent().parent().mysql
        start = len(self.images)
        remainder = mysql.rowcount() - start
        items_to_fetch = min(fetch, remainder)

        if items_to_fetch <= 0:
            
            return
        
        self.beginInsertRows(QModelIndex(), start, start + items_to_fetch)

        self.images += mysql.CURSOR.fetchmany(fetch)

        self.endInsertRows()
        
        self.number_populated.emit(items_to_fetch)
    
    def data(self, index, role):
        
        ind = (index.row() * 5) + index.column()

        if ind >= len(self.images) or not any(self.images[ind]):

            return QVariant()
        
        data = self.images[ind]

        match role:
            
            case Qt.ItemDataRole.DecorationRole: return get_path(data[1])

            case Qt.ItemDataRole.EditRole:
                
                rowid = {data[0]}
                path = {data[1]}
                artist = set(data[2].split())
                tags = set(data[3].split())
                rating = {data[4]}
                stars = {data[5]}
                type = {data[6]}
                site = {data[7]}
                date_used = {data[8]}
                hash = {data[9].hex()} 
                href = {data[10]}
                src = {data[11]}

                tags.discard('qwd')
                
                return rowid, path, tags, artist, stars, rating, type, site, date_used, hash, href, src

            case Qt.ItemDataRole.ToolTipRole:
                
                art, tag, rat, sta, typ, sit, = data[2:8]
            
                tags = self.wrapper.wrap(
                    ' '.join(sorted(tag.replace(' qwd ', ' ').split()))
                    )
                tooltip = self.wrapper.wrap(
                    f'Artist: {art.strip()} Rating: {rat.lower()} Stars: {sta} Type: {typ.lower()} Site: {sit}'
                    )
                
                return '\n'.join(tags + tooltip)

            case Qt.ItemDataRole.SizeHintRole:
                
                return QSize(self.width, self.width)
            
            case Qt.ItemDataRole.UserRole: return data
            
            case Qt.ItemDataRole.FontRole: return ind
        
        return QVariant()
    
    def setData(self, index, values, role=Qt.ItemDataRole.EditRole):
        
        if role == Qt.ItemDataRole.EditRole and index.isValid():
            
            values = {MODEL[key]:val for key, val in values.items()}
            try: current = self.images[index.data(Qt.ItemDataRole.FontRole)]
            except TypeError: return
            new = tuple()
            
            for num, value in enumerate(current):
                
                if num not in values: new += (value,); continue
                
                vals = values[num]
                
                if isinstance(vals, tuple):
                    
                    for val in vals[0]: value += f' {val} '
                    
                    for val in vals[1]: value = value.replace(f' {val} ', ' ')
                
                else: value = vals
                        
                new += (value,)
                    
            self.images[index.data(Qt.ItemDataRole.FontRole)] = new
            self.dataChanged.emit(index, index)
            
            return True
            
        return False
    
class PaintDelegate(QStyledItemDelegate):
    
    def paint(self, painter, option, index, margin=10):

        QStyledItemDelegate.paint(self, painter, option, index)
        path = index.data(Qt.ItemDataRole.DecorationRole)
        
        if path is not None:

            width = self.parent().table.width
            rect = QPoint(width, width)
                      
            painter.save()

            image = (
                get_frame(str(path)) 
                if path.suffix == '.webm' else 
                QImage(str(path))
                )
            image = image.scaled(
                rect.x() - margin, rect.x() - margin, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                transformMode=Qt.TransformationMode.SmoothTransformation
                )
            
            offset = rect - QPoint(image.size().width(), image.size().height())
            painter.drawImage(option.rect.topLeft() + (offset / 2), image)
            painter.restore()