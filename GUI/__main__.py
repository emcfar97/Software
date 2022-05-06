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

args = parser.parse_args()

match args.program:
    
    case 0: 
        
        from GUI.machinelearning import __main__
        
    case 1:
        
        from GUI.managedata import __main__
        
    case 2:
        print(2)
        
    case 3:
        
        from GUI.slideshow import __main__
        
    case 4:
        
        from GUI.videosplitter import __main__
        
    case _:

        Qapp = QApplication([])

        app = App()
        Qapp.setQuitOnLastWindowClosed(False)

        Qapp.exec()