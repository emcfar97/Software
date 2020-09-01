import imagehash, piexif, time, bs4, requests, re, tempfile, hashlib, sys, ast
from . import ROOT
from math import log
from PIL import Image
from io import BytesIO
from configparser import ConfigParser
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
    2: 'sex|hetero|vaginal|anal|cum|penis|vagina|pussy|pussy_juice|vaginal_juices|spread_pussy|erection|clitoris|anus|oral|fellatio|fingering|handjob|masturbation|object_insertion', 
    1: 'NOT (sex OR hetero OR vaginal OR anal OR cum OR penis OR vagina OR pussy OR pussy_juice OR vaginal_juices OR spread_pussy OR erection OR clitoris OR anus OR oral OR fellatio OR fingering OR handjob OR masturbation OR object_insertion) AND (nipples OR areola OR areolae OR covered_nipples OR cameltoe OR wedgie OR torn_clothes OR pubic_hair OR topless OR bottomless OR sexually_suggestive OR nude OR wet_panties OR no_panties OR spanking OR bondage OR vore OR bdsm OR open_clothes OR revealing_clothes OR breast_slip OR areoala_slip OR spread_ass OR orgasm OR vibrator OR sex_toy OR bulge OR lactation OR panty_pull OR panties_around_leg OR panties_removed OR partially_visible_vulva OR breast_sucking OR birth OR naked_clothes OR used_condom OR (suggestive AND (blush AND (spread_legs OR undressing OR erect_nipples OR ((miniskirt OR microskirt) AND underwear) OR (clothes_lift AND underwear)))))',
    0: 'NOT (sex OR hetero OR vaginal OR anal OR cum OR penis OR vagina OR pussy OR pussy_juice OR vaginal_juices OR spread_pussy OR erection OR clitoris OR anus OR oral OR fellatio OR fingering OR handjob OR masturbation OR object_insertion OR nipples OR areola OR areolae OR covered_nipples OR cameltoe OR wedgie OR torn_clothes OR pubic_hair OR topless OR bottomless OR sexually_suggestive OR nude OR wet_panties OR no_panties OR spanking OR bondage OR vore OR bdsm OR open_clothes OR revealing_clothes OR breast_slip OR areoala_slip OR spread_ass OR orgasm OR vibrator OR sex_toy OR bulge OR lactation OR panty_pull OR panties_around_leg OR panties_removed OR partially_visible_vulva OR breast_sucking OR birth OR naked_clothes OR used_condom OR (suggestive AND (blush AND (spread_legs OR undressing OR erect_nipples OR ((miniskirt OR microskirt) AND underwear) OR (clothes_lift AND underwear)))))'
    }
