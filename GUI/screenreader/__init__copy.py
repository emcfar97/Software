import pytesseract, requests, cv2, textwrap, qimage2ndarray
import numpy as np
from os import getenv
from difflib import SequenceMatcher
from dotenv import load_dotenv, set_key

from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import Qt, QTimer, QThreadPool
from PyQt6.QtGui import QPixmap

from GUI import Worker

load_dotenv(r'GUI\.env')
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
IMAGE = r'GUI\screenreader\image.jpg'
MASK = r'GUI\screenreader\mask.jpg'
AUTH_KEY = getenv('AUTH_KEY')

TEXTWRAP = 50
AUTHORIZATION = f'DeepL-Auth-Key {AUTH_KEY}'
TARGET_LANG = 'EN'

ORG = (40, 60)
FONTSCALE = 1.25
THICKNESS = 2
FONT = cv2.FONT_HERSHEY_TRIPLEX
COLOR = (25, 25, 0)

'https://api-free.deepl.com/v2/usage'

class ScreenReader(QLabel):
    
    def __init__(self, parent=None):
        
        super(ScreenReader, self).__init__()
        self.setWindowTitle('Screen Reader')
        self.parent = parent
        self.wrapper = textwrap.TextWrapper(TEXTWRAP)
        self.pixmap = QPixmap()
        self.text = ''
        self.translation = ''
        self.configure_gui()
        self.create_widgets()
        
        self.show()
    
    def configure_gui(self):
        
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.screen = QApplication.primaryScreen()
        geometry = self.screen.geometry()
        
        self.setGeometry(
            int(geometry.width() * .17), int(geometry.height() * .74),
            int(geometry.width() * .63), int(geometry.height() * .25)
            )
        self.setMinimumSize(
            int(geometry.width() * .10), int(geometry.height() * .10)
            )
        
        # self.setStyleSheet('''
        #     background: transparent;
        #     ''')
        
    def create_widgets(self):
        
        self.threadpool = QThreadPool(self)
        self.capture_timer = QTimer(self)
        self.capture_timer.setInterval(750)
        self.capture_timer.timeout.connect(self.capture_screen)
        self.capture_timer.start()
        
    def extract_text(self):
         
        image = self.pixmap_to_array(self.pixmap)
        mask = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        mask = cv2.threshold(
            mask, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
            )[1]
        mask = cv2.GaussianBlur(mask, (11, 11), 1)
                
        # get horizontal mask of large size since text are horizontal components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 13))
        connected = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        cnts = cv2.findContours(
            connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        for num, c in enumerate(cnts):
            
            x, y, w, h = cv2.boundingRect(c)
            ROI = image[y:y+h, x:x+w]
            # ROI = cv2.GaussianBlur(ROI, (25, 25), 0)
            text = pytesseract.image_to_string(ROI, lang='jpn')
            # text = text.replace(' ', '')
            print(text)
            
        # similarity = SequenceMatcher(None, self.text, text)

        # if similarity.ratio() < 0.80 and text:
            
        #     self.text = text
            
        #     # self.translation = self.translate_text()
        #     self.translation = text#"But I was quite the opposite, I was frustrated in front of the chancellor's office."
            
        # # self.replace_text(image, self.translation)
        self.capture_timer.start()
        
    def translate_text(self):
        
        request = requests.get(
            'https://api-free.deepl.com/v2/usage', 
            headers={'Authorization': 'c4cf117f-65c2-7664-1a2f-0d3be677b4da:fx'},
            )
        
        return request['translations'][0]['text']
        
    def replace_text(
        self, image_rgb, label, top_left_xy,
        font_scale, font_thickness, 
        font_face, font_color_rgb,
        bg_color_rgb=None, outline_color_rgb=(255, 255, 255),
        line_spacing=2
        ):
        """
        Adds text (including multi line text) to images.
        You can also control background color, outline color, and line spacing.

        outline color and line spacing adopted from: https://gist.github.com/EricCousineau-TRI/596f04c83da9b82d0389d3ea1d782592
        """
        OUTLINE_FONT_THICKNESS = 3 * font_thickness

        im_h, im_w = image_rgb.shape[:2]

        for line in self.wrapper.wrap(label):
            
            x, y = top_left_xy

            # ====== get text size
            if outline_color_rgb is None:
                get_text_size_font_thickness = font_thickness
            else:
                get_text_size_font_thickness = OUTLINE_FONT_THICKNESS

            (line_width, line_height_no_baseline), baseline = cv2.getTextSize(
                line,
                font_face,
                font_scale,
                get_text_size_font_thickness,
                )
            line_height = line_height_no_baseline + baseline

            if bg_color_rgb is not None and line:
                # === get actual mask sizes with regard to image crop
                if im_h - (y + line_height) <= 0:
                    sz_h = max(im_h - y, 0)
                else:
                    sz_h = line_height

                if im_w - (x + line_width) <= 0:
                    sz_w = max(im_w - x, 0)
                else:
                    sz_w = line_width

                # ==== add mask to image
                if sz_h > 0 and sz_w > 0:
                    bg_mask = np.zeros((sz_h, sz_w, 3), np.uint8)
                    bg_mask[:, :] = np.array(bg_color_rgb)
                    image_rgb[
                        y : y + sz_h,
                        x : x + sz_w,
                    ] = bg_mask

            # === add outline text to image
            if outline_color_rgb is not None:
                image_rgb = cv2.putText(
                    image_rgb,
                    line,
                    (x, y + line_height_no_baseline),  # putText start bottom-left
                    font_face,
                    font_scale,
                    outline_color_rgb,
                    OUTLINE_FONT_THICKNESS,
                    cv2.LINE_AA,
                )
            # === add text to image
            image_rgb = cv2.putText(
                image_rgb,
                line,
                (x, y + line_height_no_baseline),  # putText start bottom-left
                font_face,
                font_scale,
                font_color_rgb,
                font_thickness,
                cv2.LINE_AA,
            )
            top_left_xy = (x, y + int(line_height * line_spacing))

        return image_rgb
        
    def pixmap_to_array(self, pixmap):
                
        return qimage2ndarray.rgb_view(pixmap.toImage())
    
    def mse(self, img1, img2):
        
        img1 = self.pixmap_to_array(img1)
        img2 = self.pixmap_to_array(img2)
        
        try: diff = cv2.subtract(img1, img2)
        except: return 100
        
        h, w = img1.shape[:2]
        err = np.sum(diff**2)
        
        return err / (float(h * w))

    def capture_screen(self):
        
        self.setWindowOpacity(0)
        pixmap = self.screen.grabWindow(0, *self.geometry().getRect())
        self.setWindowOpacity(1)
        
        if self.pixmap.isNull() or (self.mse(self.pixmap, pixmap) > 5):
            
            # self.capture_timer.stop()
            self.pixmap = pixmap 
            self.setPixmap(pixmap)
            self.extract_text()
    
    def moveEvent(self, event): self.capture_screen()
    
    def keyPressEvent(self, event):

        key_press = event.key()
        # modifiers = event.modifiers()
        # alt = modifiers == Qt.AltModifier
                        
        if key_press == Qt.Key_Escape: self.close()