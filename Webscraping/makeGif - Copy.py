import os, imageio, cv2
import numpy as np
from os.path import join
from PIL import Image

def make_gif(name, path, image1, image2):
    
    image = Image.new('RGB', (image1.width, image1.height + image2.height))
    image.paste(image1);  image.paste(image2, (0, image1.height))
    find_corners(image); return
    images = [
        np.asarray(image.crop((*corner[0], *corner[1])))
        for corner in zip(*find_corners(image))
        ] 
    # try:
    imageio.mimsave(join(path, name), images, duration=.20)
    # except Exception as error:

        # print('Error:', str(error))
        # os.mkdir(join(path, name[:-4]))
        # for num, image in enumerate(images, 1):
        #     image.save(
        #         join(path, name[:-4], '{}_{:02d}.jpg'.format(name[:-4], num))
        #         )

def find_corners(image, thresh=244):

    def find_limits():

        row, col = corners[0]
        rows = sum(1 for i in corners if row-15 < i[0] <= row+15)//2
        cols = sum(1 for i in corners if i[1]==col)//2

        return [cols, rows]

    img = np.asarray(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray[gray < thresh] = 0   
    gray[gray >= thresh] = 255
    gray = np.float32(gray)

    dst = cv2.cornerHarris(gray,8,3,0.04)
    dst = cv2.dilate(dst, None)
    dst = cv2.threshold(dst, 0.01*dst.max(), 255,0)
    dst = np.uint8(dst[-1])
    stats = cv2.connectedComponentsWithStats(dst)
    
    img[dst>0.01*dst.max()]=[0,0,255]
    cv2.write('', img)
    # corners = np.int0(stats[-1])[1:]
    # limits = find_limits()
    # width =  corners[2][0] - corners[0][0]
    # height =  corners[4*limits[0]][1] - corners[0][1]
    # corners =  [
    #     [
    #         [corners[0][0] + i*width, corners[1][1] + j*height]
    #         for j in range(limits[1]) for i in range(limits[0])
    #     ][:24],
    #     [
    #         [corners[2*limits[0]+1][0] + i*width,
    #         corners[2*limits[0]+1][1] + j*height] 
    #         for j in range(limits[1]) for i in range(limits[0])
    #     ][:24]
    # ]
    # return corners

path = r'C:\Users\Emc11\Downloads\Error'

for image in os.listdir(path):
    if image.endswith('contacta.jpg'):
        print(image, '\n')
        image_a = Image.open(join(path, image))
        image_b = Image.open(join(path, image.replace('a.', 'b.')))
        make_gif(f'{image[:-12]}.gif', rf'{path[:-6]}\test', image_a, image_b)