artists_dict = {
    '0': ['', None],
    '0Lightsource': ['lightsource', None],
    '774': ['774_(nanashi)', None],
    'ABBB': ['ABBB', None],
    'Afrobull': ['Afrobull', None],
    'AkaShiaアカシア': ['', None],
    'akchu': ['akchu', None],
    'AME_雨': ['', None],
    'aomori': ['aomori', 1],
    'AQUA': ['', None],
    'Arctic char': ['tabata_hisayuki', None],
    'Arcticchar': ['tabata_hisayuki', None],
    'BergYB@DL販售中': ['', None],
    'bigdeadalive': ['bigdead93', None],
    'bkko': ['', None],
    'BlackFire': ['', None],
    'Bon': ['', None],
    'BOW':['bow_(bhp)', 0],
    'brekkist': ['', None],
    'C.ぶち': ['', None],
    'CHANxCO': ['', None],
    'Cian yo': ['', None],
    'Cianyo': ['', None],
    'cinko': ['', None],
    'Crescentia': ['Crescentia', None],
    'Nayuru':['Crescentia', None],
    'Crow': ['', None],
    'ctrlz77': ['', None],
    'CyanCapsule': ['', None],
    'DarkMangaka': ['', None],
    'DrossDrawings': ['', None],
    'DYTM': ['', None],
    'Elf': ['', None],
    'enigmagyaru':['gyarusatan', 1],
    'Gyarusatan': ['gyarusatan', 1],
    'Fishine_魚生': ['', None],
    'FUYA': ['', None],
    'paul_kwon': ['zeronis', None],
    'gray_eggs_n_ham':['gray_eggs_n_ham', 1],
    'graydoodles_':['gray_eggs_n_ham', 1],
    'hews': ['', None],
    'Hisasi': ['', None],
    'ICHIGAIN(一概)': ['', None],
    'iskra': ['iskra', 1],
    'ittla': ['ittla', 1],
    'JADF@jadf_': ['', None],
    'jcm2': ['', None],
    'JJuneジュン': ['jjune', 0],
    'joy ride': ['', None],
    'joyride': ['', None],
    'JP06@4日目西A': ['', None],
    'kajin': ['kajin_(kajinman)', 1],
    'kakao': ['', None],
    'kinucakes':['mariel_cartwright', None],
    'kon_kit':['konkitto', 0],
    'konomi★きのこのみ': ['', None],
    'Kultur': ['', None],
    'Kuuki': ['', None],
    'liveforthefunk': ['', None],
    'lmsketch': ['lm_(legoman)', 1],
    'Lucknight': ['', None],
    'Luxu': ['', None],
    'MadKaiser': ['', None],
    'Maji': ['', None],
    'Matinee': ['', None],
    'MC蕎麥': ['', None],
    'mdfあん': ['', None],
    'MIBRY☆': ['', None],
    'MoeBell': ['', None],
    'moong': ['', None],
    'Mukka': ['mukka', None],
    'N': ['', None],
    'Nanoless': ['', None],
    'nekofondue':['soduki', None],
    'niko': ['', None],
    'niwacho': ['', None],
    'Numbskull': ['', None],
    'oda古事記': ['', None],
    'Olkee': ['', None],
    'Ormille': ['', None],
    'otmm':['redrop', 0],
    'Owler': ['owler', 1],
    'P.man@ラクガキ屋': ['', None],
    'Pd': ['', None],
    'Peri': ['', None],
    'personalami':['personal_ami', 1],
    'Polyle': ['', None],
    'PrincessHinghoi': ['', None],
    'ratatatat74': ['', None],
    'RBG': ['', None],
    'ReDrop_おつまみ': ['redrop', 0],
    'ReiR': ['', None],
    'ryoagawa': ['agawa_ryou', 0],
    'rtil': ['rtil', 1],
    'RYU': ['', None],
    'sage・ジョー＠月西り28b': ['', None],
    'Saggitary': ['', None],
    'saitom': ['saitou_masatsugu', None],
    'samiri': ['', None],
    'sangobob': ['', None],
    'Seinen': ['seinen', None],
    'Shaliva': ['', None],
    'shift': ['', None],
    'somesomesome': ['', None],
    'SR': ['', None],
    'Stormcow': ['stormcow', None],
    'Sue': ['suertee34', None],
    'suezu': ['', None],
    'tarouyamada0101': ['', None],
    'Tetisuka': ['tetisuka', None],
    'tetsu': ['tetsu_(kimuchi)', 0],
    'TheTenk': ['', None],
    'Toddswee': ['', None],
    'tofuubear': ['tofuubear', None],
    'tukudani01': ['tsukudani', None],
    'uejini': ['gashi-gashi', None],
    'unou': ['', None],
    'V': ['', None],
    'vee': ['', None],
    'watatanza': ['watatanza', None],
    'Xin&obiwan': ['obiwan', 0],
    'Xin&obiコミ1A11ab': ['obiwan', 0],
    'Xin&obi月曜日れ34a': ['obiwan', 0],
    'Xin&obi月曜日れ34ab': ['obiwan', 0],
    'xtilxtil': ['rtil', None],
    'Y.P': ['', None],
    'yamaori': ['', None],
    'yas': ['', None],
    'YD': ['yang-do', 0],
    'YD@4日目西A': ['yang-do', 0],
    'yumoteliuce': ['', None],
    'Zako': ['zako_(arvinry)', None],
    'zerostripe': ['', None],
    'Zheng': ['zheng', 0],
    '♣3': ['nanaya_(daaijianglin)', 0],
    '♣3@金曜日西り02a': ['nanaya_(daaijianglin)', 0],
    '【丁髷帝国】まげきち': ['magekichi', None],
    'ぁぁぁぁ': ['aaaa', 0],
    'あきのそら': ['', None],
    'あくまで山羊さん': ['', None],
    'あすぜむ@４日目南ヒ42b': ['', None],
    'あぶぶ@凍結解除されたよ': ['abubu', 0],
    'あぶぶ＠復旧率069_162': ['abubu', 0],
    'ありのとわたり': ['', None],
    'あんこまん': ['', None],
    'あんこまん西よ': ['', None],
    'うらやま': ['', None],
    'うるりひ': ['', None],
    'おぶい＠夏コミ4日目あ40a': ['', None],
    'おるとろ_Vadass': ['', None],
    'お気楽ニック': ['', None],
    'かえぬこ＠４日目西ら01b': ['', None],
    'かねた': ['', None],
    'きょくちょ@単行本発売中': ['', None],
    'きょくちょ@月_西A_36b': ['', None],
    'くまこ': ['', None],
    'くみこ': ['', None],
    'くろわ': ['', None],
    'ぐすたふ': ['', None],
    'このでみのる': ['', None],
    'ごさいじ': ['', None],
    'ごるごんぞーら': ['', None],
    'ざくろ：4日目西れ': ['', None],
    'しぇふ@お仕事募集中': ['', None],
    'しおこんぶ': ['', None],
    'しゅにち_4日目西ゆ': ['', None],
    'じるす': ['', None],
    'すかいれ@月曜目西め06a': ['', None],
    'すかいれーだー@お仕事募集中': ['', None],
    'すーぱーぞんび': ['', None],
    'ぞんだ': ['zonda', None],
    'たかみち': ['', None],
    'ち.':[ '', None],
    'ちよ@Poiが如く': ['', None],
    'てだいん': ['tedain', None],
    'てつお': ['tetsuo_(tetuo1129)', None],
    'とりまへら': ['', None],
    'ななひめ': ['nanahime', None],
    'なまにくATK（あったかい）': ['namaniku_atk', None],
    'にの子': ['ninoko', None],
    'にゅう＠にゅう工房': ['', None],
    'のりパチ': ['', None],
    'はいぶりっどに生きたい': ['', None],
    'はすの上梅津': ['', None],
    'はんざきじろう': ['', None],
    'ばん!':[ 'ban', None],
    'ひなづか凉': ['', None],
    'ぴょんぴょん丸': ['', None],
    'ぴょん吉': ['', None],
    'ぴょん吉@日曜日 西り41b': ['', None],
    'ぴょん吉@日曜日西り41b': ['', None],
    'ぴよぴよ': ['', None],
    'ぷぅ崎ぷぅ奈': ['', None],
    'へら': ['hera_(hara0742)', None],
    'へろへろTom': ['', None],
    'ぺぺ': ['', None],
    'ぽち。': ['', None],
    'ぽてきち': ['', None],
    'まんす': ['', None],
    'みこやん': ['', None],
    'みたま': ['', None],
    'みたらし侯成': ['', None],
    'みちきんぐ': ['', None],
    'みちきんぐ@月曜南ナ37a': ['', None],
    'みなかみ': ['', None],
    'みのりむね': ['', None],
    'むねしろ@4日目れ–10b': ['', None],
    'めいさむ': ['', None],
    'やどかり': ['', None],
    'やんBARU': ['', None],
    'やんよ◆三日目西Ｌ27b': ['', None],
    'やんよ◆個展中止します': ['', None],
    'ゆゆ◆かわいそうな子': ['', None],
    'よしろん': ['', None],
    'りんでるふ': ['', None],
    'れぐでく': ['', None],
    'れとり': ['', None],
    'わくら': ['', None],
    'わなあた': ['', None],
    'わにわにぱにっく': ['', None],
    'アキラ': ['', None],
    'アトム': ['', None],
    'アマミヤ': ['', None],
    'アレグロ': ['', None],
    'ウンツエ@4日目西り': ['', None],
    'エルフ干': ['', None],
    'エロエ': ['', None],
    'オレンジマル@4日目西A38b': ['', None],
    'キクタ': ['', None],
    'キサラギツルギ@お仕事募集中': ['', None],
    'キチロク': ['', None],
    'キョルノフ': ['', None],
    'コザ＠Ｃ96４日目フ23a': ['', None],
    'サキ': ['', None],
    'サブ': ['', None],
    'サブロー': ['', None],
    'ディッコ(dikk0)': ['', None],
    'トール': ['', None],
    'ドウモウ_doumou': ['doumou', 0],
    'ナハ78': ['', None],
    'パオ': ['', None],
    'ボリス': ['', None],
    'マル_カキスト': ['', None],
    'ミツ': ['', None],
    'ミモネル': ['', None],
    'ムシ＠月曜西よ12b': ['', None],
    'ムラオサム': ['', None],
    'ロリコンダー': ['', None],
    'ワカメさん＠三日目I‐02ｂ': ['', None],
    '一ノ瀬ランド': ['', None],
    '一畳厠': ['', None],
    '不嬢女子月曜西よ14a': ['', None],
    '不死者O': ['', None],
    '中乃空@C96三日目西れ65a': ['', None],
    '五月猫': ['', None],
    '伊翁(イオン)': ['', None],
    '佃煮': ['', None],
    '低脂肪乳168円': ['', None],
    '何処テトラ@日曜日東テ04b': ['', None],
    '光主義者': ['', None],
    '兵蟹': ['', None],
    '内緒': ['', None],
    '分水嶺': ['', None],
    '双葉淀夢@c96日曜西よ22a': ['', None],
    '國王': ['', None],
    '夏桜@「花びら乙女」発売中!!': ['', None],
    '大仲いと': ['', None],
    '大爷别掐脸': ['', None],
    '安堂流': ['', None],
    '山本善々': ['', None],
    '山石': ['', None],
    '山羊ゆうお仕事募集中': ['', None],
    '川上六角': ['', None],
    '常磐緑4日目西り10b': ['', None],
    '常磐緑こみトレ４号館シ２４ｂ': ['', None],
    '平沢＠': ['', None],
    '広弥': ['', None],
    '弥猫うた@4日目西A': ['', None],
    '御坂12003@4日西よ23a': ['', None],
    '御坂12003@新刊委託中': ['', None],
    '愛上陸（waon＋越前）': ['', None],
    '方天戟_げっきー': ['', None],
    '暗黒えむ将軍': ['', None],
    '暗黒えむ将軍四日目西H19b': ['', None],
    '曳地朔夜': ['', None],
    '月宮つとめ＠': ['', None],
    '朝凪': ['', None],
    '朝昭': ['', None],
    '村井ニボシ': ['', None],
    '松河': ['', None],
    '核座頭': ['', None],
    '森宮正幸': ['', None],
    '榎ゆきみ@4日目ほ35a': ['', None],
    '樂桑': ['', None],
    '武田弘光': ['', None],
    '水平線◆三日目西めー42a': ['', None],
    '水龍敬': ['', None],
    '江野たと': ['', None],
    '泡面之侠': ['', None],
    '浅賀葵＠４日目西の': ['', None],
    '海老ブルー@C96金曜ア26a': ['', None],
    '海老ブルー@コミ1': ['', None],
    '湯豆ふ': ['', None],
    '猫姫優華@4日目南ケ13b': ['', None],
    '田嶋有紀': ['', None],
    '由雅なおは': ['', None],
    '真吉': ['', None],
    '秋橘': ['', None],
    '笹岡ぐんぐ': ['', None],
    '笹森トモエ': ['', None],
    '篠塚醸二': ['', None],
    '紅茶味覺': ['', None],
    '緑肉＠例大祭の26b': ['', None],
    '緑茶イズム': ['', None],
    '美矢火': ['', None],
    '羽凪いぬ': ['', None],
    '花田やのち': ['', None],
    '荻野アつき': ['', None],
    '荻野アつき_コミ1C36a': ['', None],
    '荻野アつき_個展中止します': ['', None],
    '荻野アつき◆三日目西Ｌ27b': ['', None],
    '蒟吉': ['', None],
    '蒼都かりん': ['', None],
    '藍夜@ついったーayasisu': ['', None],
    '蛇腹トルネード': ['', None],
    '詩乃譜': ['', None],
    '赤城あさひと': ['', None],
    '超絶美少女mine': ['', None],
    '越後屋タケル': ['', None],
    '辰波': ['', None],
    '遠藤良危＠月曜西よ24a': ['', None],
    '遠野すいか@４日目西め－01b': ['', None],
    '郁': ['', None],
    '釜ボコ': ['', None],
    '鈴雨やつみ': ['', None],
    '銀河味': ['', None],
    '銀鶏': ['', None],
    '闇夜乃鴉': ['', None],
    '隈吉': ['', None],
    '雪国裕': ['', None],
    '雪秀': ['', None],
    '青木幹治': ['', None],
    '風の行者': ['', None],
    '馬の助': ['', None],
    '馬克杯(Magukappu)': ['', None],
    '魔泥': ['', None],
    '鯨田だい太': ['', None],
    '鶴亀': ['', None],
    '鶴亀@1日目西れ': ['', None],
    '쏘망이': ['', None],
    '호시오키': ['', None],
    '８４６号@更新休止中': ['', None],
    '＿太子⭕️西り43a': ['', None]
    }

