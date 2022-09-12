import piexif, bs4, requests, re, tempfile, hashlib, ast, json
from . import ROOT, USER, EXT
from math import log
from io import BytesIO
from ffprobe import FFProbe
from imagehash import dhash
from progress.bar import IncrementalBar
from PIL import Image, GifImagePlugin, UnidentifiedImageError, ImageFile
from cv2 import VideoCapture, imencode, cvtColor, COLOR_BGR2RGB, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES

ImageFile.LOAD_TRUNCATED_IMAGES = True
PATH = USER / r'Dropbox\ん'
RESIZE = [1320, 1000]
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0'
    }

data = json.load(open(r'Webscraping\constants.json', encoding='utf-8'))

METADATA = data['METADATA']
GENERAL = data['GENERAL']
CUSTOM = data['CUSTOM']
RATING = data['RATING']
ARTIST = data['ARTIST']
REMOVE = set(data['REMOVE'])
REPLACE = data['REPLACE']

def save_image(name, image=None, exif=b''):
    '''Save image to name (with optional exif metadata)'''

    try:
        if re.search('jp.*g|png', name.suffix):

            name = name.with_suffix('.webp')
            
            if image:
                img = Image.open(BytesIO(
                    requests.get(image, headers=HEADERS).content
                    ))
                img.thumbnail(RESIZE)
                
            else: img = Image.open(name)    
            
            img = img.convert('RGB')
            img.save(name, 'webp', exif=exif)

        elif re.search('gif|webm|mp4', name.suffix):
            
            name.write_bytes(
                requests.get(image, headers=HEADERS).content
                )
    
    except UnidentifiedImageError: return False
    except OSError as error:
        if 'trunc' not in error.args:
            try: img.save(name.with_suffix('.gif'))
            except: pass
    except: pass
    
    return name.exists()

def get_name(path, hasher=1):
    '''Return pathname (from optional hash of image)'''
    
    stem = path

    if hasher:
        if isinstance(path, str):
            data = requests.get(path, headers=HEADERS).content
        else: data = path.read_bytes()
        hasher = hashlib.md5(data)

        stem = f'{hasher.hexdigest()}.{re.findall(EXT, str(path), re.IGNORECASE)[0]}'
    
    return PATH / stem[0:2] / stem[2:4] / stem.lower().replace('jpeg','jpg')

def get_hash(image, src=False):
    '''Return perceptual hash of image'''
        
    if src:
        
        try:
            image = Image.open(
                BytesIO(requests.get(image, headers=HEADERS).content)
                )
        except: return None
    
    elif re.search('jp.*g|png|gif', image.suffix, re.IGNORECASE): 
        
        try: image = Image.open(image)
        except: return None

    elif re.search('webm|mp4', image.suffix, re.IGNORECASE):
        
        try:
            video_capture = VideoCapture(str(image)).read()[-1]
            image = cvtColor(video_capture, COLOR_BGR2RGB)
            image = Image.fromarray(image)
        except: return None
    
    image.thumbnail([32, 32])
    image = image.convert('L')

    return f'{dhash(image)}'

def video_generator(path, step=1):
    
    temp_dir = tempfile.TemporaryDirectory()
    vidcap = VideoCapture(str(path))
    success, frame = vidcap.read()
        
    while success:
            
        if (vidcap.get(CAP_PROP_POS_FRAMES) % step) == 0:
            
            temp = ROOT.parent / temp_dir.name / f'{next(tempfile._get_candidate_names())}.jpg'
            temp.write_bytes(imencode('.jpg', frame)[-1])
            yield temp
            
        success, frame = vidcap.read()
    
    else:
        temp_dir.cleanup()
        vidcap.release()

