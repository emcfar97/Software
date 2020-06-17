from os import remove
from subprocess import Popen

from GUI import galleryView, previewView, sliderView, mainView, trainView
from GUI import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QMessageBox, QDesktopWidget, Qt
from GUI import CURSOR, DATAB, MODIFY, DELETE, NEZUMI, sql

class App(QMainWindow):
    
    def __init__(self):
        
        super().__init__()
        self.setWindowTitle('Custom GUI')
        self.desktop = QDesktopWidget()
        self.configure_gui()
        self.create_widgets()
        self.show()
        
    def configure_gui(self):
        
        resolution = Qapp.desktop().screenGeometry()
        width, height = resolution.width(),  resolution.height()

        self.setGeometry(
            int(width * .34), int(height * .29),
            int(width * .35), int(height * .48)
            )
        
        self.layout = QVBoxLayout()        
        self.frame = QWidget(self)
        self.frame.setLayout(self.layout)
        self.frame.setFixedSize(int(width * .32), int(height * .35))
        self.frame.setStyleSheet('''
            border-style: inset;
            border-width: 2px;
            border-color: #C0C0C0
            ''')
        
        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.setContentsMargins(20, 10, 20, 20)
        self.setCentralWidget(self.frame)
        
    def create_widgets(self, height=75):
        
        size = self.frame.width() * .9, height
        self.options = {
            'Manage Data': ManageData, 
            'Gesture Draw': GestureDraw, 
            'Machine Learning': MachineLearning
            }
        for name in self.options.keys():
            
            option = Option(self.frame, name, size=size)
            self.layout.addWidget(option)
    
    def select(self, title):
        
        self.options[title](self, self.desktop)
        self.hide()

    def keyPressEvent(self, sender):

        key_press = sender.key()

        if key_press == Qt.Key_Escape: self.close()

    def closeEvent(self, sender): DATAB.close()
 
class Option(QWidget):

    def __init__(self, parent, target, size):
        
        super().__init__(parent)
        self.target = target
        self.label = QLabel(target, self)
        self.label.setAlignment(Qt.AlignCenter)

        width, height = size
        self.widget = QLabel(self)
        self.label.setFixedSize(int(width * .25), height)
        self.widget.setFixedSize(int(width * .75), height)
        
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.widget)

    def enterEvent(self, sender): self.setStyleSheet('background: #b0caef')

    def leaveEvent(self, sender): self.setStyleSheet('background: #f0f0f0')
    
    def mousePressEvent(self, sender): 
        
        if sender.button() == Qt.LeftButton:

            self.parent().parent().select(self.target)

class ManageData(QMainWindow):
    
    def __init__(self, parent, desktop):
        
        super().__init__(parent)
        self.setWindowTitle('Manage Data')
        self.desktop = desktop
        self.configure_gui()
        self.create_widgets()
        self.showMaximized()
        self.desktop.resized.connect(lambda x: print('po'))

    def configure_gui(self):
        
        self.layout = QHBoxLayout()
        self.center = QWidget()
        self.center.setLayout(self.layout)
        self.setCentralWidget(self.center)

        resolution = Qapp.desktop().screenGeometry()
        self.setGeometry(
            0, 0, 
            resolution.width(),  resolution.height()
            )  

    def create_widgets(self):
        
        self.gallery = galleryView.Gallery(self)
        self.preview = previewView.Preview(self, self.windowTitle())
        
        self.layout.addWidget(self.gallery)
        self.layout.addWidget(self.preview)

        self.gallery.setParent(self)
        self.preview.setParent(self)
    
    def start_slideshow(self, gallery, index):

        try: self.slideshow.close()
        except: self.slideshow = sliderView.Slideshow(self, gallery, index)

    def change_records(self, gallery, *args):
        
        parameters = []
        tags, artists, stars, rating, type = args

        if tags:
            for tag in tags[0]:
                parameters.append(f'tags=CONCAT(tags, "{tag} ")')
            for tag in tags[1]:
                parameters.append(f'tags=REPLACE(tags, " {tag} ", " ")')

        if artists:
            for artist in artists[0]:
                parameters.append(f'artist=CONCAT(artist, "{artist} ")')
            for artist in artists[1]:
                parameters.append(f'artist=REPLACE(artist, " {artist} ", " ")')

        if stars: parameters.append(f'stars={stars}')
        if rating: parameters.append(f'rating={rating - 1}')
        if type: parameters.append(f'type={type - 1}')

        while True:
            try:
                CURSOR.executemany(
                    MODIFY.format(', '.join(parameters)), gallery
                    )
                break
            except sql.errors.InternalError: continue
        DATAB.commit()
        self.gallery.populate()
    
    def delete_records(self, sender=None):
        
        message = QMessageBox.question(
            self, 'Delete', 'Are you sure you want to delete this?',
            QMessageBox.Yes | QMessageBox.No
            )
        
        if message == QMessageBox.Yes:        
            gallery = gallery = [
                (index.data(Qt.UserRole),) for index in 
                self.gallery.images.selectedIndexes()
                ]
            CURSOR.executemany(DELETE, gallery)
            for image, in gallery: 
                try: remove(image)
                except PermissionError: return
                except FileNotFoundError: pass
            DATAB.commit()
            self.gallery.populate()
        
    def keyPressEvent(self, sender):

        key_press = sender.key()

        if key_press == Qt.Key_Delete: self.delete_records()

        elif key_press == Qt.Key_Escape: self.close()

        elif key_press == Qt.Key_F5: self.gallery.populate()

        elif key_press in (Qt.Key_Right, Qt.Key_Left) and sender.modifiers() == Qt.AltModifier:
            
            if key_press == Qt.Key_Left:
                self.gallery.ribbon.go_back()
                
            else:
                self.gallery.ribbon.go_forward()
                        
    def closeEvent(self, sender):

        self.close()
        try: self.slideshow.close()
        except: pass
        self.parent().show()
 
