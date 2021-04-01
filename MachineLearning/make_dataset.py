
def Get_images_dataset():

    import tempfile, hashlib   
    from math import log
    from PIL import Image 
    from pathlib import Path
    from cv2 import VideoCapture, imencode, cvtColor, COLOR_BGR2RGB

    HASHER = hashlib.md5()

    def save_images(path, dest, gray_=False, crop_=False):
        
        for file in path:
            
            # if len(list(dest.glob('*'))) > 100500: break
            
            try:
                
                if file.suffix in (('.jpeg', '.jpg', '.png')): images = [file]
                
                elif file.suffix in (('.gif', '.mp4', '.webm', '.mp4')):
                    
                    images = []
                    temp_dir = tempfile.TemporaryDirectory()
                    vidcap = VideoCapture(str(file))
                    success, frame = vidcap.read()
            
                    while success:
                        
                        data = imencode('.jpg', frame)[-1]
                        HASHER.update(data)
                        temp = Path(temp_dir.name) / f'{HASHER.hexdigest()}.jpg'
                        temp.write_bytes(data)
                        images.append(temp)
                        success, frame = vidcap.read()

                    else: 
                        step = round(90 * log((len(images) * .0007) + 1) + 1)
                        images = images[::step]
                
                for file in images:
                    
                    image = Image.open(file)
                    if gray_: image, file = gray(image, file)
                    if crop_: image = crop(image)
                    image.thumbnail([512, 512])
                    image.save(dest / file.name)
                
            except: continue


    def crop(image):
        
        standard = image.height if image.height < image.width else image.width
        standard //= 2
        center = image.size[0] // 2, image.size[1] // 2
        
        left = center[0] - standard
        upper = center[1] - standard
        right = center[0] + standard
        lower = center[1] + standard

        return image.crop((left, upper, right, lower))
    
    def gray(image, file):
        
        image = image.convert('L')
        HASHER.update(image.tobytes())
        name = file.with_name(HASHER.hexdigest() + file.suffix)
        
        return image, name
    
    dests = [
        Path(r'E:\Users\Emc11\Training\Medium\3-Dimensional'),
        ]

    num = 0
    path = [file for file in Path(r'E:\Users\Emc11\Training\3-Dimensional').iterdir()]
    save_images(path, dests[num])
