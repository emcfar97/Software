from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QFormLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QComboBox
from PyQt5.QtCore import Qt

class Properties(QMainWindow):

    def __init__(self, parent, indexes):
        
        super().__init__(parent)
        self.setWindowTitle('Properties')
        self.configure_gui()
        self.create_widgets()
        self.display(indexes)

    def configure_gui(self):
        
        self.center = QWidget()
        self.layout = QVBoxLayout()
        self.setCentralWidget(self.center)
        self.center.setLayout(self.layout)
        
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
        self.tags.returnPressed.connect(self.output)
        self.artist.returnPressed.connect(self.output)
        self.stars.addItems(['', '1', '2', '3', '4', '5'])
        self.rating.addItems(['', 'Safe', 'Questionable', 'Explicit'])
        self.type.addItems(['', 'Photograph', 'Illustration'])
        
        self.form = QFormLayout()
        self.form.addRow('Path', self.path)
        self.form.addRow('Tags',  self.tags)
        self.form.addRow('Artist',  self.artist)
        self.form.addRow('Stars',  self.stars)
        self.form.addRow('Rating',  self.rating)
        self.form.addRow('Type',  self.type)
        self.layout.addLayout(self.form)

        horizontal = QHBoxLayout()
        horizontal.setAlignment(Qt.AlignRight)
        for text in ['OK', 'Cancel', 'Apply']:
            option = QPushButton(text)
            if text in ['OK', 'Apply']:
                option.clicked.connect(self.output)
            else: option.clicked.connect(self.close)
            horizontal.addWidget(option)
        else: option.setEnabled(False)
        self.layout.addLayout(horizontal)
    
        self.path.textEdited.connect(lambda: option.setEnabled(True))
        self.tags.textEdited.connect(lambda: option.setEnabled(True))
        self.artist.textEdited.connect(lambda: option.setEnabled(True))
        self.stars.activated.connect(lambda: option.setEnabled(True))
        self.rating.activated.connect(lambda: option.setEnabled(True))
        self.type.activated.connect(lambda: option.setEnabled(True))

    def display(self, indexes):
        
        self.indexes = indexes
        data = [i.data(1000) for i in self.indexes]
        paths = set.intersection(*[i[0] for i in data])
        tags = set.intersection(*[i[1] for i in data])
        artist = set.intersection(*[i[2] for i in data])
        stars = set.intersection(*[i[3] for i in data])
        rating = set.intersection(*[i[4] for i in data])
        type = set.intersection(*[i[5] for i in data])
        
        if paths: self.path.setText(paths.pop())
        if tags: self.tags.setText(' '.join(tags))
        if artist: self.artist.setText(' '.join(artist))
        if stars: self.stars.setCurrentIndex(int(stars.pop()))
        if rating: self.rating.setCurrentText(rating.pop().capitalize())
        if type: self.type.setCurrentIndex(type.pop() + 1)

        self.place = tags, artist
        self.show()
    
    def output(self, sender=None):

        gallery = [
            (index.data(Qt.UserRole),) for index in self.indexes
            ]
        tags = self.validate(0)
        artist = self.validate(1)
        stars = int(self.stars.currentText()) if self.stars.currentText() else 0
        rating = self.rating.currentText()
        type = self.type.currentIndex()

        if gallery and (tags or artist or (0 < stars <= 5) or rating or type):
            self.parent().parent().change_records(
                gallery, tags, artist, stars, rating, type - 1
                )

        self.close()

    def validate(self, type_):
        
        target = (
            set(self.artist.text().split())
            if type_ else 
            set(self.tags.text().split())
            )
        insert = target - self.place[type_]
        remove = self.place[type_] - target

        return (insert, remove) if any([insert, remove]) else tuple()
    
    def type_validation(self):

        type = self.type.currentIndex() - 1

        return [type] if type >= 0 else None
