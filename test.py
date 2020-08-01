import os, shutil
from os.path import splitext, join, exists, isfile
from Webscraping.utils import DATAB, CURSOR, sql, save_image, get_tags, generate_tags, get_driver, execute

# manuke shounen
    # path = r'C:\Users\Emc11\Downloads\Katawa Shoujo'
    # dest = r'C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三'
    # sprites = {}

    # for i in range(3):

    #         for file in os.listdir(path):
    #             if not file.endswith('jpg'): continue
    #             file = splitext(file)[0]
    #             try: 
    #                 char, pose, expr = file.split('_')[1:]
    #                 if not char.startswith(("shiz", "mish", "lill", "hanak", "emi", "rin")): continue
    #             except ValueError: continue
                
    #             if i == 0: 
    #                 if char == 'emiwheel': continue
    #                 if char == 'shizuyu': continue
    #                 if char == 'rinpan': continue
                    
    #                 sprites[char] = {}
                
    #             elif i == 1: 
    #                 if char == 'shizuyu':
    #                     pose = char
    #                     char = 'shizu'
    #                 if char == 'emiwheel':
    #                     pose = char
    #                     char = 'emi'
    #                 if char == 'rinpan': 
    #                     pose = char
    #                     char = 'rin'
                    
    #                 sprites[char][pose] = []

    #             elif i == 2: 
    #                 if char == 'shizuyu':
    #                     pose = char
    #                     char = 'shizu'
    #                 if char == 'emiwheel':
    #                     pose = char
    #                     char = 'emi'
    #                 if char == 'rinpan': 
    #                     pose = char
    #                     char = 'rin'
                    
    #                 sprites[char][pose].append(expr)

# pyqt5
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
    #         '192.168.1.43' if __file__.startswith(('e:\\|e:/')) else '127.0.0.1'
    #         )
    #     datab.open()
        
    #     return datab

    # app = QApplication([])
    # test_model = ImportSqlTableModel()
    # app.exec_()

# ffmpeg
    # import ffmpeg, ffprobe

    # path = r'C:\Users\Emc11\Downloads'

    # for file in os.listdir(path):
        
    #     if file.endswith('ogg'):
    #         file = join(path, file)
    #         audio = file.replace('ogg', 'opus')
    #         ffmpeg.input(file).output(audio, metadata='title="ENG Stereo (Opus 112Kbps)"').run()

    # "C:\Users\Emc11\Downloads\S01E01.opus" "C:\Users\Emc11\OneDrive - University of Missouri\Documents\Reference\Pickup A Live\Date A Live - S1\[Judas] Date A Live - S01E01.mkv" 
    # # [Judas] Date A Live - S01E01

SELECT = 'SELECT DISTINCT artist FROM imagedata GROUP BY artist HAVING COUNT(artist) > 100 ORDER BY artist'
STATS = '''SELECT (
    SELECT COUNT(*) FROM imagedata 
    WHERE MATCH(tags, artist) AGAINST(%s IN BOOLEAN MODE) AND stars
    ) AS TOTAL,
    (
    SELECT SUM(stars) FROM imagedata 
    WHERE MATCH(tags, artist) AGAINST(%s IN BOOLEAN MODE)
    ) AS STARS
    '''

CURSOR.execute(SELECT)

for artist, in CURSOR.fetchall()[1:101]:

    CURSOR.execute(STATS, (artist, artist))
    sum, star = CURSOR.fetchone()
    try: print(f'{artist.strip():<25} (Num: {sum:>4}, Stars: {star:>4}): {star / (sum*5):>4.2%}')
    except: continue