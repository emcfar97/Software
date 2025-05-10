import argparse
from PyQt6.QtWidgets import QApplication

from GUI.managedata import ManageData

parser = argparse.ArgumentParser(
    prog='Manage Database', 
    description='Manage Database arguments'
    )
parser.add_argument(
    '-a', '--admin', type=bool,
    help='Is admin',
    default=0
    )
args = parser.parse_args()

Qapp = QApplication([])

app = ManageData(None, args.admin)
Qapp.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")

Qapp.exec()