class GestureDraw(QMainWindow):
    
    def __init__(self, parent, desktop):
        
        super().__init__(parent)
        self.setWindowTitle('Gesture Draw')
        self.desktop = desktop
        self.configure_gui()
        self.create_widgets()
        self.show()
        Popen([NEZUMI])

    def configure_gui(self):
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        resolution = Qapp.desktop().screenGeometry()
        self.setGeometry(
            0, 0, 
            resolution.width() // 2,  resolution.height()
            )   

    def create_widgets(self):
        
        self.gallery = galleryView.Gallery(self)
        self.preview = previewView.Preview(self, self.windowTitle())
        
        self.stack.addWidget(self.gallery)
        self.stack.addWidget(self.preview)
        
    def start_session(self):
        
        gallery = [
            thumb.data(Qt.UserRole) for thumb in 
            self.gallery.images.selectedIndexes()
            ]
        time = self.gallery.ribbon.time.text()
        
        if gallery and time:
            if ':' in time:
                m, s = time.split(':')
                time = int(m) * 60 + int(s)
            elif time: time = int(time)
            
            self.preview.start(gallery, time)
            self.stack.setCurrentIndex(1)
   
    def keyPressEvent(self, sender):
        
        key_press = sender.key()

        if key_press == Qt.Key_Escape:

            if self.stack.currentIndex():
            
                self.timer.close()
                self.gallery.ribbon.tags.clear()
                self.gallery.ribbon.time.clear()
                self.stack.setCurrentIndex(0)
                self.gallery.populate()
            
            else: self.close()

        elif key_press == Qt.Key_F5: self.gallery.populate()
    
    def closeEvent(self, sender):

        self.close()
        self.parent().show()
 
class MachineLearning(QMainWindow):
    
    def __init__(self, parent):
        
        super().__init__(parent)
        self.setWindowTitle('Machine Learning')
        self.configure_gui()
        self.create_widgets()
        self.showMaximized()

    def configure_gui(self):
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        resolution = Qapp.desktop().screenGeometry()
        self.setGeometry(
            0, 0, 
            resolution.width(),  resolution.height()
            )  

    def create_widgets(self): 
        
        self.main = mainView.Main(self)
        self.train = trainView.Training(self)
        
        self.stack.addWidget(self.main)
        self.stack.addWidget(self.train)
        self.stack.setCurrentIndex(1)
        
    def keyPressEvent(self, sender):
        
        if sender.key() == Qt.Key_F11: self.open_slideshow()
        
        elif sender.key() == Qt.Key_Enter: self.change_records()
        
        elif sender.key() == Qt.Key_Delete: self.delete_records()
        
        elif sender.key() == Qt.Key_Escape: self.close()

    def closeEvent(self, sender):
    
        self.close()
        self.parent().show()

if __name__ == '__main__':
    
    Qapp = QApplication([])
    
    app = App()
    
    Qapp.exec_()
