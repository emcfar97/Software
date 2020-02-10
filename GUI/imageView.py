import textwrap
from . import *
from .propertiesView import *
from PyQt5.QtCore import QAbstractTableModel, QVariant, QObject, QModelIndex, QItemSelectionModel
from PyQt5.QtWidgets import QApplication, QAbstractScrollArea, QAbstractItemView, QMenu, QAction, QActionGroup
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

def open_database():
     
    datab = QSqlDatabase.addDatabase('QODBC')
    datab.setUserName('root')
    datab.setPassword('SchooL1@')
    datab.setDatabaseName('userData')
    datab.setHostName(
        '192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
        )
    datab.open()
     
    return datab

class imageView(QTableView):

    def __init__(self, parent):

        super().__init__(parent)
        self.menu = self.create_menu()
        self.properties = Properties(self.parent().parent())
        self.table = Model(self, parent.width())   
        self.setModel(self.table)
        self.horizontalHeader().hide()      
        self.verticalHeader().hide() 

        self.doubleClicked.connect(self.open_slideshow)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuEvent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContentsOnFirstShow
            )
        
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
        
        self.parent().status.modify(
            self.total(), len(self.selectedIndexes())
            )

    def open_slideshow(self, index):

        parent = self.parent().parent()

        if parent.windowTitle() == 'Manage Data' and not parent.slideshow:
            
            parent.slideshow = True
            parent.open_slideshow(
                (index.row() * 5) + index.column()
                )
    
    def create_menu(self):
        
        menu = QMenu(self)
        parent = self.parent()

        sortMenu = QMenu('Sort by', menu)
        order = [QActionGroup(sortMenu), QActionGroup(sortMenu)]
        for i in ['Rowid', 'Path', 'Artist', 'Stars', 'Hash', 'Random']:
            action = QAction(i, sortMenu, checkable=True)
            if i == 'Rowid': action.setChecked(True)
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
            parent.ribbon.order = order

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
            parent.ribbon.rating = rating
        
        typeMenu = QMenu('Type', menu)
        type_ = QActionGroup(typeMenu)
        for i in ['All', 'Photo', 'Illus']:
            action = QAction(i, typeMenu, checkable=True)
            type_.triggered.connect(parent.populate)
            type_.addAction(action)
            typeMenu.addAction(action)
        else: 
            action.setChecked(True)
            menu.addMenu(typeMenu)
            type_.setExclusive(True)
            parent.ribbon.type = type_

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
                triggered=lambda: self.properties.display(self.selectedIndexes()))
                )
        except AttributeError: pass

        return menu

    def contextMenuEvent(self, sender): self.menu.popup(sender)
    
    def copy_path(self):

        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)

        for index in self.selectedIndexes():
            
            cb.setText(index.data(Qt.UserRole), mode=cb.Clipboard)

class Model(QAbstractTableModel):

    def __init__(self, parent, width):

        QAbstractTableModel.__init__(self, parent)
        self.wrapper = textwrap.TextWrapper(width=70)
        self.size = int(width * .1888)
        self.images = []
        self.rowsLoaded = 0
        self.rows = 0

    def flags(self, index):
        
        return (
            Qt.ItemIsEnabled | Qt.ItemIsSelectable# | Qt.ItemIsUserCheckable
            )
    
    def rowCount(self, parent): return self.rows    

    def columnCount(self, parent): return 5

    def data(self, index, role, type=0):

        ind = (index.row() * 5) + index.column()

        if not index.isValid() or ind > len(self.images): return QVariant()

        if role == Qt.DecorationRole:
    
            path = self.images[ind][0]
            if path.endswith(('.mp4', '.webm')):
                
                success, image = VideoCapture(path).read()
                image = QImage(
                    image.data, image.shape[1], image.shape[0], 
                    QImage.Format_RGB888
                    ).rgbSwapped()
                
            else: image = QImage(path)

            image = image.scaled(
                self.size, self.size, Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
            
            return QPixmap.fromImage(image)

        elif role == Qt.ToolTipRole:
            
            tag, art, sta, rat, typ, = self.images[ind][1:]
            typ = 'Illustration' if typ else 'Photograph'
            tags = self.wrapper.wrap(f'{tag}'.strip())
            rest = self.wrapper.wrap(
                f'Artist: {art} Rating: {rat} Stars: {sta} {typ}'
                )
            return '\n'.join(tags + rest)

        elif role == 1000: 
            
            data = self.images[ind]
            path = {data[0]}
            tags = {data[1]} if data[1] else set()
            artist = {data[2]} if data[2] else set()
            stars = {data[3]}
            rating = {data[4]}
            type = {data[5]}
            
            return path, tags, artist, stars, rating, type

        elif role == Qt.UserRole: return QVariant(self.images[ind][0])

        elif role == Qt.SizeHintRole: return QSize(self.size, self.size)

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
        self.size = int(width * .188)
        self.images = []
        self.rowsLoaded = 0

    def flags(self, index):

        return (
            Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
            )
    
    def rowCount(self, parent): return len(self.images) // 5     

    def columnCount(self, parent): return 5

    def data(self, index, role):

        ind = (index.row() * 5) + index.column()

        if not index.isValid() or ind > len(self.images): return QVariant()

        if role == Qt.DecorationRole:

            path = self.images[ind][0]
            if path.endswith(('.mp4', '.webm')):
                
                success, image = VideoCapture(path).read()
                image = QImage(
                    image.data, image.shape[1], image.shape[0], 
                    QImage.Format_RGB888
                    ).rgbSwapped()
                
            else: image = QImage(path)

            image = image.scaled(
                self.size, self.size, Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
            
            return QPixmap.fromImage(image)

        elif role == Qt.ToolTipRole:
            
            tag, art, rat, sta, = self.images[ind][1:]
            tags = self.wrapper.wrap(f'{tag.strip()}')
            rest = self.wrapper.wrap(
                f'Artist: {art}Rating: {rat} Stars: {sta}'
                )
            return '\n'.join(tags + rest)

        elif role == Qt.UserRole: return QVariant(self.images[ind][0])

        elif role == Qt.SizeHintRole: return QSize(self.size, self.size)

        return QVariant()
   
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

class Select(QLabel):

    def __init__(self, image, size):
        
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)

        self.image = image
        
        if image.endswith(('.mp4', '.webm')):
            
            success, image = VideoCapture(image).read()
            pixmap = QImage(
                image, size, size, 
                image.shape[1] * 3, 
                QImage.Format_RGB888
                )
            
        else:
        
            pixmap = QPixmap(image).scaled(
                size, size, Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
        
        self.setPixmap(pixmap)
