if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication
    from GUI import *

    Qapp = QApplication([])

    app = ManageData()

    Qapp.exec_()