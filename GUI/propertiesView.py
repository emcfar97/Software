from  . import AUTOCOMPLETE, Completer
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QTabWidget, QWidget, QFormLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QComboBox

class Properties(QMainWindow):

    update = pyqtSignal(object, object, object)

    def __init__(self, parent, indexes):
        
        super(Properties, self).__init__()
        self.setWindowTitle('Properties')
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        self.populate(indexes)

    def configure_gui(self):
        
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)
        self.props = QWidget()
        self.stats = QWidget()
        
        self.tabs.addTab(self.props, 'Properties')
        self.tabs.addTab(self.stats, 'Stats')
        self.prop_layout = QVBoxLayout()
        self.stat_layout = QVBoxLayout()
        self.props.setLayout(self.prop_layout)
        self.stats.setLayout(self.stat_layout)
        
        size = [
            int(self.parent.width() * .25), 
            int(self.parent.height() * .5)
            ]
        position = [
            self.mapToGlobal(QCursor().pos()).x(), 
            self.mapToGlobal(QCursor().pos()).y()
            ]
        resolution = QDesktopWidget().screenGeometry(
            self.mapToGlobal(QCursor().pos())
            )
        screen = [
            resolution.bottomRight().x(), 
            resolution.bottomRight().y()
            ]

        for num, (i, j, k) in enumerate(zip(size, position, screen)):
            if (displacement := k - (i + j)) < 0: 
                position[num] += displacement
        self.setGeometry(*position, *size)  
        
    def create_widgets(self):
        
        self.modified = {}
        artist, tags = open(AUTOCOMPLETE).readlines()

        self.path = QLineEdit(self)
        self.tags = LineEdit(self)
        self.artist = LineEdit(self)
        self.stars = ComboBox(self)
        self.rating = ComboBox(self)
        self.type = ComboBox(self)
        self.site = LineEdit(self, True)
        
        self.path.setDisabled(True)
        self.tags.setCompleter(Completer(tags.split()))
        self.artist.setCompleter(Completer(artist.split()))
        self.stars.addItems(['', '1', '2', '3', '4', '5'])
        self.rating.addItems(['', 'Safe', 'Questionable', 'Explicit'])
        self.type.addItems(['', 'Photograph', 'Illustration', 'Comic'])
        
        self.form = QFormLayout()
        self.form.addRow('Path', self.path)
        self.form.addRow('Tags',  self.tags)
        self.form.addRow('Artist',  self.artist)
        self.form.addRow('Stars',  self.stars)
        self.form.addRow('Rating',  self.rating)
        self.form.addRow('Type',  self.type)
        self.form.addRow('Site',  self.site)
        self.prop_layout.addLayout(self.form)

        horizontal = QHBoxLayout()
        horizontal.setAlignment(Qt.AlignRight)
        self.prop_layout.addLayout(horizontal)
        for text in ['OK', 'Cancel', 'Apply']:
            option = QPushButton(text)
            if text in ['OK', 'Apply']:
                option.clicked.connect(self.output)
            else: option.clicked.connect(self.close)
            horizontal.addWidget(option)
        else: option.setEnabled(False)
    
        self.tags.textEdited.connect(lambda: option.setEnabled(True))
        self.artist.textEdited.connect(lambda: option.setEnabled(True))
        self.stars.activated.connect(lambda: option.setEnabled(True))
        self.rating.activated.connect(lambda: option.setEnabled(True))
        self.type.activated.connect(lambda: option.setEnabled(True))
        self.site.textEdited.connect(lambda: option.setEnabled(True))
        
    def populate(self, indexes):
        
        path, tags, artist, stars, rating, type, site = (
            set.intersection(*column) for column in zip(*indexes)
            )
        
        if path: self.path.setText(path.pop())
        if tags:  self.tags.setText(' '.join(sorted(tags)))
        if artist: self.artist.setText(' '.join(artist))
        if stars: self.stars.setCurrentIndex(stars.pop())
        if rating: self.rating.setCurrentText(rating.pop())
        if type:  self.type.setCurrentText(type.pop())
        if site:  self.site.setText(site.pop())

        self.paths = [(row[0].pop(),) for row in indexes]
        self.update.connect(self.parent.update_records)
        self.parent.windows.add(self)
        self.tags.setFocus()
        self.show()
    
    def output(self, event=None):
        
        modified = {
            self.form.itemAt(i, 0).widget().text(): 
            self.form.itemAt(i, 1).widget().text()
            for i in range(1, self.form.rowCount())
            if self.form.itemAt(i, 1).widget().text()
            }
        
        self.update.emit(self, self.paths, modified)
        
    def keyPressEvent(self, event):
        
        key_press = event.key()

        if key_press in (Qt.Key_Return, Qt.Key_Enter): self.output()
        
        if key_press == Qt.Key_Escape: self.close()

class LineEdit(QLineEdit):

    def __init__(self, parent, type_=False):

        super(LineEdit, self).__init__(parent)
        self.modified = set(), set()
        self.initial = set()
        self.type = type_
    
    def setText(self, text):

        if text:

            self.initial = set(text.split())

            return super().setText(text)
    
    def text(self):
        
        new = set(super().text().split())
        add, remove = new - self.initial, self.initial - new
        
        if not (add or remove): return False
        
        if self.type: return add
        
        return add, remove

class ComboBox(QComboBox):

    def __init__(self, parent):

        super(ComboBox, self).__init__(parent)
        self.activated.connect(self.modify)
        self.modified = None
  
    def text(self): return self.modified

    def modify(self, change): self.modified = change