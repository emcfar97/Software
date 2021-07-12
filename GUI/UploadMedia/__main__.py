from PyQt5.QtWidgets import QApplication

from GUI.UploadMedia import UploadMedia

Qapp = QApplication([])

app = UploadMedia()

Qapp.exec_()
