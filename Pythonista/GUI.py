import ui, socket
from iPhoneGUI import *
#h = socket.gethostname()
#print(socket.gethostbyname(h))
import mysql.connector as sql

# DATAB = sql.connect(
#    user='root', password='SchooL1@', 
#    database='userData', host='192.168.1.43'
#    )
#CURSOR = DATAB.cursor()
#TEST = 'SELECT src, tags, artist, rating, stars FROM imageData ORDER BY RAND() LIMIT 10'
TEST = 'SELECT src FROM imageData WHERE path LIKE ".jp%g" ORDER BY RAND() LIMIT 50'

class model(object):
    
    def __init__(self):
        
        self.images = []
        
    @ui.in_background
    def populate(self, images):
        
        self.images = images
    
    def tableview_number_of_sections(self, tableview):
        # Return the number of sections (defaults to 1)
        return 1

    def tableview_title_for_header(self, tableview, section):
        
        return #'placeholder'

    def tableview_can_delete(self, tableview, section, row):
        
        return True

    def tableview_can_move(self, tableview, section, row):
        
        return False

    def tableview_delete(self, tableview, section, row):
        cell = tableview[row]
        print(cell)

    def tableview_move_row(self, tableview, from_section, from_row, to_section, to_row):
        # Called when the user moves a row with the reordering control (in editing mode).
        pass
    
    def tableview_number_of_rows(self, tv, s):
        
        return len(self.images)
        
    def tableview_cell_for_row(self, tv, s, r):
        
        cell = ui.TableViewCell()
        cell.image_view = ui.Image.named('iob:ios7_cloud_download_outline_24')
        cell.text_label.text = self.images[r]
        return cell

def setup(): 
    
    table.data_source = model()
    table.data_source.populate(
        [str(hash(i)) for i in range(50)]
        )
    view.present('sheet')

def parse(sender): 
    
    print(sender)
    return
    
    CURSOR.execute(TEST)
    table.data_source.populate(CURSOR.fetchall())

def f(sender): print('action')
def g(sender): print('edit')
def h(sender): print('accessory')

def push_to(sender): nav.push_view(sender)

nav = ui.NavigationView(main_view)
setup()
