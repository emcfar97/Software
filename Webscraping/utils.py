import requests, re, tempfile, json, ffmpeg, warnings
from . import ROOT, USER, TOKEN, get_token
from math import log
from io import BytesIO
from hashlib import md5
from ffprobe import FFProbe
from ffprobe.exceptions import FFProbeError
from imagehash import dhash
from ast import literal_eval
from progress.bar import IncrementalBar
from deepdanbooru_onnx import DeepDanbooru
from PIL import Image, ImageFile, GifImagePlugin, UnidentifiedImageError
from cv2 import VideoCapture, imencode, cvtColor, COLOR_BGR2RGB, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES

warnings.simplefilter('ignore', Image.DecompressionBombWarning)
ImageFile.LOAD_TRUNCATED_IMAGES = True
PATH = USER / r'Dropbox\ん'
RESIZE = [1320, 1320]
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0'
    }
MODEL = DeepDanbooru(
    tags_path=r'MachineLearning\general-tags.txt', threshold=0.475
    )
EXT = 'jpe?g|png|webp|gif|mp4|webm'

data = json.load(open(r'Webscraping\constants.json', encoding='utf-8'))

METADATA = data['METADATA']
GENERAL = data['GENERAL']
CUSTOM = data['CUSTOM']
RATING = data['RATING']
ARTIST = data['ARTIST']
REMOVE = set(data['REMOVE'])
REPLACE = data['REPLACE']

def save_image(name, image=None, web_format=True):
    '''Save image to name (with optional exif metadata)'''

    try:
        if re.search('jp.*g|png|bmp|webp', name.suffix):
            
            if image:
                
                if web_format:
                    
                    webp = name.with_suffix('.webp')
                    ffmpeg.input(image).output(str(webp), loglevel="error").run(
                        overwrite_output=True, capture_stdout=True, capture_stderr=True
                        )
                    # name = name.replace(webp)
                    img = Image.open(webp)
                    img.thumbnail(RESIZE)
                    img.save(name)
                
                else:
                    img = Image.open(BytesIO(
                        requests.get(image, headers=HEADERS).content
                        ))
                    img.thumbnail(RESIZE)
                    img.save(name)
                
            else:
                
                img = Image.open(name)
                img.save(name)
        
            img.close()
        
        elif re.search('gif|mp4|webm', name.suffix):
            
            if '//redgif' in str(image): image = get_redgif(name.name)
                
            if web_format:
                
                webm = name.with_suffix('.webm')
                ffmpeg.input(image).output(str(webm), vcodec='vp9', loglevel="error").run(
                    overwrite_output=True, capture_stdout=True, capture_stderr=True
                    )
                name = name.replace(webm)
                
            else:
                
                name.write_bytes(
                    requests.get(image, headers=HEADERS).content
                    )
                    
    except UnidentifiedImageError: return False
    
    except PermissionError: return False
    
    except OSError as error:
        
        if error.errno == 22:
            
            print('\n', image)
            return False
        
        else: raise error
        # if 'trunc' not in error.args:
        #     try: img.save(name.with_suffix('.gif'))
        #     except: pass
            
    except ffmpeg.Error as error:
        
        if b'-10054' in error.stderr:
            
            print('\n', image)
            return True
        
        elif b'25643' in error.stderr:
            
            name.write_bytes(requests.get(image).content)
            return name.exists()
    
        print(error.stderr)
        return False
    
    return name.exists()

def get_redgif(name):
    "Use redgif API to download a url's contents to the specified name"
    
    global TOKEN
    url = f'https://api.redgifs.com/v2/gifs/{name}'

    request = requests.get(
        url, headers={'Authorization': f'Bearer {TOKEN}'}
        )
    raw_data = request.json()
    
    if 'error' in raw_data:
        
        match raw_data['error']['code']:
            
            case 'TokenDecodeError':
            
                globals()['TOKEN'] = get_token()
                request = requests.get(
                    url, headers={'Authorization': f'Bearer {TOKEN}'}
                    )
                hd_video_url = request.json()['gif']['urls']['hd']
        
            case 'Gone' | 'NotFound':
            
                return None
        
    else: hd_video_url = raw_data['gif']['urls']['hd']
        
    return hd_video_url

