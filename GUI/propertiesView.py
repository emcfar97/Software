from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QFormLayout, QVBoxLayout, QLineEdit
from PyQt5.QtCore import Qt

class Properties(QMainWindow):

    def __init__(self, parent): 
        
        super().__init__(parent)
        self.setWindowTitle('Properties')
        self.configure_gui()
        self.create_widgets()
        self.show()

    def configure_gui(self): 
        
         
        self.layout = QFormLayout()
        self.layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.setLayout(self.layout)

        resolution = Qapp.desktop().screenGeometry()
        self.setGeometry(
            resolution.width() * .3, resolution.height() * .3, 
            resolution.width() * .25,  resolution.height() * .5
            )  

    def create_widgets(self): 
        
        # self.details = QFormLayout()
        # self.details.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        # self.layout.addLayout(self.details)

        self.layout.addRow('Title', QLineEdit(self))
        self.layout.addRow('Tags',  QLineEdit(self))
        self.layout.addRow('Artist',  QLineEdit(self))
        self.layout.addRow('Stars',  QLineEdit(self))
        self.layout.addRow('Rating',  QLineEdit(self))
        self.layout.addRow('Type',  QLineEdit(self))

if __name__ == '__main__':
    
    Qapp = QApplication([])
    
    app = Properties(None)

    Qapp.exec_()