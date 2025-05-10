import deepl, pytesseract, cv2, qimage2ndarray, psutil, win32process, win32gui, re
import numpy as np
from os import getenv
from dotenv import load_dotenv, set_key

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QComboBox, QLabel, QVBoxLayout, QAction, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, QThreadPool, pyqtSignal
from PyQt6.QtGui import QPaintEvent, QWindow, QGuiApplication, QPixmap, QPainter

from GUI import Worker

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
load_dotenv(r'GUI\.env')
DEEPL = deepl.Translator(getenv('AUTH_KEY'))
        
class Launch(QMainWindow):
    
    window_selected = pyqtSignal(object)

    def __init__(self, parent=None):
        
        super(Launch, self).__init__()
        self.setWindowTitle('Visual Novel Reader')
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        self.show()
        self.activateWindow()
        
    def configure_gui(self):
        
        self.center = QWidget(self)
        self.layout = QVBoxLayout()
        
        self.center.setLayout(self.layout)
        self.setCentralWidget(self.center)

        geometry = QApplication.desktop().screenGeometry()
        
        self.setGeometry(
            int(geometry.width() * .33), int(geometry.height() * .33),
            int(geometry.width() * .35), int(geometry.height() * .48)
            )
        self.setMinimumSize(
            int(geometry.width() * .20), int(geometry.width() * .20)
            )
        
    def create_widgets(self):
        
        # self.refresh = QTimer(self)
        self.label = QLabel('Choose a window', self)
        self.combobox = QComboBox(self)

        # self.refresh.setInterval(500)
        # self.refresh.timeout.connect(self.get_windows)
        self.label.setAlignment(Qt.AlignCenter)
        self.combobox.setMinimumWidth(100)
        self.combobox.addItems(self.get_windows())
        self.combobox.currentTextChanged.connect(self.select_window)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combobox)
        # self.refresh.start()

    def create_menu(self):

        self.menubar = self.menuBar()
        self.menubar.triggered.connect(self.menuPressEvent)
        
        # File
        file = self.menubar.addMenu('File')
        
        # View
        view = self.menubar.addMenu('View')
        
        # Help
        help = self.menubar.addMenu('Help')
        
        self.usage = QAction(self)
        self.usage.setText(
            f'Character usage: ' +
            f'{DEEPL.get_usage().character.count} of ' +
            f'{DEEPL.get_usage().character.limit}'
            )
        self.usage.setEnabled(False)
        
        help.addAction(self.usage)

    def get_windows(self):
        
        self.combobox.clear()
        windows = ['']
        win32gui.EnumWindows(self.winEnumHandler, windows)

        return windows
        
    def winEnumHandler(self, hwnd, windows):

        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            
            name = f'[{hex(hwnd)}]: {win32gui.GetWindowText(hwnd)}'
            windows.append(name)

    def select_window(self, window): self.window_selected.emit(window)
    
    def update_usage(self):
        
        self.usage.setText(
            f'Character usage: ' +
            f'{DEEPL.get_usage().character.count} of ' +
            f'{DEEPL.get_usage().character.limit}'
            )
        
    def keyPressEvent(self, event):

        key_press = event.key()
        # modifiers = event.modifiers()
        # alt = modifiers == Qt.AltModifier
                        
        if key_press == Qt.Key_Escape: self.close()
    
    def menuPressEvent(self, event):

        action = event.text()
    
        # File
        
        # View
        
        # Help
        
    def closeEvent(self, event):
        
        self.parent.window.setParent(None)
        self.parent.container.setWindowFlags(Qt.Window | Qt.MSWindowsOwnDC)
        self.close()

class ScreenReader(QMainWindow):
    
    def __init__(self, parent=None):
        
        super(ScreenReader, self).__init__()
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        
    def configure_gui(self):
        
        self.text = ''
        self.translation = ''
        self.region_interest = []
        
        self.window = None
        self.whnd = None
        self.center = QWidget(self)
        
    def create_widgets(self):
        
        self.pixmap = QPixmap()
        self.threadpool = QThreadPool(self)
        self.launch = Launch(self)
        
        self.capture_timer = QTimer(self)
        self.capture_timer.setInterval(1000)
        self.capture_timer.timeout.connect(self.capture_screen)
        
        self.launch.window_selected.connect(self.set_window)
    
    def set_window(self, window):
        
        title, = re.findall('\[.+\]: (.+)', window)
        self.whnd = win32gui.FindWindowEx(None, None, None, title)  
        self.setWindowTitle(f'Visual Novel Reader — {title}')
        
        self.window = QWindow.fromWinId(self.whnd)
        self.container = QWidget.createWindowContainer(self.window)
        self.container.setWindowFlags(Qt.FramelessWindowHint)
        self.container.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        
        self.setCentralWidget(self.container)
        self.capture_timer.start()
        self.showFullScreen()
        self.activateWindow()
    
    def extract_text(self):
        
        image = self.pixmap_to_array(self.pixmap)
        mask = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        mask = cv2.threshold(
            mask, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
            )[1]
        # mask = cv2.GaussianBlur(mask, (11, 11), 1)
        
        # get horizontal mask of large size since text are horizontal components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 13))
        connected = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        contours, heirarchy = cv2.findContours(
            connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
        for contour in contours:
            
            coordinate = cv2.boundingRect(contour)
            label = TextRegion(self.window,'', coordinate)

            self.region_interest.append(label)
        
        self.capture_timer.start()

    def pixmap_to_array(self, pixmap):
                
        return qimage2ndarray.rgb_view(pixmap.toImage())
    
    def capture_screen(self):
        
        screen = QGuiApplication.primaryScreen()
        pixmap = screen.grabWindow(self.whnd)

        if self.pixmap.isNull() or (self.pixmap.toImage() != pixmap.toImage()):
            
            self.capture_timer.stop()
            self.pixmap = pixmap 
            self.extract_text()
    
class TextRegion(QLabel):
    
    def __init__(self, parent, text, ROI):
        
        super(TextRegion, self).__init__(parent)
        self.setText(text)
        self.configure_gui(ROI)
        self.translate_text()
        
    def configure_gui(self, region_interest):

        self.setGeometry(*region_interest)
        self.setStyleSheet("color: red;")
    
    def translate_text(self):
        
        text = self.text()