from PyQt5.QtWidgets import QDockWidget, QWidget,QVBoxLayout, QTabWidget, QTreeWidget, QSizePolicy
from PyQt5.QtCore import Qt
from random import randint

class Design(QTabWidget):

    def __init__(self, parent):
        
        super(Design, self).__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(lambda index: self.removeTab(index))
        self.create_widgets()

        for i in range(3): self.addTab(Model(self), f'Model{i}')

    def create_widgets(self):
        
        self.palettes = Palettes(self)
        self.inspector = Inspector(self)

        self.parent().addDockWidget(Qt.LeftDockWidgetArea, self.palettes)
        self.parent().addDockWidget(Qt.RightDockWidgetArea, self.inspector)
    
    def keyPressEvent(self, event):
    
        key_press = event.key()

        if False: pass

        else: self.parent().keyPressEvent(event)

class Model(QWidget):
    
    def __init__(self, parent): 
        
        super(Model, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()

    def configure_gui(self): pass
        
    def create_widgets(self): pass
    
    def keyPressEvent(self, event):
    
        key_press = event.key()

        if False: pass

        else: self.parent().keyPressEvent(event)
        
class Palettes(QDockWidget):
    
    def __init__(self, parent):
        
        super(Palettes, self).__init__('Palettes', parent)
        self.layout = QVBoxLayout()
        self.configure_gui()
        self.create_widgets()

    def configure_gui(self):
        
        self.setMinimumWidth(self.parent().width())
        self.setAllowedAreas(
            Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
            )

    def create_widgets(self):
        
        for i in range(20):
            i = Layer(self)
            self.layout.addWidget(i)
        # self.tree = QTreeWidget(self)
        # # self.tree.setColumnCount(1)
        # self.tree.setColumnHidden(0, True)
        # self.layout.addWidget(self.tree)

    def keyPressEvent(self, event):
    
        key_press = event.key()

        if False: pass

        else: self.parent().keyPressEvent(event)

class Inspector(QDockWidget):
    
    def __init__(self, parent):
        
        super(Inspector, self).__init__('Inspector', parent)
        self.layout = QVBoxLayout()
        self.configure_gui()
        self.create_widgets()

    def configure_gui(self):
        
        self.setAllowedAreas(
            Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
            )
        self.setMinimumWidth(self.parent().width())
        self.setGeometry(0, 0, 300, 600)

    def create_widgets(self):

        self.tree = QTreeWidget(self)
        # self.tree.setColumnCount(1)
        self.tree.setColumnHidden(0, True)
        self.layout.addWidget(self.tree)
    
    def keyPressEvent(self, event):
    
        key_press = event.key()

        if False: pass

        else: self.parent().keyPressEvent(event)

class Layer(QWidget):
    
    def __init__(self, parent): 
        
        super(Layer, self).__init__(parent)
        self.setStyleSheet(
            f'background: {hex(randint(0,15))}{hex(randint(0,15))}{hex(randint(0,15))}'
            )

    def configure_gui(self): pass

    def create_widgets(self): pass