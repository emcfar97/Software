from PyQt6.QtWidgets import QTableView, QAbstractItemView
from PyQt6.QtCore import Qt, QItemSelection, QVariant, pyqtSignal
from PyQt6.QtGui import QFileSystemModel
    
class FileExplorer(QTableView):
    
    selection = pyqtSignal(QItemSelection, QItemSelection)
     
    def __init__(self, parent):
         
        super(FileExplorer, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        for header in [self.horizontalHeader(), self.verticalHeader()]:
            header.setSectionResizeMode(header.Stretch)
            header.hide()
        else: header.setSectionResizeMode(header.ResizeToContents)
        
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setVerticalScrollMode(1)
        self.setGridStyle(0)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.contextMenuEvent)
        
        self.setStyleSheet('''
            QTableView {
                outline: 0;
            }
            QTableView::item:selected {   
                background: #CDE8FF;
                border: 1px solid #99D1FF
            }
            QTableView::item:!selected:hover
            {   
                background: #E5F3FF;
            }
        ''')
    
    def create_widgets(self):
        
        self.model = Model(self)
        self.model.setRootPath(ROOT_DIR)
        self.setModel(self.model)
        self.setRootIndex(self.model.index(ROOT_DIR))
        
    def selectionChanged(self, select, deselect):
        
        self.selection.emit(select, deselect)
                
class Model(QFileSystemModel):
    
    def __init__(self, parent):

        QFileSystemModel.__init__(self, parent)
        
    # def data(self, index, role):
        
    #     if role == Qt.DecorationRole: return 
        
        # if role == Qt.EditRole: return self.parent.rootIndex + data
        
    #     if role == Qt.ToolTipRole: return
        
    #     if role == Qt.SizeHintRole: return 
        
    #     if role == Qt.UserRole: return 
        
    #     return QVariant()