def progress(size, left, site, length=20):
    
    percent = left / size
    padding = int(percent * length)
    bar = f'[{"|" * padding}{" " * (length-padding)}]'
    print(f'{site}  —  {bar} {percent:>4.0%} ({left}/{size})')
    sys.stdout.write("\033[F")
    if left == size: print()
        
def login(driver, site, type_=0):
    
    credentials = ConfigParser(delimiters='=') 
    credentials.read('credentials.ini')
    from selenium.webdriver.common.keys import Keys

    if site == 'flickr':

        driver.get('https://identity.flickr.com/login')
        while driver.current_url == 'https://identity.flickr.com/login':
            driver.find('login-email', credentials.get(site, 'user'), type_=2)
            driver.find('login-email', Keys.RETURN, type_=2)
            driver.find('login-password', credentials.get(site,'pass'), type_=2)
            driver.find('login-password', Keys.RETURN, type_=2)
            time.sleep(2.5)

    elif site == 'metarthunter':

        driver.get('https://www.metarthunter.com/members/')
        driver.find('//*[@id="user_login"]', credentials.get(site, 'user'))
        driver.find('//*[@id="user_pass"]', credentials.get(site, 'pass'))
        while driver.current_url == 'https://www.metarthunter.com/members/': 
            time.sleep(2)
            
    elif site == 'femjoyhunter':

        driver.get('https://www.femjoyhunter.com/members/')
        driver.find('//*[@id="user_login"]', credentials.get(site, 'user'))
        driver.find('//*[@id="user_pass"]', credentials.get(site, 'pass'))
        while driver.current_url == 'https://www.femjoyhunter.com/members/': 
            time.sleep(2)
            
    elif site == 'elitebabes':

        driver.get('https://www.elitebabes.com/members/')
        driver.find('//*[@id="user_login"]', credentials.get(site, 'user'))
        driver.find('//*[@id="user_pass"]', credentials.get(site, 'pass'))
        while driver.current_url == 'https://www.elitebabes.com/members/': 
            time.sleep(2)

    elif site == 'instagram':
    
        driver.get('https://www.instagram.com/')
        driver.find('/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div[2]/div/label/input', credentials.get(site, 'email'))
        driver.find('/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div[3]/div/label/input', credentials.get(site, 'pass'))
        driver.find('/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div[3]/div/label/input', Keys.RETURN)
        time.sleep(2)

    elif site== 'gelbooru':

        driver.get('https://gelbooru.com/index.php?page=account&s=login&code=00')
        driver.find('/html/body/div[4]/div[4]/div/div/form/input[1]', credentials.get(site, 'user'))
        driver.find('/html/body/div[4]/div[4]/div/div/form/input[2]', credentials.get(site, 'pass'))
        driver.find('/html/body/div[4]/div[4]/div/div/form/input[2]', Keys.RETURN)
        time.sleep(1)

    elif site == 'sankaku':

        driver.get(f'https://{type_}.sankakucomplex.com/user/login')
        driver.find('//*[@id="user_name"]', credentials.get(site, 'user'))
        driver.find('//*[@id="user_password"]', credentials.get(site, 'pass'))
        driver.find('//*[@id="user_password"]', Keys.RETURN)
        time.sleep(2)
    
    elif site == 'furaffinity':

        driver.get('https://www.furaffinity.net/login/')
        driver.find('//*[@id="login"]', credentials.get(site, 'user'))
        driver.find('//body/div[2]/div[2]/form/div/section[1]/div/input[2]', credentials.get(site, 'pass'))
        while driver.current_url == 'https://www.furaffinity.net/login/': 
            time.sleep(2)
    
    elif site == 'twitter':

        email = credentials.get(site, 'email')
        passw = credentials.get(site, 'pass')

        driver.get('https://twitter.com/login')
        element = '//body/div[1]/div[2]/div/div/div[1]/form/fieldset/div[{}]/input'  
        while driver.current_url == 'https://twitter.com/login':
            try:  
                driver.find('session[username_or_email]', email, type_=3)
                time.sleep(.75)
                driver.find('session[password]', passw, type_=3)
                driver.find('session[password]', Keys.RETURN, type_=3)
                time.sleep(5)

            except:
                driver.find(element.format(1), email)
                time.sleep(.75)
                driver.find(element.format(2), passw)
                driver.find(element.format(2), Keys.RETURN)
                time.sleep(5)

    elif site == 'posespace':

        driver.get('https://www.posespace.com/')
        driver.find("//body/form[1]/div[3]/div[1]/nav/div/div[2]/ul[2]/li[6]/a", click=True)
        driver.find("popModal", click=True, type_=7)
        driver.find("loginUsername", credentials.get(site, 'email'), type_=2)
        driver.find("loginPassword", credentials.get(site, 'pass'), type_=2)
        driver.find("btnLoginSubmit", click=True, type_=2)

    elif site == 'pinterest':
        
        driver.get('https://www.pinterest.com/login/')
        driver.find('//*[@id="email"]', credentials.get(site, 'email'))
        driver.find('//*[@id="password"]', credentials.get(site, 'pass'))
        driver.find('//*[@id="password"]', Keys.RETURN)
        time.sleep(5)
        
    elif site == 'deviantArt':

        driver.get('https://www.deviantart.com/users/login')
        driver.find('//*[@id="username"]', credentials.get(site, 'email'))
        driver.find('//*[@id="password"]', credentials.get(site, 'pass'))
        driver.find('//*[@id="password"]', Keys.RETURN)
        time.sleep(5)

