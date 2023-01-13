'''
App for displaying images and video. Currently only works with Manage Database.
'''
from pathlib import Path
from qute.utilities.menus import menuFromDictionary
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtGui import QAction, QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer, QStringListModel, QVariant
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMenu, QMessageBox

from GUI.propertiesView import Properties
from GUI.utils import ROOT, create_submenu_, get_frame, copy_path, copy_to
from GUI.slideshow.imageViewer import imageViewer
from GUI.slideshow.videoPlayer import videoPlayer

MENU = {
    'Fullscreen': None,
    'Sep1': None,
    'Slideshow': None,
    'Sep2': None,
    'Rotate right': None,
    'Rotate left': None,
    'Sep3': None,
    'Copy': None,
    'Delete': None,
    'Sep4': None,
    'Properties': None
    }
SLIDESHOW = [
    ['Pause', 'Play', 0], 
    None, 
    ['Speed - Slow', 'Speed - Medium', 'Speed - Fast', 1]
    ]

class Slideshow(QMainWindow):

    def __init__(self, parent=None, gallery=list(), index=0):

        super(Slideshow, self).__init__()
        self.parent = parent
        self.configure_gui()
        self.create_widgets(gallery)
        self.create_menu()
        self.index = index
        self.move()
        self.showMaximized()
        self.activateWindow()

    def configure_gui(self):
        
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)
        self.setMouseTracking(True)

    def create_widgets(self, gallery):
        
        self.model = Model(self, gallery)

        self.image = imageViewer(self)
        self.video = videoPlayer(self)
        self.stack.addWidget(self.image)
        self.stack.addWidget(self.video)
        
        self.timer = QTimer()
        self.timer.timeout.connect(
            lambda: self.setCursor(Qt.CursorShape.BlankCursor)
            )
        
        # self.video.player.mediaStatusChanged.connect(lambda: self.move(+1))
        self.slideshow = QTimer()
        self.slideshow.timeout.connect(
            lambda: self.move(+1)
            )

    def create_menu(self):

        self.menubar = self.menuBar()
        self.menubar.triggered.connect(self.menuPressEvent)
        
        # File
        file = self.menubar.addMenu('File')
        file.addAction('Copy Image to', lambda: copy_to(self, [self.model.index(self.index)]))#, shortcut='CTRL+SHIFT+C')
        file.addSeparator()
        file.addAction('Exit', self.close)#, shortcut='Ctrl+W')
        
        # View
        view = self.menubar.addMenu('View')
        view.addAction('Fullscreen', self.fullscreen)#, shortcut='F11')
        
        # Help
        help = self.menubar.addMenu('Help')
        
        menu = QMenu(self)

        self.full = QAction(
            'Fullscreen', menu, triggered=self.fullscreen
            )
        menu.addAction(self.full)
        
        menu.addSeparator()
        menu.addAction(QAction(
            'Rotate right', menu, triggered=lambda: self.rotate(+1)
            ))
        menu.addAction(QAction(
            'Rotate left', menu, triggered=lambda: self.rotate(-1)
            ))
        
        menu.addSeparator()
        menu.addAction(QAction(
            'Copy', menu, triggered=copy_to
            ))
        menu.addAction(QAction(
            'Delete', menu, triggered=self.delete
            ))
        
        menu.addSeparator()
        menu.addAction(QAction(
            'Properties', menu, triggered=self.openEditor
            ))

        self.menu = menu

        # self.full = QAction(
        #     'Fullscreen', menu, triggered=self.fullscreen
        #     )
        # menu.addAction(self.full)
        
        # self.fullAction = QAction('Fullscreen', triggered=self.fullscreen)
        
        # MENU['Fullscreen'] = self.fullAction
        # MENU['Slideshow'] = create_submenu_(
        #     self, 'Slideshow', SLIDESHOW, self.playEvent
        #     )[0]
        # MENU['Rotate right'] = lambda: self.rotate(+1)
        # MENU['Rotate left'] = lambda: self.rotate(-1)
        # MENU['Copy'] = lambda: copy_path([self.model.index(self.index)])
        # MENU['Delete'] = self.delete
        
        # if self.parent is not None:
            
        #     MENU['Properties'] = self.openEditor
        
        # self.menu = menuFromDictionary(MENU, self)
        # self.menu.insertSeparator(self.menu.children()[1])
        # self.menu.insertMenu(self.menu.children()[1], MENU['Slideshow'])
        # MENU['Slideshow'].removeAction(MENU['Slideshow'].children()[0])

    def move(self, delta=0):
        
        if self.slideshow.isActive() and self.stack.currentIndex == 1:
            
            print('Video: ', self.stack.currentIndex == 1)
            print('Slideshow: ', self.slideshow.isActive())
            print('EndofMedia: ', self.video.mediaStatus == QMediaPlayer.MediaStatus.EndOfMedia)
            # return 0
            
        if not self.model.gallery:
            self.image.no_image()
            return 0
        
        self.index = (self.index + delta) % len(self.model.gallery)
        path = self.model.index(self.index).data(Qt.ItemDataRole.UserRole)[1]
        self.setWindowTitle(f'{Path(path).name} - Slideshow')

        if path is None: pixmap = QPixmap()
        else:
            if path.endswith('.webp'):
                image = QImage(path)
                path = None
            elif path.endswith(('.gif', '.mp4', '.webm')):
                image = get_frame(path)
            else: print(path)
            
            pixmap = QPixmap(image).scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatio, 
                transformMode=Qt.TransformationMode.SmoothTransformation
                )

        self.image.update(pixmap)
        self.stack.setCurrentIndex(0)
        self.video.update(path)
        
        if self.slideshow.isActive(): self.slideshow.start()
    
    def fullscreen(self):

        if self.isFullScreen():

            self.timer.stop()
            self.image.setStyleSheet('background: ')
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.full.setText('Fullscreen')
            self.menubar.show()
            self.show()

        else:

            self.image.setStyleSheet('background: black')
            self.setCursor(Qt.CursorShape.BlankCursor)
            self.full.setText('Exit fullscreen')
            self.menubar.hide()
            self.showFullScreen()

    def rotate(self, sign):

        path = self.model.index(self.index).data(Qt.UserRole)[1]

        if path.endswith('.webp'):
            self.image.rotate(path, sign)
        
        else:
            self.video.rotate(path, sign)
            
        self.move()
                
    def delete(self):
        
        if self.stack.currentIndex():
            self.video.update(None)
        else: self.image.update(None)
        
        index = [self.model.index(self.index)]

        if self.parent:
            if self.parent.delete_records(index):
                del self.model.gallery[self.index]
                self.model.layoutChanged.emit()
                self.move()
        else:
            message = QMessageBox.question(
                None, 'Delete', 
                'Are you sure you want to delete this?',
                QMessageBox.Yes | QMessageBox.No
                )
            
            if message == QMessageBox.Yes:
                
                (ROOT / index[0]).unlink(True)
                del self.model.gallery[self.index]
                self.model.layoutChanged.emit()
                self.move()
        
    def openEditor(self):

        index = self.model.index(self.index)
        
        Properties(self.parent, [index.data(Qt.ItemDataRole.EditRole)])
        
    def playEvent(self, event):
        
        if event.text() == 'Pause': 

            self.slideshow.stop()
            return
        
        match MENU['Slideshow'].children()[6].checkedAction().text():
            
            case 'Speed - Slow': self.slideshow.start(30000)
                
            case 'Speed - Medium': self.slideshow.start(15000)
                
            case 'Speed - Fast': self.slideshow.start(5000)
          
    def contextMenuEvent(self, event):
        
        self.menu.popup(event.globalPos())

    def menuPressEvent(self, event=None):

        match event.text():
            
            case 'Copy Image to':
                
                copy_to(self, [self.model.index(self.index)])

            case 'Exit': self.close()

    def keyPressEvent(self, event):

        key_press = event.key()
        video = self.stack.currentIndex()
        alt = event.modifiers() == Qt.KeyboardModifier.AltModifier
        ctrl = event.modifiers() == Qt.KeyboardModifier.ControlModifier
        shift = event.modifiers() == Qt.KeyboardModifier.ShiftModifier
        
        match event.key():
            
            case (Qt.Key.Key_Right|Qt.Key.Key_Left):
                
                self.move(1 if key_press == Qt.Key.Key_Right else -1)
                
            case Qt.Key.Key_Delete: self.delete()
            
            case Qt.Key.Key_F11: self.fullscreen()

            case Qt.Key.Key_Escape:
                
                if self.isFullScreen(): self.fullscreen()
                
                else: self.close()
            
        if video:
            
            match event.key():
                
                case (Qt.Key.Key_Home|Qt.Key.Key_End):
                    
                    if key_press == Qt.Key.Key_Home: self.video.position(0)
                    else: self.video.position(100)
                    
                case (Qt.Key.Key_Period|Qt.Key.Key_Comma):

                    sign = 1 if key_press == Qt.Key.Key_Period else -1
                    if ctrl: self.video.position(sign * 50)
                    else: self.video.position(sign * 5000)
                
                case (Qt.Key.Key_Up|Qt.Key.Key_Down):

                    sign = 1 if key_press == Qt.Key.Key_Up else -1
                    if ctrl: self.video.volume(sign * .1)
                    else: self.video.volume(sign * .10)
                
                case Qt.Key.Key_Space: self.video.pause()
                
                case Qt.Key.Key_M: self.video.mute()      
            
        if alt:
                    
            if key_press in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                
                self.openEditor()
            
            if key_press == Qt.Key.Key_F4: self.close()
                    
        elif ctrl:
            
            if shift and key_press == Qt.Key.Key_C:
                
                copy_to(self, [self.model.index(self.index)])
            
            elif key_press == Qt.Key.Key_C: self.copy_path()
            
            elif key_press == Qt.Key.Key_W: self.close()
              
    def mouseMoveEvent(self, event):
        
        if self.isFullScreen():

            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.timer.start(1500)
        
    def mousePressEvent(self, event):
        
        if event.button() == Qt.MouseButton.LeftButton:
            
            if event.pos().x() > (self.width() * .5): self.move(+1)
            elif event.pos().x() < (self.width() * .5): self.move(-1)
    
    def closeEvent(self, event):
        
        self.slideshow.stop()
        self.video.stop()

class Model(QStringListModel):

    def __init__(self, parent, gallery):

        QStringListModel.__init__(self, parent)
        self.gallery = gallery
    
    def rowCount(self, parent=None): return len(self.gallery)

    def data(self, index, role):

        index = index.row()

        match role:
            
            case Qt.ItemDataRole.EditRole:
                
                data = self.gallery[index][1:8]
                
                path = {data[0]}
                artist = set(data[1].split())
                tags = set(data[2].split())
                rating = {data[3]}
                stars = {data[4]}
                type = {data[5]}
                site = {data[6]}

                tags.discard('qwd')
                
                return path, tags, artist, stars, rating, type, site
            
            case Qt.ItemDataRole.UserRole: return self.gallery[index]
            
            case 300: return index
            
        return QVariant()