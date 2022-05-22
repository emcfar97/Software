from PyQt5.QtWidgets import QApplication

from GUI.slideshow import Slideshow
    
paths = [
    r"E:\Users\Emc11\Dropbox\ん\bd\12\bd12888ec1548ef0af7e5d6f87ba9f22.gif", 
    r"E:\Users\Emc11\Dropbox\ん\28\49\284936fd8f83c61bdb04bc7a4ed3385f.gif", 
    r"E:\Users\Emc11\Dropbox\ん\a0\7c\a07cc1a653a47ac90dbd394c1ebefbaa.gif"
    ]

Qapp = QApplication([])

app = Slideshow()

Qapp.exec_()