def save_image(name, image, exif=b''):
    '''Save image to name (with optional exif metadata)'''

    try:
        if re.search('jp.*g', image, re.IGNORECASE):

            if name.exists(): Image.open(name).save(name, exif=exif)
            else:
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
        
    if src and 'http' in image:
        
        ext = image.ext[:4]
        temp_dir = tempfile.TemporaryDirectory()
        temp = '\\'.join(
            temp_dir.name, f'{next(tempfile._get_candidate_names())}{ext}'
            )
        
        with open(temp, 'wb') as img:
            image = img.write(requests.get(image).content).name
    
    if re.search('jp.*g|png|gif', image.suffix, re.IGNORECASE): 
        
        image = Image.open(image)

    elif re.search('webm|mp4', image.suffix, re.IGNORECASE):
        
        video_capture = VideoCapture(str(image)).read()[-1]
        image = cvtColor(video_capture, COLOR_BGR2RGB)
        image = Image.fromarray(image)
    
    image.thumbnail([32, 32])
    image = image.convert('L')
    try: temp_dir.cleanup()
    except UnboundLocalError: pass

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
            f' {tags} ', rating, piexif.dump({"0th":zeroth_ifd,"Exif":exif_ifd})
            ]

    else: 

        tags = ' '.join(list(set(tags + general.split())))
        if rating is not None: tags = (f' {tags} ', rating)
        
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
