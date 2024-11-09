from PyQt6.QtCore import Qt, QThreadPool, pyqtSignal
from PyQt6.QtGui import QCursor, QGuiApplication
from PyQt6.QtWidgets import QMainWindow, QItemDelegate, QTabWidget, QWidget, QFormLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QComboBox

from GUI.utils import AUTOCOMPLETE, Worker, Completer, get_path

# class Properties(QItemDelegate):
class Properties(QMainWindow):

    properties_updated = pyqtSignal(object, object, object)
    set_data = pyqtSignal(object, object)

    def __init__(self, parent, model, indexes):
        
        super(Properties, self).__init__()
        self.setWindowTitle('Properties')
        self.parent = parent
        self.model = model
        self.indexes = indexes
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
        resolution = QGuiApplication.screenAt(
            self.mapToGlobal(QCursor().pos())
            ).geometry()
        screen = [
            resolution.x() + resolution.width() - 1,
            resolution.y() + resolution.height() - 1,
            ]

        for num, (i, j, k) in enumerate(zip(size, position, screen)):
            
            if (displacement := k - (i + j)) < 0:
                
                position[num] += displacement

        self.setGeometry(*position, *size) 
        
    def create_widgets(self):
        
        self.threadpool = QThreadPool()
        self.modified = {}
        # with open(AUTOCOMPLETE) as file:
        with open(AUTOCOMPLETE, encoding='utf8') as file:
            artist, tags = file.readlines()

        self.path = QLineEdit(self)
        self.tags = LineEdit(self)
        self.artist = LineEdit(self)
        self.stars = ComboBox(self)
        self.rating = ComboBox(self)
        self.type = ComboBox(self)
        self.site = LineEdit(self, True)
        
        self.path.setReadOnly(True)
        self.tags.setCompleter(Completer(tags.split()))
        self.artist.setCompleter(Completer(artist.split()))
        self.stars.addItems(['', '1', '2', '3', '4', '5'])
        self.rating.addItems(['', 'General', 'Sensitive', 'Questionable', 'Explicit', 'Restricted'])
        self.rating.view().setRowHidden(5, True)
        self.type.addItems(['', 'Photograph', 'Illustration', 'Comic'])
        
        self.prop_form = QFormLayout()
        self.prop_form.addRow('Path', self.path)
        self.prop_form.addRow('Tags',  self.tags)
        self.prop_form.addRow('Artist',  self.artist)
        self.prop_form.addRow('Stars',  self.stars)
        self.prop_form.addRow('Rating',  self.rating)
        self.prop_form.addRow('Type',  self.type)
        self.prop_form.addRow('Site',  self.site)
        self.prop_layout.addLayout(self.prop_form)


        inputs = QHBoxLayout()
        inputs.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.prop_layout.addLayout(inputs)
        
        for text in ['OK', 'Cancel', 'Apply']:
            
            option = QPushButton(text)
            
            if text in ['OK', 'Apply']:
            
                option.clicked.connect(self.output)
            
            else: option.clicked.connect(self.close)
            
            inputs.addWidget(option)
            
        else: option.setEnabled(False)
    
        self.tags.textEdited.connect(lambda: option.setEnabled(True))
        self.artist.textEdited.connect(lambda: option.setEnabled(True))
        self.stars.activated.connect(lambda: option.setEnabled(True))
        self.rating.activated.connect(lambda: option.setEnabled(True))
        self.type.activated.connect(lambda: option.setEnabled(True))
        self.site.textEdited.connect(lambda: option.setEnabled(True))
        
        self.rowid = QLineEdit(self)
        self.date_used = QLineEdit(self)
        self.hash = QLineEdit(self)
        self.href = QLineEdit(self)
        self.src = QLineEdit(self)
            
        self.rowid.setReadOnly(True)
        self.date_used.setReadOnly(True)
        self.hash.setReadOnly(True)
        self.href.setReadOnly(True)
        self.src.setReadOnly(True)

        self.stat_form = QFormLayout()
        self.stat_form.addRow('Rowid:', self.rowid)
        self.stat_form.addRow('Date Used:', self.date_used)
        self.stat_form.addRow('Hash:', self.hash)
        self.stat_form.addRow('Href:', self.href)
        self.stat_form.addRow('Src:', self.src)
        self.stat_layout.addLayout(self.stat_form)
    
    def populate(self, indexes):

        indexes = [index.data(Qt.ItemDataRole.EditRole) for index in indexes]
        rowid, path, tags, artist, stars, rating, type, site, date_used, hash, href, src = (
            set.intersection(*column) for column in zip(*indexes)
            )
        
        if path: self.path.setText(path.pop())
        if tags:  self.tags.setText(' '.join(sorted(tags)))
        if artist: self.artist.setText(' '.join(artist))
        if stars: self.stars.setCurrentIndex(stars.pop())
        if rating: self.rating.setCurrentText(rating.pop())
        if type:  self.type.setCurrentText(type.pop())
        if site:  self.site.setText(site.pop())

        if rowid: self.rowid.setText(str(rowid.pop()))
        if date_used: self.date_used.setText(str(date_used.pop()))
        if hash: self.hash.setText(hash.pop())
        if href: self.href.setText(href.pop())
        if src: self.src.setText(src.pop())
        
        self.paths = [(*row[1],) for row in indexes]
        self.properties_updated.connect(self.parent.update_records)
        self.set_data.connect(self.model.setData)
        self.parent.windows.add(self)
        self.tags.setFocus()
        self.show()
    
    def output(self, event=None):
        
        modified = {
            self.prop_form.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().text(): 
            self.prop_form.itemAt(i, QFormLayout.ItemRole.FieldRole).widget().get_text()
            for i in range(1, self.prop_form.rowCount())
            if self.prop_form.itemAt(i, QFormLayout.ItemRole.FieldRole).widget().get_text()
            }
        
        self.properties_updated.emit(self, self.paths, modified)

        if len(self.indexes) < 100:

            for index in self.indexes:

                self.set_data.emit(index, modified)

    def keyPressEvent(self, event):
        
        match event.key():
            
            case (Qt.Key.Key_Return|Qt.Key.Key_Enter): self.output()
        
            case Qt.Key.Key_Escape: self.close()

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
    
    def get_text(self):
        
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
  
    def get_text(self): return self.modified

    def modify(self, change): self.modified = change