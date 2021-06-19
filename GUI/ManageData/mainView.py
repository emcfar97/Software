from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QMessageBox, QStatusBar
from GUI import galleryView, previewView, slideshowView

class ManageData(QMainWindow):
            
    TYPE = {
        'Photograph': 'エラティカ ニ',
        'Illustration': 'エラティカ 三',
        'Comic': 'エラティカ 四',
        1: 'エラティカ ニ',
        2: 'エラティカ 三',
        3: 'エラティカ 四'
        }

    def __init__(self, parent):
        
        super(ManageData, self).__init__()
        self.setWindowTitle('Manage Data')
        self.parent = parent
        self.configure_gui()
        self.create_menu()
        self.create_widgets()
        self.showMaximized()
        self.gallery.populate()

    def configure_gui(self):
        
        self.center = QWidget(self)
        self.layout = QHBoxLayout()

        self.center.setLayout(self.layout)
        self.setCentralWidget(self.center)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        resolution = Qapp.desktop().screenGeometry()
        width, height = resolution.width(),  resolution.height()
        self.setGeometry(0, 0, width, height)

    def create_menu(self):
        
        self.menubar = self.menuBar()
        
        # file = self.menubar.addMenu('File')
        
    def create_widgets(self):
            
        self.windows = set()
        self.gallery = Gallery(self)
        self.preview = Preview(self, 'white')
        self.slideshow = Slideshow(self)
        
        self.layout.addWidget(self.gallery)
        self.layout.addWidget(self.preview)
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)
    
    def start_slideshow(self, index=None):
        
        view = self.gallery.images
        if not view.table.images: return

        selection = QItemSelection(
            view.table.index(0, 0),
            view.table.index(
                view.table.rowCount() - 2, 
                view.table.columnCount() - 1
                )
            )
        selection.merge(QItemSelection(
                view.table.index(
                    view.table.rowCount() - 1, 0
                    ),
                view.table.index(
                    view.table.rowCount() - 1, 
                    (view.total() - 1) % view.table.columnCount()
                    )),
                view.selectionModel().Select
                )

        self.slideshow.gallery = selection.indexes()
        index = index if index else view.currentIndex()
        self.slideshow.index = sum(index.data(100))
        
        self.slideshow.move(0)
        if self.slideshow.isHidden():
            self.slideshow.showMaximized()
        self.slideshow.activateWindow()

    def update_records(self, gallery, **kwargs):
                
        parameters = []
        query = set(self.gallery.query)
        change = set(i.lower() for i in kwargs)
        random = 'RANDOM()' in self.gallery.get_order()

        for key, vals in kwargs.items():
            
            key = key.lower()
            
            if isinstance(vals, tuple):
                
                for val in vals[0]:

                    parameters.append(f'{key}=CONCAT({key}, " {val} ")')
                
                for val in vals[1]:

                    parameters.append(f'{key}=REPLACE({key}, " {val} ", " ")')
                
            else: parameters.append(f'{key}={vals}')

        # if 'Path' in kwargs:

            # for path, in gallery:
            #     path = ROOT / path

            #     try: path.rename(path.with_name())
            #     except (
            #         FileExistsError, 
            #         FileNotFoundError, 
            #         PermissionError
            #         ) as error:
            #         message = QMessageBox.question(
            #             None, type(error).__name__, str(error), 
            #             QMessageBox.Ignore | QMessageBox.Ok
            #             )
            #         if message == QMessageBox.Ok: return 0

        if 'Type' in kwargs:
            
            for path, in gallery:
                path = ROOT / path
                dropbox = path.parent.parent
                new = self.TYPE[kwargs['Type']]

                try: path.rename(dropbox / new / path.name)
                except (
                    FileExistsError, 
                    FileNotFoundError, 
                    PermissionError
                    ) as error:
                    message = QMessageBox.question(
                        None, type(error).__name__, str(error), 
                        QMessageBox.Ignore | QMessageBox.Ok
                        )
                    if message == QMessageBox.Ok: return 0
        
        busy = MYSQL.execute(
            MODIFY.format(', '.join(parameters)), gallery, many=1, commit=1
            )
        if busy:
            QMessageBox.information(
                None, 'The database is busy', 
                'There is a transaction currently taking place',
                QMessageBox.Ok
                )
            return 0

        if not random: self.gallery.populate()
        # else: self.gallery.images.clearSelection()
        if not self.slideshow.isHidden(): self.slideshow.move()   

        return 1
    
    def delete_records(self, gallery, update=False):
                
        message = QMessageBox.question(
            None, 'Delete', 
            'Are you sure you want to delete this?',
            QMessageBox.Yes | QMessageBox.No
            )
        
        if message == QMessageBox.Yes:
            
            paths = [
                (data[0].pop(),) for index in gallery 
                if (data := index.data(Qt.UserRole))
                ]
            
            # If MYSQL returns an error
            if MYSQL.execute(DELETE, paths, many=1):
                QMessageBox.information(
                    None, 'The database is busy', 
                    'There is a transaction currently taking place',
                    QMessageBox.Ok
                    )
                MYSQL.rollback()
                return 0

            for path, in paths: (ROOT / path).unlink(True)
            MYSQL.commit()
            
            if update:
                self.gallery.images.update([])
                self.gallery.populate()
            # else:
            #     table = self.gallery.images.table
            #     for index in gallery:
            #         table.images.remove(index)
            #     table.layoutChanged.emit()
            if not self.slideshow.isHidden(): self.slideshow.move()   

            return 1
    
    def menuPressEvent(self, action=None):

        print(action)

    def keyPressEvent(self, event):

        key_press = event.key()

        if key_press in (Qt.Key_Return, Qt.Key_Enter):
            
            self.start_slideshow()

        elif key_press == Qt.Key_Delete:
            
            gallery = self.gallery.images.selectedIndexes() 
            self.delete_records(gallery)
                        
        elif key_press == Qt.Key_Escape: self.close()
    
        else: self.parent.keyPressEvent(event)

    def closeEvent(self, event):
        
        self.windows.clear()
        self.slideshow.close()
        try: self.parent.windows[self.windowTitle()].remove(self)
        except: pass
        if not self.parent.is_empty(): self.parent.show()