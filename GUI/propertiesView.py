from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QFormLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QComboBox
from PyQt5.QtCore import Qt

class Properties(QMainWindow):

    def __init__(self, parent, indexes):
        
        super().__init__(parent)
        self.parent().properties.add(self)
        self.setWindowTitle('Properties')
        self.configure_gui()
        self.create_widgets()
        self.display(indexes)

    def configure_gui(self):
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.props = QWidget()
        self.stats = QWidget()
        self.tabs.addTab(self.props, 'Properties')
        self.tabs.addTab(self.stats, 'Stats')
        self.prop_layout = QVBoxLayout()
        self.stat_layout = QVBoxLayout()
        self.props.setLayout(self.prop_layout)
        self.stats.setLayout(self.stat_layout)

        size = self.parent().size()
        self.setGeometry(
            size.width() * .3, size.height() * .3, 
            size.width() * .45,  size.height() * .50
            )  
        
    def create_widgets(self):
        
        self.path = QLineEdit(self)
        self.tags = QLineEdit(self)
        self.artist = QLineEdit(self)
        self.stars = QComboBox(self)
        self.rating = QComboBox(self)
        self.type = QComboBox(self)
        
        self.path.setDisabled(True)
        self.stars.addItems(['', '1', '2', '3', '4', '5'])
        self.rating.addItems(['', 'Safe', 'Questionable', 'Explicit'])
        self.type.addItems(['', 'Photograph', 'Illustration', 'Comics'])
        
        self.form = QFormLayout()
        self.form.addRow('Path', self.path)
        self.form.addRow('Tags',  self.tags)
        self.form.addRow('Artist',  self.artist)
        self.form.addRow('Stars',  self.stars)
        self.form.addRow('Rating',  self.rating)
        self.form.addRow('Type',  self.type)
        self.prop_layout.addLayout(self.form)

        horizontal = QHBoxLayout()
        horizontal.setAlignment(Qt.AlignRight)
        for text in ['OK', 'Cancel', 'Apply']:
            option = QPushButton(text)
            if text in ['OK', 'Apply']:
                option.clicked.connect(self.output)
            else: option.clicked.connect(self.close)
            horizontal.addWidget(option)
        else: option.setEnabled(False)
        self.prop_layout.addLayout(horizontal)
    
        self.path.textEdited.connect(lambda: option.setEnabled(True))
        self.tags.textEdited.connect(lambda: option.setEnabled(True))
        self.artist.textEdited.connect(lambda: option.setEnabled(True))
        self.stars.activated.connect(lambda: option.setEnabled(True))
        self.rating.activated.connect(lambda: option.setEnabled(True))
        self.type.activated.connect(lambda: option.setEnabled(True))

    def display(self, indexes):
        
        self.data = [
            i.data(1000) for i in indexes if i.data(1000) is not None
            ]
        paths = set.intersection(*[i[0] for i in self.data])
        tags = set.intersection(*[i[1] for i in self.data])
        artist = set.intersection(*[i[2] for i in self.data])
        stars = set.intersection(*[i[3] for i in self.data])
        rating = set.intersection(*[i[4] for i in self.data])
        type = set.intersection(*[i[5] for i in self.data])
        
        if paths: self.path.setText(paths.pop())
        if tags: self.tags.setText(' '.join(sorted(tags)))
        if artist: self.artist.setText(' '.join(artist))
        if stars: self.stars.setCurrentIndex(stars.pop())
        if rating: self.rating.setCurrentText(rating.pop())
        if type: self.type.setCurrentText(type.pop())

        self.place = tags, artist
        self.tags.setFocus()
        self.show()
    
    def output(self, sender=None):

        gallery = [(index[0].pop(),) for index in self.data if index[0]]
        tags = self.validate(0)
        artist = self.validate(1)
        stars = self.stars.currentIndex()
        rating = self.rating.currentIndex()
        type = self.type.currentIndex()
        
        self.close()

        if gallery and (tags or artist or (0 < stars <= 5) or rating or type):
            self.parent().parent().change_records(
                gallery, tags, artist, stars, rating, type
                )
        
    def validate(self, type_):
        
        target = (
            set(self.artist.text().split())
            if type_ else 
            set(self.tags.text().split())
            )
        insert = target - self.place[type_]
        remove = self.place[type_] - target

        return (insert, remove) if any([insert, remove]) else tuple()
    
    def keyPressEvent(self, sender):
        
        key_press = sender.key()
        ctrl = sender.modifiers()

        if key_press == Qt.Key_Return: self.output()
        
        if key_press == Qt.Key_Escape: self.close()