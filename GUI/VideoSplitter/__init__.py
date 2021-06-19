from PyQt5.QtWidgets import QMainWindow
# from VideoSplitter import *

class MainWindow(QMainWindow):

    def __init__(self, parent):
        
        super(VideoSplitter, self).__init__()
        self.setWindowTitle('Video Splitter')
        self.parent = parent
        self.configure_gui()
        self.create_menu()
        self.create_widgets()
        self.showMaximized()

    def configure_gui(self):
        
        self.layout = QStackedWidget(self)
        self.setCentralWidget(self.layout)  

        resolution = Qapp.desktop().screenGeometry()
        width, height = resolution.width(),  resolution.height()
        self.setGeometry(0, 0, width, height)

    def create_widgets(self):
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)

if __name__ == '__main__':
    
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from VideoSplitter import *

    Qapp = QApplication([])

    app = VideoSplitter(None)

    Qapp.exec_()