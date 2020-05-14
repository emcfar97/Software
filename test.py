import os, shutil
from os.path import splitext, join, exists
import os, ffmpeg, tempfile, shutil
from os.path import join, splitext, split
from ffprobe import FFProbe
from Webscraping.utils import DATAB, CURSOR, sql, save_image, get_tags, generate_tags, get_driver, execute
path = r'C:\Users\Emc11\Downloads\Katawa Shoujo'
dest = r'C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三'
sprites = {}

for i in range(3):

        for file in os.listdir(path):
            if not file.endswith('jpg'): continue
            file = splitext(file)[0]
            try: 
                char, pose, expr = file.split('_')[1:]
                if not char.startswith(("shiz", "mish", "lill", "hanak", "emi", "rin")): continue
            except ValueError: continue
            
            if i == 0: 
                if char == 'emiwheel': continue
                if char == 'shizuyu': continue
                if char == 'rinpan': continue
                
                sprites[char] = {}
            
            elif i == 1: 
                if char == 'shizuyu':
                    pose = char
                    char = 'shizu'
                if char == 'emiwheel':
                    pose = char
                    char = 'emi'
                if char == 'rinpan': 
                    pose = char
                    char = 'rin'
                
                sprites[char][pose] = []

            elif i == 2: 
                if char == 'shizuyu':
                    pose = char
                    char = 'shizu'
                if char == 'emiwheel':
                    pose = char
                    char = 'emi'
                if char == 'rinpan': 
                    pose = char
                    char = 'rin'
                
                sprites[char][pose].append(expr)

#
    # from PyQt5.QtCore import QVariant, Qt
    # from PyQt5.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
    # from PyQt5.QtWidgets import QApplication, QTableView, QLabel, QItemDelegate

    # class ImportSqlTableModel(QSqlTableModel):

    #     def __init__(self, *args, **kwargs):
            
    #         super(ImportSqlTableModel, self).__init__(*args, **kwargs)
    #         self.db = open_database()
    #         self.setTable("imageData")
    #         self.setEditStrategy(QSqlTableModel.OnFieldChange)
    #         qry = QSqlQuery("select * from imageData LIMIT 10", self.db)
    #         self.setQuery(qry)
    #         self.setFilter('stars=5')
    #         self.select()
    #         idx = self.index(0, 0)
    #         print('Data',idx.data(),self.rowCount(), self.columnCount())
    #         pass

    #     def data(self, index, role=Qt.DisplayRole):

    #         value = super(ImportSqlTableModel, self).data(index)
    #         if index.column() in self.booleanSet:
    #             if role == Qt.CheckStateRole:
    #                 return Qt.Unchecked if value == 2 else Qt.Checked
    #             else:
    #                 return QVariant()
    #         return QSqlTableModel.data(self, index, role)

    #     def setData(self, index, value, role=Qt.EditRole):
    #         if not index.isValid():
    #             return False
    #         if index.column() in self.booleanSet:
    #             if role == Qt.CheckStateRole:
    #                 val = 2 if value == Qt.Unchecked else 0
    #                 return QSqlTableModel.setData(self, index, val, Qt.EditRole)
    #             else:
    #                 return False
    #         else:
    #             return QSqlTableModel.setData(self, index, value, role)

    #     def flags(self, index):
    #         if not index.isValid():
    #             return Qt.NoItemFlags
    #         if index.column() in self.booleanSet:
    #             return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable
    #         elif index.column() in self.readOnlySet:
    #             return Qt.ItemIsSelectable | Qt.ItemIsEnabled
    #         else:
    #             return QSqlTableModel.flags(self, index)

    # def open_database():
        
    #     datab = QSqlDatabase.addDatabase('QSQLITE')
    #     datab.setUserName('root')
    #     datab.setPassword('SchooL1@')
    #     datab.setDatabaseName('userData')
    #     datab.setHostName(
    #         '192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    #         )
    #     datab.open()
        
    #     return datab

    # app = QApplication([])
    # test_model = ImportSqlTableModel()
    # app.exec_()

path = r'C:\Users\Emc11\Videos\Captures\2020-0418-1857.mp4'
new = r'C:\Users\Emc11\Dropbox\Videos\Captures\2020-0418-1857.mp4'

metadata = FFProbe(path).streams[0]
height, width = int(metadata.height), int(metadata.width)
file = split(splitext(path)[0])[-1]
ffmpeg.input(path).drawtext(
    text=file, x=width*.75, y=height*.90, shadowx=(width*.75) + 10, shadowy=(height*.90) + 10, shadowcolor='gray', fontsize=42) \
    .output(new, crf=20, preset='fast').run()