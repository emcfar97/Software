import argparse
from PyQt6.QtWidgets import QApplication
from . import App

parser = argparse.ArgumentParser(
    prog='GUI', 
    description=''
    )
parser.add_argument(
    '-p', '--program', type=int,
    help='argument', default=None
    )
parser.add_argument(
    '-a', '--admin', type=bool,
    help='Is admin',
    default=0
    )

args = parser.parse_args()

match args.program:
    
    case 0: 
        
        from GUI.deeplearning import __main__
        
    case 1:
        
        from GUI.managedata import __main__
        
    case 2:
        from GUI import GestureDraw
        GestureDraw()
        
    case 3:
        
        from GUI.slideshow import __main__
        
    case 4:
        
        from GUI.videosplitter import __main__
        
    case _:

        Qapp = QApplication([])

        app = App()
        Qapp.setQuitOnLastWindowClosed(False)
        Qapp.setStyleSheet(
            "QMessageBox { messagebox-text-interaction-flags: 5; }"
            )

        Qapp.exec()