def get_tags(driver, path, filter=False):

    tags = set()
    frames = []
    video = path.suffix in ('.gif', '.webm', '.mp4')

    if video:

        tags.add('animated')
        
        if path.suffix in ('.webm', '.mp4'):
            try:
                for stream in FFProbe(str(path)).streams:
                    if stream.codec_type == 'audio':
                        tags.add('audio')
                        break
            except: pass

            vidcap = VideoCapture(str(path))
            frame_count = int(vidcap.get(CAP_PROP_FRAME_COUNT))
            vidcap.release()
        
        elif path.suffix in ('.gif'):
            
            gifcap = GifImagePlugin.GifImageFile(str(path))
            frame_count = gifcap.n_frames
            gifcap.close()
            
        step = 90 * log((frame_count * .002) + 1) + 1
        frames = video_generator(path, round(step))
        
    else: frames.append(path)
    
    for frame in frames:

        driver.get('http://dev.kanotype.net:8003/deepdanbooru/')
        driver.find('//*[@id="exampleFormControlFile1"]', str(frame))
        driver.find('//button[@type="submit"]', click=True)

        for _ in range(4):
            html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
            try:
                tags.update([
                    tag.text for tag in html.find('tbody').findAll(href=True)
                    ])
                break
            except AttributeError:
                if driver.current_url().endswith('deepdanbooru/'):
                    driver.find('//*[@id="exampleFormControlFile1"]',str(frame))
                    driver.find('//button[@type="submit"]', click=True)
                driver.refresh()
    
    if filter: tags.difference_update(REMOVE)
    
    return ' '.join(tags)

def generate_tags(general, metadata=0, custom=0, artists=[], rating=0, exif=1):
    
    tags = ['qwd']

    if general:
        
        tags.extend(
            key for key in GENERAL if evaluate(general, GENERAL[key])
            )
    if metadata:
        
        tags.extend(
            key for key in METADATA if evaluate(metadata, METADATA[key])
            )
    if custom:
        
        tags.extend(
            key for key in CUSTOM if evaluate(general, CUSTOM[key])
            )
    if rating:
        
        tags = set(tags + general.split())
        rating = [
            key for key in RATING if evaluate(
                f' {" ".join(tags)} ', RATING[key]
                )
            ]
    
    if exif:
        
        custom = tags.copy()
        custom.remove('qwd')
        
        zeroth_ifd = {
            piexif.ImageIFD.XPKeywords: [
                byte for char in '; '.join(custom) 
                for byte in [ord(char), 0]
                if 0 <= byte <= 255
                ],
            piexif.ImageIFD.XPAuthor: [
                byte for char in '; '.join(artists) 
                for byte in [ord(char), 0]
                if 0 <= byte <= 255
                ]
            }
        exif_ifd = {piexif.ExifIFD.DateTimeOriginal: u'2000:1:1 00:00:00'}
        
        exif = piexif.dump({"0th":zeroth_ifd, "Exif":exif_ifd})
        rating.append(exif)
    
    tags = " ".join(tags)
    for key, value in REPLACE.items():
        tags = re.sub(f' {key} ', f' {value} ', tags)
    else: tags = tags.replace('-', '_')

    return [tags] + rating if rating else tags

def evaluate(tags, pattern):
    
    if re.search('AND|OR|NOT', pattern):
        query = tuple(pattern.replace('(', '( ').replace(')', ' )').split(' '))
        query = str(query).replace("'(',", '(').replace(", ')'", ')')
        query = query.replace('<','(').replace('>',')')
        # query = re.sub('(\w+)', r'"\1",', pattern)
        # query = re.sub('(\([^(\([^()]*\))]*\))', r'\1,', query)
        # # query = re.sub('([))])', '),),', query)
        query = ast.literal_eval(query)
                
        return parse(tags.split(), query)

    else: return re.search(f' ({pattern}) ', tags)

def parse(tags, search):
    
    if (len(search) == 1) and isinstance(search[0], tuple): search, = search
    
    elif all(op not in search for op in ['AND','OR','NOT']):
        if isinstance(search, str): return search in tags
        else: return search[0] in tags

    if 'AND' in search: 
        num = search.index('AND')
        return parse(tags, search[:num]) and parse(tags,search[num+1:])
    
    elif 'OR' in search: 
        num = search.index('OR')
        return parse(tags, search[:num]) or parse(tags, search[num+1:])
    
    elif 'NOT' in search: return not parse(tags, search[1])