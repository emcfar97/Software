from PyQt5.QtWidgets import QApplication

from GUI.uploadmedia import UploadMedia

Qapp = QApplication([])

app = UploadMedia()

Qapp.exec_()
