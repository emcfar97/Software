import argparse

parser = argparse.ArgumentParser(
    prog='GUI Applications', 
    description='GUI app arguments'
    )
parser.add_argument(
    '-p', '--program', type=int,
    help='argument', default=None
    )
parser.add_argument(
    '-a', '--args', type=bool,
    help='Arguments for specific program',
    default=0
    )

args = parser.parse_args()

match args.program:
    
    case 0: 
        
        from .deeplearning import __main__
        
    case 1:
        
        from .managedata import __main__
        
    case 2:
        from . import GestureDraw
        GestureDraw()
        
    case 3:
        
        from .slideshow import __main__
        
    case 4:
        
        from .videosplitter import __main__
        
    case _:

        from PyQt6.QtWidgets import QApplication
        from . import App
        
        Qapp = QApplication([])

        app = App()
        Qapp.setQuitOnLastWindowClosed(False)
        Qapp.setStyleSheet(
            "QMessageBox { messagebox-text-interaction-flags: 5; }"
            )

        Qapp.exec()