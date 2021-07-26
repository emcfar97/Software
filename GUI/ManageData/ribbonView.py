from PyQt5.QtCore import QTimer, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QAbstractItemView, QPushButton, QCheckBox, QStyle, QCompleter, QMenu, QAction

class Ribbon(QWidget):
     
    def __init__(self, parent):
         
        super(Ribbon, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
        
    def configure_gui(self):
         
        self.undo = ['']
        self.redo = []

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def create_widgets(self):
        
        # History navigation
        self.history = QHBoxLayout()
        self.layout.addLayout(self.history)

        self.back = QPushButton()
        self.forward = QPushButton()
        self.menu = QPushButton()
        
        for button, event, icon in zip(
            [self.back, self.forward, self.menu],
            [self.go_back, self.go_forward, self.menu.showMenu],
            [QStyle.SP_ArrowBack, QStyle.SP_ArrowForward, QStyle.SP_ArrowDown]
            ):
            
            button.setIcon(self.style().standardIcon(icon))
            button.clicked.connect(event)
            button.setEnabled(False)
            self.history.addWidget(button)

        # Search function
        self.tags = QLineEdit(self)
        self.tags.setPlaceholderText('Enter tags')
        self.tags.setCompleter(
            QCompleter(open(AUTOCOMPLETE).read().split())
            )
        self.tags.returnPressed.connect(self.parent().select_records)
        self.tags.textChanged.connect(self.parent().gallery.update)
        self.layout.addWidget(self.tags, 6)
        
        self.timer = QTimer(self.tags)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.parent().select_records)
        self.tags.textChanged.connect(lambda: self.timer.start(1000))
        
        self.refresh = QPushButton(self)
        self.refresh.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.refresh.clicked.connect(self.parent().select_records)
        self.layout.addWidget(self.refresh, 1, Qt.AlignLeft)
        
        self.multi = QCheckBox('Multi-selection', self)
        self.multi.clicked.connect(self.changeSelectionMode)
        self.layout.addWidget(self.multi, 0, Qt.AlignLeft)

        self.tags.setFocus()
        
    def update(self, string='', check=1):

        if string:

            if self.undo:
                if string != self.undo[-1]:
                    self.undo.append(string)
                    self.redo.clear()
            else:
                self.undo.append(string)
                self.redo.clear()

        self.back.setEnabled(bool(self.undo[1:]))
        self.forward.setEnabled(bool(self.redo))
        self.menu.setEnabled(bool(self.undo + self.redo))

        menu = QMenu(self, triggered=self.menuEvent)
        for state in reversed(self.undo[1:] + self.redo[::-1]):
            
            action = QAction(state, menu, checkable=True)
            if state == string and check: 
                action.setChecked(True)
                check=0
            menu.addAction(action)

        else: self.menu.setMenu(menu)
        
        self.tags.setText(self.undo[-1])
    
    def go_back(self, event=None, update=True):
        
        if len(self.undo) > 1:
            self.redo.append(self.undo.pop())
            if update: self.update()

    def go_forward(self, event=None, update=True):
        
        if self.redo:
            self.undo.append(self.redo.pop())
            if update: self.update()
    
    def changeSelectionMode(self, event):
        
        if event:
            self.parent().images.setSelectionMode(
                QAbstractItemView.MultiSelection
                )
        else:
            self.parent().images.setSelectionMode(
                QAbstractItemView.ExtendedSelection
                )
            self.parent().images.clearSelection()
    
    def menuEvent(self, event):

        action = event.text()

        if action in self.undo:

            while action != self.undo[-1]: self.go_back(update=False)

        elif action in self.redo:

            while action in self.redo: self.go_forward(update=False)
        
        self.update()

    def keyPressEvent(self, event):
    
        key_press = event.key()

        if key_press in (Qt.Key_Return, Qt.Key_Enter): pass

        else: self.parent().keyPressEvent(event)