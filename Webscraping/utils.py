import imagehash, piexif, bs4, requests, re, tempfile, hashlib, sys, ast
from . import ROOT
from math import log
from PIL import Image
from io import BytesIO
from cv2 import VideoCapture, imencode, cvtColor, COLOR_BGR2RGB

PATH = ROOT / r'\Users\Emc11\Dropbox\Videos\ん'
TYPE = ['エラティカ ニ', 'エラティカ 三', 'エラティカ 四']
RESIZE = [1320, 1000]
HEADERS = {
    'User-Agent': 'Mozilla/5.0'
    }
HASHER = hashlib.md5()
EXT = 'jp.*g|png|gif|webp|webm|mp4'

METADATA = {
    'audio':'audio|has_audio',
    '3d_cg': '3d'
    }
GENERAL = {
    'age_difference': 'age_difference|teenage_girl_and_younger_boy',
    'bottomless': 'bottomless AND NOT (topless OR nude)', 
    'condom': 'condom', 
    'cowgirl_position': 'cowgirl_position|reverse_cowgirl_position', 
    'cum': 'cum|precum|semen',
    'dancing': 'dancing|dancer', 
    'gesugao': 'crazy_smile|crazy_eyes|gesugao', 
    'girl_on_top': 'girl_on_top',
    'japanese_clothes': 'yamakasa|tabi|sarashi|fundoshi|hakama|short_yukata|yukata|short_kimono|kimono|geta|happi|zori',
    'male_focus': '(male_focus OR (solo AND 1boy) OR (1boy AND NOT (1girl OR 2girls OR 3girls OR 4girls OR multiple_girls)))',
    'muscular': '(solo OR (1girl AND NOT (1boy OR 2boys OR 3boys OR 4boys OR multiple_boys))) AND (muscular OR muscle OR muscular_female OR abs)', 
    'nude': 'nude AND NOT functionally_nude',
    'functionally_nude': '(functionally_nude OR (bottomless AND topless)) AND NOT nude', 
    'open_clothes': 'open_clothes|open_coat|open_jacket|open_shirt|open_robe|open_kimono|open_fly|open_shorts', 
    'orgasm': 'orgasm|ejaculation', 
    'piercings': 'piercings|earrings|navel_piercings|areola_piercing|back_piercing|navel_piercing|nipple_piercing|ear_piercing|eyebrow_piercing|eyelid_piercing|lip_piercing|nose_piercing|tongue_piercing|clitoris_piercing|labia_piercing|penis_piercing|testicle_piercing|nipple_chain', 
    'presenting': 'presenting OR top-down_bottom-up OR ((spread_legs OR spread_pussy) AND (trembling OR (heavy_breathing OR breath) OR (parted_lips AND NOT clenched_teeth))) OR spread_pussy', 
    'pussy': 'pussy|vagina', 
    'pussy_juice': 'pussy_juice|pussy_juices|pussy_juice_trail|pussy_juice_puddle|pussy_juice_stain|pussy_juice_drip_through_clothes', 
    'revealing_clothes': 'revealing_clothes|torn_clothes|micro_bikini|crop_top|pussy_peek|midriff|cleavage_cutout|wardrobe_malfunction|breast_slip|nipple_slip|areola_slip|no_panties|no_bra|pelvic_curtain|side_slit|breasts_outside|see-through|partially_visible_vulva|functionally_nude|breastless_clothes|bare_shoulders|one_breast_out',
    'sex': 'sex|vaginal|anal|facial|oral|fellatio|cunnilingus|handjob|frottage|tribadism|group_sex|hetero', 
    'sex_toys': 'sex_toys|vibrator|dildo|butt_plug|artificial_vagina',
    'solo': 'solo OR (1girl AND NOT (1boy OR 2boys OR 3boys OR 4boys OR multiple_boys)) OR (1boy AND NOT (1girl OR 2girls OR 3girls OR 4girls OR multiple_girls))', 
    'standing_sex': '(standing_on_one_leg OR (standing AND (leg_up OR leg_lift))) AND sex',
    'suggestive': 'sexually_suggestive OR (naughty_smile OR fellatio_gesture OR teasing OR blush OR spread_legs OR pulled_by_self OR lifted_by_self OR (come_hither OR beckoning) OR (tongue_out AND (open_mouth OR licking_lips)) OR (bent_over AND (looking_back OR looking_at_viewer)) OR (trembling OR (saliva OR sweat) OR ((heavy_breathing OR breath) OR (parted_lips AND NOT clenched_teeth))) OR (skirt_lift OR bra_lift OR dress_lift OR shirt_lift OR wind_lift OR breast_lift OR kimono_pull) AND NOT (vaginal OR anal OR sex OR erection OR aftersex OR ejaculation OR pussy OR penis))', 
    'suspended_congress': 'suspended_congress|reverse_suspended_congress',
    'topless': 'topless AND bare_shoulders AND NOT (bottomless OR nude)', 
    }