def get_name(path, hasher=1):
    '''Return pathname (from optional hash of image)'''
    
    if isinstance(path, str): 
        suffix = '.' + re.findall(EXT, path)[0]
    else: suffix = path.suffix

    if suffix in ('.jpg', '.jpeg', '.png', '.bmp'): suffix = '.webp'
    elif suffix in ('.gif', '.mp4'): suffix = '.webm'

    if hasher:
        
        if isinstance(path, str):
            data = requests.get(path, headers=HEADERS).content
        else: data = path.read_bytes()
        hasher = md5(data)

        path = f'{hasher.hexdigest()}{suffix}'
        
    else:
        path = f'{path.split(".")[0]}{suffix}'
    
    return PATH / path[0:2] / path[2:4] / path

def get_hash(image, src=False):
    '''Return perceptual hash of image'''
       
    if src:
        
        try:
            image = Image.open(
                BytesIO(requests.get(image, headers=HEADERS).content)
                )
        except: return None
    
    elif re.search('jp.*g|png|webp|gif', image.suffix, re.IGNORECASE):
        
        try: image = Image.open(image)
        except: return None

    elif re.search('webm|mp4', image.suffix, re.IGNORECASE):
        
        try:
            video_capture = VideoCapture(str(image)).read()[-1]
            image = cvtColor(video_capture, COLOR_BGR2RGB)
            image = Image.fromarray(image)
        except: return None
    
    else: raise TypeError
    
    image.thumbnail([32, 32])
    image = image.convert('L')

    return f'{dhash(image)}'

def frame_generator(path, temp_dir=None, step=1):
    
    cleanup = temp_dir
    
    if temp_dir is None: 
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
        vidcap.release()
        if cleanup is None: temp_dir.cleanup()

def get_tags(path, filter=False):

    tags=set()
    
    if path.suffix in ('.gif', '.webm', '.mp4'):

        frames = []
        tags.add('animated')
        temp_dir = tempfile.TemporaryDirectory()
        data = FFProbe(str(path)).streams
        
        try:
            video = data[0]
            
            if hasattr(video, 'TAG:DURATION'):

                duration = dict(video.__dict__)['TAG:DURATION'].split(':')
                duration = sum(
                    float(x) * 60 ** i for i, x in enumerate(reversed(duration))
                    )
                
            elif hasattr(video, 'duration'):
                
                try: duration = video.duration_seconds()

                except: duration = float(video.duration)

            if duration <= 5: tags.add('looping_video')
            elif 5  <  duration <= 180: tags.add('short_video')
            elif 180 < duration <= 600: tags.add('medium_video')
            elif 600 < duration: tags.add('long_video')
            
        except (TypeError, ValueError): pass
        
        if path.suffix in ('.webm', '.mp4'):
            try:
                for stream in data:
                    if stream.codec_type == 'audio':
                        tags.add('audio')
                        break
            except: pass
            
            try: frame_count = video.frames()
            except FFProbeError:
                vidcap = VideoCapture(str(path))
                frame_count = int(vidcap.get(CAP_PROP_FRAME_COUNT))
                vidcap.release()
        
        elif path.suffix in ('.gif'):
            
            gifcap = GifImagePlugin.GifImageFile(str(path))
            frame_count = gifcap.n_frames
            gifcap.close()
        
        if frame_count <= 0: frame_count = video.framerate
        
        step = 90 * log((frame_count * .002) + 1) + 1
        frames = list(frame_generator(path, temp_dir, round(step)))

        tags.update(*[set(i) for i in MODEL(frames)])
        temp_dir.cleanup()
    
    else: tags = set(MODEL(str(path)))
    
    if filter: tags.difference_update(REMOVE)
    
    return ' '.join(tags)

def generate_tags(general, metadata=0, custom=0, rating=0):
    
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
        
        tags = list(set(tags + general.split()))
        rating = [
            key for key in RATING if evaluate(
                f' {" ".join(tags)} ', RATING[key]
                )
            ]
    
    tags = " ".join(sorted(tags)).replace('-', '_')
    for key, value in REPLACE.items():
        tags = re.sub(f' {value} ', f' {key} ', tags)
        if re.match('( _)|(_ )|(__)', tags): print(tags, value, key); raise
    
    return [tags] + rating if rating else tags

def evaluate(tags, pattern):
    
    if re.search('AND|OR|NOT', pattern):
        query = tuple(pattern.replace('(', '( ').replace(')', ' )').split(' '))
        query = str(query).replace("'(',", '(').replace(", ')'", ')')
        query = query.replace('<','(').replace('>',')')
        # query = re.sub('(\w+)', r'"\1",', pattern)
        # query = re.sub('(\([^(\([^()]*\))]*\))', r'\1,', query)
        # # query = re.sub('([))])', '),),', query)
        query = literal_eval(query)
                
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