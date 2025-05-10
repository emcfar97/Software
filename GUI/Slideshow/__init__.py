'''
App for displaying images and video. Currently only works with Manage Database.
'''
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QTimer, QStringListModel, QVariant
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMenu, QMessageBox

from GUI.propertiesView import Properties
from GUI.utils import ROOT, MODEL, create_submenu, get_path, copy_path, copy_to, open_file
from GUI.slideshow.imageViewer import imageViewer
from GUI.slideshow.videoPlayer import videoPlayer
from GUI.slideshow.controls import Controls

SLIDESHOW = [
    ['Pause', 'Play'], 
    ['Speed - Slow', 'Speed - Medium', 'Speed - Fast']
    ]

class Slideshow(QMainWindow):

    def __init__(self, parent=None, gallery=list(), index=0):

        super(Slideshow, self).__init__()
        self.parent = parent
        self.index = index
        self.configure_gui()
        self.create_widgets(gallery)
        self.create_menu()
        self.showMaximized()
        self.move()
        self.activateWindow()

    def configure_gui(self):
        
        self.setMinimumSize(
            int(self.parent.width() * .25),
            int(self.parent.height() * .20)
            )
        
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)
        self.setMouseTracking(True)

    def create_widgets(self, gallery):
        
        self.model = Model(self, gallery)

        self.image = imageViewer(self)
        self.video = videoPlayer(self)
        # self.controls = Controls(self)
        self.stack.addWidget(self.image)
        self.stack.addWidget(self.video)
        # self.stack.addWidget(self. controls)
        
        self.timer = QTimer()
        self.timer.timeout.connect(
            lambda: self.setCursor(Qt.CursorShape.BlankCursor)
            )
        
        # self.video.player.mediaStatusChanged.connect(lambda: self.move(+1))
        self.video.playing.connect(lambda: self.stack.setCurrentIndex(1))
        self.slideshow = QTimer()
        self.slideshow.timeout.connect(lambda: self.move(+1))

    def create_menu(self):
        
        # menubar
        self.menubar = self.menuBar()
        self.menubar.triggered.connect(self.menuPressEvent)
        
        # File
        file = self.menubar.addMenu('File')
        file.addAction(
            'Copy Image to', 'CTRL+SHIFT+C', 
            lambda: copy_to(self, [self.model.index(self.index)])
            )
        file.addSeparator()
        file.addAction('Exit', 'Ctrl+W', self.close)
        
        # View
        view = self.menubar.addMenu('View')
        view.addAction('Fullscreen', 'F11', self.fullscreen)
        
        # Help
        help = self.menubar.addMenu('Help')
        
        # context menu
        self.menu = QMenu()
        
        self.fullAction = QAction('Fullscreen', triggered=self.fullscreen)
        self.menu.addAction(self.fullAction)
        self.menu.addSeparator()
        
        self.slideshow_menu = QMenu('Slideshow', self.menu)
        create_submenu(
            self.slideshow_menu, None, SLIDESHOW[0], 
            self.playEvent, check=0, get_menu=True
            )
        self.slideshow_menu.addSeparator()
        create_submenu(
            self.slideshow_menu, None, SLIDESHOW[1], 
            self.playEvent, check=1, get_menu=True
            )
        self.menu.addMenu(self.slideshow_menu)
        self.menu.addSeparator()
        
        self.menu.addAction(QAction(
            'Rotate right', self.menu, triggered=lambda: self.rotate(+1)
            ))
        self.menu.addAction(QAction(
            'Rotate left', self.menu, triggered=lambda: self.rotate(-1)
            ))
        self.menu.addSeparator()
        
        self.menu.addAction(QAction(
            'Copy', self.menu, triggered=copy_to
            ))
        self.menu.addAction(QAction(
            'Delete', self.menu, triggered=self.delete
            ))
        self.menu.addSeparator()
        
        self.menu.addAction(QAction(
            'Open file location', self.menu, triggered=lambda: open_file(self.model.index(self.index))
            ))
        self.menu.addSeparator()
        
        self.menu.addAction(QAction(
            'Properties', self.menu, triggered=self.openEditor
            ))

    def move(self, delta=0):
        
        if self.slideshow.isActive() and self.stack.currentIndex == 1:
            
            print('Video: ', self.stack.currentIndex == 1)
            print('Slideshow: ', self.slideshow.isActive())
            print('EndofMedia: ', self.video.mediaStatus == QMediaPlayer.MediaStatus.EndOfMedia)
            # return 0
            
        if not self.model.gallery:
            
            self.image.no_image()
            return 0
        
        # self.video.update(None)
        
        self.index = (self.index + delta) % len(self.model.gallery)
        path = self.model.index(self.index).data(Qt.ItemDataRole.DecorationRole)
        self.setWindowTitle(f'{path.name} - Slideshow')
        
        self.image.update(str(path))
        self.stack.setCurrentIndex(0)
        
        if path.suffix == '.webm': self.video.update(str(path))
        elif path.suffix == '.webp': self.video.update(None)
    
    def fullscreen(self):

        if self.isFullScreen():

            self.timer.stop()
            self.image.setStyleSheet('background: ')
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.fullAction.setText('Fullscreen')
            self.showMaximized()
            self.menubar.show()

        else:

            self.image.setStyleSheet('background: black')
            self.setCursor(Qt.CursorShape.BlankCursor)
            self.fullAction.setText('Exit fullscreen')
            self.menubar.hide()
            self.showFullScreen()

    def rotate(self, sign):

        path = self.model.index(self.index).data(Qt.ItemDataRole.DecorationRole)

        if path.suffix == '.webp': self.image.rotate(str(path), sign)
        
        elif path.suffix == '.webm': self.video.rotate(str(path), sign)
            
        self.move()
                
    def delete(self):
        
        index = [self.model.index(self.index)]

        if self.parent:
        
            if self.stack.currentIndex():
                
                self.video.update(None)
                
            else: self.image.update(None)
            
            if self.parent.delete_records(index):
                
                del self.model.gallery[self.index]
                self.model.layoutChanged.emit()
                self.move()
                
        else:
            
            message = QMessageBox.question(
                None, 'Delete', 
                'Are you sure you want to delete this?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
            
            if message == QMessageBox.StandardButton.Yes:
                
                del self.model.gallery[self.index]
                self.model.layoutChanged.emit()
                self.move()
                (ROOT / index[0]).unlink(True)
        
    def openEditor(self):

        Properties(self.parent, self.model, [self.model.index(self.index)])
        
    def playEvent(self, event):
        
        if event.text() == 'Pause': 

            self.slideshow.stop()
            return
        
        match self.slideshow_menu.children()[6].text():
            
            case 'Speed - Slow': self.slideshow.start(45000)
                
            case 'Speed - Medium': self.slideshow.start(15000)
                
            case 'Speed - Fast': self.slideshow.start(5000)
            
        self.slideshow_menu.children()[4].setChecked(True)
          
    def contextMenuEvent(self, event):
        
        self.menu.popup(event.globalPos())

    def menuPressEvent(self, event=None):

        match event.text():

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
                    
                    self.video.set_position(0)
                    
                case (Qt.Key.Key_Period|Qt.Key.Key_Comma):

                    sign = 1 if key_press == Qt.Key.Key_Period else -1
                    if ctrl: self.video.set_position(sign * 50)
                    else: self.video.set_position(sign * 5000)
                
                case (Qt.Key.Key_Up|Qt.Key.Key_Down|Qt.Key.Key_W|Qt.Key.Key_S):

                    sign = 1 if key_press in (Qt.Key.Key_Up, Qt.Key.Key_W) else -1
                    if ctrl: self.video.set_volume(sign * .1)
                    else: self.video.set_volume(sign * .10)
                
                case Qt.Key.Key_Space: self.video.pause()
                
                case Qt.Key.Key_M: self.video.mute()      
            
        if alt:
                    
            if key_press in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                
                self.openEditor()
            
            if key_press == Qt.Key.Key_F4: self.close()
                    
        elif ctrl:
            
            if shift and key_press == Qt.Key.Key_C:
                
                copy_to(self, [self.model.index(self.index)])
            
            elif key_press == Qt.Key.Key_C: 
                
                copy_path([self.model.index(self.index)])
            
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
        self.video.update(None)

class Model(QStringListModel):

    def __init__(self, parent, gallery):

        QStringListModel.__init__(self, parent)
        self.gallery = gallery
    
    def flags(self, index):
        
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
    
    def rowCount(self, parent=None): return len(self.gallery)

    def data(self, index, role):

        index = index.row()
        data = self.gallery[index]
        
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
            
            case Qt.ItemDataRole.UserRole: return self.gallery[index]
            
            case Qt.ItemDataRole.FontRole: return index
            
        return QVariant()

    def setData(self, index, values, role=Qt.ItemDataRole.EditRole):
        
        if role == Qt.ItemDataRole.EditRole and index.isValid():
            
            values = {MODEL[key]:val for key, val in values.items()}
            current = self.gallery[index.data(Qt.ItemDataRole.FontRole)]
            new = tuple()
            
            for num, value in enumerate(current):
                
                if num not in values: new += (value,); continue
                
                vals = values[num]
                
                if isinstance(vals, tuple):
                    
                    for val in vals[0]: value += f' {val} '
                    
                    for val in vals[1]: value = value.replace(f' {val} ', ' ')
                
                else: value = vals
                        
                new += (value,)
                    
            self.gallery[index.data(Qt.ItemDataRole.FontRole)] = new
            self.dataChanged.emit(index, index)

            return True
            
        return False