CUSTOM = {
    'aphorisms': '((((nipples OR nipple_slip OR areolae OR areola_slip OR breasts_outside OR no_bra) OR (no_panties OR pussy OR penis OR no_underwear))) AND ((shawl OR capelet OR cape OR shrug_<clothing> OR open_jacket OR bare_shoulders OR underboob OR corset OR breastless_clothes OR underbust) OR (sarong OR loincloth OR skirt OR pelvic_curtain OR showgirl_skirt OR belt OR japanese_clothes OR dress OR corset OR side_slit OR tabard))) OR (condom_belt OR leggings OR thighhighs OR thigh_boots) OR naked_clothes OR amazon_position OR nipple_chain', 
    'clothes_lift': 'clothes_lift|skirt_lift|shirt_lift|dress_lift|sweater_lift|bra_lift|bikini_lift|kimino_lift|apron_lift',
    'intercrural': 'thigh_sex',
    'loops': 'loops|thigh_strap|necklace|neck_ring|anklet|bracelet|armlet',  
    'naked_clothes': 'naked_belt|naked_apron|naked_shirt|naked_cape|naked_overalls|naked_ribbon|naked_cloak|naked_bandage|naked_robe', 
    'sexy': 'NOT (nude OR topless OR (bottomless OR no_panties))',
    'slender': '(solo OR (1girl AND NOT (1boy OR 2boys OR 3boys OR 4boys OR multiple_boys))) AND (slender OR NOT (((muscular OR muscle OR muscular_female OR toned OR abs) OR ((large_breasts OR huge_breasts OR gigantic_breasts) OR (plump OR fat) OR thick_thighs OR wide_hips OR huge_ass))))',
    'vagina': 'pussy',
    'underwear': 'underwear|panties|bra|briefs'
    }
RATING = {
    3: 'sex|hetero|vaginal|anal|cum|penis|vagina|pussy|pussy_juice|vaginal_juices|spread_pussy|erection|clitoris|anus|oral|fellatio|fingering|handjob|masturbation|object_insertion', 
    2: 'NOT (sex OR hetero OR vaginal OR anal OR cum OR penis OR vagina OR pussy OR pussy_juice OR vaginal_juices OR spread_pussy OR erection OR clitoris OR anus OR oral OR fellatio OR fingering OR handjob OR masturbation OR object_insertion) AND (nipples OR areola OR areolae OR covered_nipples OR cameltoe OR wedgie OR torn_clothes OR pubic_hair OR topless OR bottomless OR sexually_suggestive OR nude OR wet_panties OR no_panties OR spanking OR bondage OR vore OR bdsm OR open_clothes OR revealing_clothes OR breast_slip OR areoala_slip OR spread_ass OR orgasm OR vibrator OR sex_toy OR bulge OR lactation OR panty_pull OR panties_around_leg OR panties_removed OR partially_visible_vulva OR breast_sucking OR birth OR naked_clothes OR used_condom OR (suggestive AND (blush AND (spread_legs OR undressing OR erect_nipples OR ((miniskirt OR microskirt) AND underwear) OR (clothes_lift AND underwear)))))',
    1: 'NOT (sex OR hetero OR vaginal OR anal OR cum OR penis OR vagina OR pussy OR pussy_juice OR vaginal_juices OR spread_pussy OR erection OR clitoris OR anus OR oral OR fellatio OR fingering OR handjob OR masturbation OR object_insertion OR nipples OR areola OR areolae OR covered_nipples OR cameltoe OR wedgie OR torn_clothes OR pubic_hair OR topless OR bottomless OR sexually_suggestive OR nude OR wet_panties OR no_panties OR spanking OR bondage OR vore OR bdsm OR open_clothes OR revealing_clothes OR breast_slip OR areoala_slip OR spread_ass OR orgasm OR vibrator OR sex_toy OR bulge OR lactation OR panty_pull OR panties_around_leg OR panties_removed OR partially_visible_vulva OR breast_sucking OR birth OR naked_clothes OR used_condom OR (suggestive AND (blush AND (spread_legs OR undressing OR erect_nipples OR ((miniskirt OR microskirt) AND underwear) OR (clothes_lift AND underwear)))))'
    }

class Progress:
    
    def __init__(self, size, site, length=20):
        
        self.size = size
        self.site = site
        self.length = length
        self.left = (i for i in range(self.size))
        
    def __str__(self):
        
        try: left = next(self.left)
        except: left = self.size
        percent =  left / self.size
        ratio = f'({left}/{self.size})'
        padding = int(percent * self.length)
        bar = f'[{"|" * padding}{" " * (self.length-padding)}]'
        sys.stdout.write("\033[F")
        
        return f'{self.site}  —  {bar} {percent:>4.0%} {ratio}'

