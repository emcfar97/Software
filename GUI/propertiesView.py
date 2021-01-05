from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QTabWidget, QWidget, QFormLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QComboBox
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QPoint

class Properties(QMainWindow):

    def __init__(self, parent, indexes):
        
        super(Properties, self).__init__()
        self.setWindowTitle('Properties')
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        self.display(indexes)

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
        
        size = self.parent.width() * .5, self.parent.height() * .5
        position = QCursor().pos()
        resolution = QDesktopWidget().screenGeometry(position)
        screen = resolution.width(), resolution.height()
        screen_position = position - resolution.topLeft()
        screen_position = [screen_position.x(), screen_position.y()]
        position = [position.x(), position.y()]

        for num, (i, j, k, l) in enumerate(
            zip(size, position, screen_position, screen)
            ):
            if (displacement := l - (i + j)) < 0: 
                position[num] += displacement

        self.setGeometry(*position, *size)  
        
    def create_widgets(self):
        
        self.modified = {}
        self.path = QLineEdit(self)
        self.tags = QLineEdit(self)
        self.artist = QLineEdit(self)
        self.stars = QComboBox(self)
        self.rating = QComboBox(self)
        self.type = QComboBox(self)
        self.site = QLineEdit(self)
        
        self.path.setDisabled(True)
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
    
        # self.path.textEdited.connect(lambda: option.setEnabled(True))
        self.tags.textEdited.connect(lambda: option.setEnabled(True))
        self.artist.textEdited.connect(lambda: option.setEnabled(True))
        self.stars.activated.connect(lambda: option.setEnabled(True))
        self.rating.activated.connect(lambda: option.setEnabled(True))
        self.type.activated.connect(lambda: option.setEnabled(True))
        self.site.textEdited.connect(lambda: option.setEnabled(True))
        
        self.tags.textEdited.connect(self.modify)
        self.artist.textEdited.connect(self.modify)
        self.stars.activated.connect(self.modify)
        self.rating.activated.connect(self.modify)
        self.type.activated.connect(self.modify)
        self.site.textEdited.connect(self.modify)

    def display(self, indexes):
        
        self.data = [
            i.data(1000) for i in indexes if i.data(1000) is not None
            ]
        paths = set.intersection(*[i[0] for i in self.data])
        tags  = set.intersection(*[i[1] for i in self.data])
        artist = set.intersection(*[i[2] for i in self.data])
        stars = set.intersection(*[i[3] for i in self.data])
        rating = set.intersection(*[i[4] for i in self.data])
        type  = set.intersection(*[i[5] for i in self.data])
        site  = set.intersection(*[i[6] for i in self.data])
        
        if paths: self.path.setText(paths.pop())
        if tags:  self.tags.setText(' '.join(sorted(tags)))
        if artist: self.artist.setText(' '.join(artist))
        if stars: self.stars.setCurrentIndex(stars.pop())
        if rating: self.rating.setCurrentText(rating.pop())
        if type:  self.type.setCurrentText(type.pop())
        if site:  self.site.setText(site.pop())

        self.place = tags, artist, stars, rating, type, site
        self.parent.windows.add(self)
        self.tags.setFocus()
        self.show()
    
    def modify(self, *args):

        key = None
        self.modified[key] = event.text()

    def output(self, event=None):

        if self.parent.parent().parent().change_records(
            [(index[0].pop(),) for index in self.data if index[0]], 
            tags=self.validate(self.tags, self.place[0]), 
            artist=self.validate(self.artist, self.place[1]), 
            stars=self.stars.currentIndex(), 
            rating=self.rating.currentIndex(),#Text(), 
            type=self.type.currentIndex(),#Text()
            ):
            self.parent.windows.discard(self)
        
    def validate(self, query, place):
        
        target = set(query.text().split())
        insert = target - place
        remove = place - target

        return insert, remove
    
    def keyPressEvent(self, event):
        
        key_press = event.key()

        if key_press in (Qt.Key_Return, Qt.Key_Enter): self.output()
        
        if key_press == Qt.Key_Escape: self.close()