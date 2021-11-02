import os, dotenv
import mysql.connector as sql
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QFormLayout, QLineEdit, QDialog, QDialogButtonBox, QMessageBox

class CONNECT:
    
    finishedTransaction = pyqtSignal(object)
    finishedSelect = pyqtSignal(object)
    finishedUpdate = pyqtSignal(object)
    finishedDelete = pyqtSignal(object)

    def __init__(self, credentials):

        super(CONNECT, self).__init__()
        self.DATAB = sql.connect(**credentials)
        self.CURSOR = self.DATAB.cursor(buffered=True)

    def execute(self, statement, arguments=None, many=0, fetch=0, source=None):
        
        try:
            if many: self.CURSOR.executemany(statement, arguments)
            else: self.CURSOR.execute(statement, arguments)

            if statement.startswith('SELECT'):

                if fetch: return self.CURSOR.fetchall()

                self.finishedSelect.emit(self.CURSOR.fetchall())
                
                return
                
            elif statement.startswith('UPDATE'):

                self.DATAB.commit()
                self.finishedUpdate.emit(source)
                
            elif statement.startswith('DELETE'):

                self.finishedDelete.emit(arguments)

            self.finishedTransaction.emit(1)

        except sql.errors.ProgrammingError as error:
            
            print('Programming', error, statement)
            return

        except sql.errors.DatabaseError as error:

            print('Database', error, statement)
            try: self.reconnect(1)
            except Exception as error:
                print('\tDatabase', error, statement)
            
            return

        except sql.errors.InterfaceError as error:

            print('Interface', error, statement)
            try: self.reconnect(1)
            except Exception as error:
                print('\tInterface', error, statement)

            return
            
        except Exception as error:
        
            print('Error', error)
            return

        return

    def rollback(self): self.DATAB.rollback()

    def reconnect(self, attempts=5, time=6):

        self.DATAB.reconnect(attempts, time)

    def commit(self): self.DATAB.commit()
    
    def rowcount(self): return self.CURSOR.rowcount

    def close(self): self.DATAB.close()

class Authenticate(QDialog):

    def __init__(self):
        
        cred = {
            'user': os.getenv('USER'),
            'password': os.getenv('PASS'),
            'host': os.getenv('HOST'),
            'database': os.getenv('DATA'),
            }
        self.success(cred)
    
    def success(self, cred):

        try: return CONNECT(cred)
        except (sql.errors.InterfaceError, UnicodeError):
            self.start()
    
    def start(self):

        super().__init__()

        self.setWindowTitle("Enter your credentials")

        QBtn = QDialogButtonBox.StandardButton.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QFormLayout()
        self.layout.addRow('Username:', QLineEdit())
        self.layout.addRow('Password:', QLineEdit())
        self.layout.addRow('Hostname:', QLineEdit())
        self.layout.addRow('Database:', QLineEdit())

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.exec()
        
        if QBtn == QDialogButtonBox.StandardButton.Ok:

            cred = {
                'user': self.layout.itemAt(1).widget().text(),
                'password': self.layout.itemAt(3).widget().text(),
                'host': self.layout.itemAt(5).widget().text(),
                'database': self.layout.itemAt(7).widget().text()
                }

            try:

                success = CONNECT(cred)
                env = dotenv.find_dotenv()
                dotenv.set_key(env, 'USER', cred['user'])
                dotenv.set_key(env, 'PASS', cred['password'])
                dotenv.set_key(env, 'HOST', cred['host'])
                dotenv.set_key(env, 'DATA', cred['database'])

                return success
    
            except (sql.errors.InterfaceError, ValueError):

                message = QMessageBox(self)
                message.setWindowTitle('Error')
                message.setText('The entered credentials are incorrect')
                message.setStandardButtons(QMessageBox.StandardButton.Ok)
                
                if message == QMessageBox.StandardButton.Ok:
                    self.start()

def center(widget):
    'Return center coordinates for a given widget'
    
    fr = widget.frameGeometry()
    cp = widget.screen().availableGeometry().center()

    qr.moveCenter(cp)
    qr.topLeft()

    return qr.topLeft()