def save_image(name, image, exif=b''):
    '''Save image to name (with optional exif metadata)'''

    try:
        if re.search('jp.*g', image, re.IGNORECASE):

            try: Image.open(name).save(name, exif=exif)
            except:
                img = Image.open(BytesIO(requests.get(image, headers=HEADERS).content))
                img.thumbnail(RESIZE)
                img.save(name.with_suffix('.jpg'), exif=exif)
            
        elif re.search('png', image, re.IGNORECASE):

            img = Image.open(BytesIO(requests.get(image, headers=HEADERS).content))
            img.thumbnail(RESIZE)
            img = img.convert('RGBA')
            img = Image.alpha_composite(
                Image.new('RGBA', img.size, (0, 0, 0)), img
                )
            img.convert('RGB').save(name.with_suffix('.jpg'), exif=exif)

        elif re.search('gif|webm|mp4', image, re.IGNORECASE):
            
            data = requests.get(image, headers=HEADERS, stream=True)
            with open(name, 'wb') as file: 
                for chunk in data.iter_content(chunk_size=1024):
                    if chunk: file.write(chunk)
    
    except: return False
    return name.exists()
    
def get_name(path, type_, hasher=1, fetch=0):
    '''Return pathname (from optional hash of image)'''

    if hasher:
        try: data = requests.get(path).content
        except: data = path.read_bytes()
        HASHER.update(data)

        if fetch: return HASHER.hexdigest()
        try: stem = f'{HASHER.hexdigest()}{path.suffix.lower()}'
        except: stem = f'{HASHER.hexdigest()}.{re.findall(EXT, path)[0]}'
    
    else: stem = path

    return PATH / TYPE[type_] / stem.replace('png', 'jpg').replace('jpeg','jpg')

def get_hash(image, src=False):
    '''Return perceptual hash of image'''
        
    if src:
        
        # ext = f".{image.split('.')[-1]}"
        # temp = tempfile.TemporaryFile(suffix=ext)
        # temp.write(requests.get(image).content)
        image = Image.open(BytesIO(requests.get(image).content))
    
    elif re.search('jp.*g|png|gif', image.suffix, re.IGNORECASE): 
        
        image = Image.open(image)

    elif re.search('webm|mp4', image.suffix, re.IGNORECASE):
        
        video_capture = VideoCapture(str(image)).read()[-1]
        image = cvtColor(video_capture, COLOR_BGR2RGB)
        image = Image.fromarray(image)
    
    image.thumbnail([32, 32])
    image = image.convert('L')

    return f'{imagehash.dhash(image)}'

def get_tags(driver, path):

    tags = set()
    frames = []
    try: video = path.suffix in ('.gif', '.webm', '.mp4')
    except: video = False

    if video:

        tags.add('animated')
        if path.suffix in ('.webm', '.mp4'): tags.add('audio')
        temp_dir = tempfile.TemporaryDirectory()
        vidcap = VideoCapture(str(path))
        success, frame = vidcap.read()
 
        while success:
            
            temp = ROOT.parent / temp_dir.name / f'{next(tempfile._get_candidate_names())}.jpg'
            temp.write_bytes(imencode('.jpg', frame)[-1])
            frames.append(temp)
            success, frame = vidcap.read()

        else: 
            step = round(90 * log((len(frames) * .0007) + 1) + 1)
            frames = frames[::step]
    
    else: frames.append(path)
    
    for frame in frames:

        driver.get('http://kanotype.iptime.org:8003/deepdanbooru/')
        driver.find('//*[@id="exampleFormControlFile1"]', str(frame))
        driver.find('//body/div/div/div/form/button', click=True)

        for _ in range(16):
            html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
            try:
                tags.update([
                    tag.text for tag in 
                    html.find('tbody').findAll(href=True)
                    ])
                break
            except AttributeError: 
                if driver.current_url().endswith('deepdanbooru/'):
                    driver.find('//*[@id="exampleFormControlFile1"]',str(frame))
                    driver.find('//body/div/div/div/form/button', click=True)
                elif not _ % 4: driver.refresh()
    
    else:
        if video: temp_dir.cleanup()
        tags.discard('rating:safe')
        tags.discard('rating:questionable')
        tags.discard('rating:explicit')
        tags.discard('photorealistic')
        tags.discard('realistic')
        tags.discard('3d')
    
    return ' '.join(tags)

def generate_tags(general, metadata=0, custom=0, artists=[], rating=0, exif=1):
    
    tags = ['qwd']
    # re.sub(
    #     '(3d)|(photorealistic)|(realistic)|(rating:\w+)|(score:\w+)', '', ' '.join(tags)
    #     ).split()

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
        
        temp = f' {" ".join(tags) + " " + general} '
        rating, = [
            key for key in RATING if evaluate(temp, RATING[key])
            ]
    if exif:
        
        tags = set(tags + general.split())
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
        
        tags = ' '.join(list(tags))
        tags = [
            tags, rating, piexif.dump({"0th":zeroth_ifd,"Exif":exif_ifd})
            ]

    else: 

        tags = ' '.join(list(set(tags + general.split())))
        if rating is not None: tags = (tags, rating)
        
    return tags

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

    else: return re.search(f'\s({pattern})\s', tags)

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
