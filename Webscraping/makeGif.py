import os, imageio, cv2
import numpy as np
from os.path import join
from PIL import Image

def make_gif(path, name, error=False):

    image = Image.open(join(path, f'{name}.jpg'))
    corners = find_corners(join(path, f'{name}.jpg'))
    images = [
        image.crop((*corner[0], *corner[1]))
        for corner in zip(corners[0][:24], corners[1][:24])
        ]
    os.mkdir(join(path[:-6], name))
    for num, image in enumerate(images, 1):
        image.save(join(path[:-6], name, f'{name}_{num:02d}.jpg'))
    imageio.mimsave(join(path[:-6], f'{name}.gif'), images, duration=.20)
    
def find_corners(path):

    def find_row(row):
        
        above = gray.shape[1] - np.count_nonzero(gray[row-1])
        center= gray.shape[1] - np.count_nonzero(gray[row])
        below = gray.shape[1] - np.count_nonzero(gray[row+1])
        
        return (
            above<center and above<below and below!=0 and above<1,
            below<center and below<above and above!=0 and below<1
            )

    def find_col(row, col, span=20):

        rght = 2*span - np.count_nonzero(gray[row-span:row+span,col-1])
        midd = 2*span - np.count_nonzero(gray[row-span:row+span,col])
        left = 2*span - np.count_nonzero(gray[row-span:row+span,col+1])
        
        return (
            rght<midd and rght<left and left!=0 and rght<=1,
            left<midd and left<rght and rght!=0 and left<=1
            )

    corners = [], []
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C, 
        cv2.THRESH_BINARY, 21, 4
        )
     
    for row in range(1, gray.shape[0]-1):

        top, bot = find_row(row)
        if top or bot:
            
            for col in range(1, gray.shape[1]-1):
              
                rght, left = find_col(row, col)
                if rght and top: corners[0].append([col, row])
                elif left and bot: corners[1].append([col, row])
        
    return corners

path = r'C:\Users\Emc11\Downloads\Error'

for image in os.listdir(path)[::-1]:
    if image.endswith('ini'): continue
    print(image, '\n')
    try: make_gif(path, image[:-4])
    except: continue

