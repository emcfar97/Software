import imagehash, sys, ast, piexif, time, bs4, requests, re
from PIL import Image
from io import BytesIO
from os.path import join
import mysql.connector as sql

RESIZE = [1320, 1000]
USER = 'Chairekakia'
EMAIL = 'Emc1130@hotmail.com'
PASS = 'SakurA1@'

PATH = r'C:\Users\Emc11\Dropbox\Videos\ん'
    
DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor(buffered=True)

SELECT = [
    'SELECT href FROM imageData WHERE site=%s',
    'SELECT href FROM favorites WHERE site=%s',
    'SELECT href FROM imageData WHERE site=%s AND ISNULL(path)',
    'SELECT href FROM favorites WHERE site=%s AND ISNULL(path)',
    'SELECT path, href, src, site FROM favorites WHERE NOT (checked OR ISNULL(path))',
    '''
        SELECT REPLACE(save_name, "E:", "C:"),'/artworks/'||image_id,'pixiv' FROM pixiv_master_image UNION
        SELECT REPLACE(save_name, "E:", "C:"), '/artworks/'||image_id, 'pixiv' FROM pixiv_manga_image
        ''',
    ]
INSERT = [
    'INSERT INTO imageData(href, site) VALUES(%s, %s)',
    'INSERT INTO favorites(href, site) VALUES(%s, %s)',
    'INSERT IGNORE INTO favorites(path, href, site) VALUES(%s, %s, %s)'
    ]
UPDATE = [
    'UPDATE imageData SET path=%s, src=%s, hash=%s, type=%s WHERE href=%s',
    # 'UPDATE imageData SET path=%s, tags=%s, rating=%s, src=%s, hash=%s, type=%s WHERE href=%s',
    'UPDATE favorites SET path=%s, hash=%s, src=%s WHERE href=%s',
    'REPLACE INTO imageData(path,hash,href,site) VALUES(%s,%s,%s,%s)',
    'UPDATE imageData SET path=%s, artist=%s, tags=%s, rating=%s, src=%s, hash=%s, type=%s WHERE href=%s',
    'UPDATE favorites SET checked=%s, saved=%s WHERE path=%s'
    ]
if __file__.startswith(('e:\\', 'e:/')):
    
    PATH = PATH.replace('C:', 'E:')
    SELECT[4] = 'SELECT REPLACE(path, "C:", "E:"), href, src, site FROM favorites WHERE NOT (checked OR ISNULL(path))'
    INSERT[2] = 'INSERT IGNORE INTO favorites(path, href, site) VALUES(REPLACE(%s, "E:", "C:"), %s, %s)'
    UPDATE = [
        'UPDATE imageData SET path=REPLACE(%s, "E:", "C:"), src=%s, hash=%s, type=%s WHERE href=%s',
        # 'UPDATE imageData SET path=REPLACE(%s, "E:", "C:"), tags=%s, rating=%s, src=%s, hash=%s, type=%s WHERE href=%s',
        'UPDATE favorites SET path=REPLACE(%s, "E:", "C:"), hash=%s, src=%s WHERE href=%s',
        'REPLACE INTO imageData(path,hash,href,site) VALUES(%s,%s,%s,%s)',
        'UPDATE imageData SET path=REPLACE(%s, "E:", "C:"), artist=%s, tags=%s, rating=%s, src=%s, hash=%s, type=%s WHERE href=%s',
        'UPDATE favorites SET checked=%s, saved=%s WHERE path=REPLACE(%s, "E:", "C:")'
        ]

metadata_dict = {
    '3d':'3d',
    'monochrome':'monochrome', 
    'sketch': 'sketch',
    'lineart': 'lineart',
    'uncensored': 'uncensored',
    'censored': 'censored'
    }
custom_dict = {
    'aphorisms': '((((nipples OR nipple_slip OR areola OR areolae OR areola_slip OR no_bra) OR (no_panties OR pussy OR no_underwear))) AND ((shawl OR capelet OR cape OR shrug_<clothing> OR open_jacket OR bare_shoulders OR breasts_outside OR breastless_clothes OR underbust OR underboob) OR (sarong OR loincloth OR skirt OR pelvic_curtain OR showgirl_skirt OR belt OR japanese_clothes OR dress OR corset OR side_slit)) OR (condom_belt OR leggings OR thighhighs OR thigh_boots))', 
    'clothes_lift': 'clothes_lift OR skirt_lift OR shirt_lift OR dress_lift OR sweater_lift OR bra_lift OR bikini_lift OR kimino_lift OR apron_lift',
    'intercrural': 'thigh_sex',
    'loops': 'loops OR thigh_strap OR necklace OR neck_ring OR anklet OR bracelet OR armlet',  
    'naked_clothes': 'naked_belt OR naked_apron OR naked_shirt OR naked_cape OR naked_overalls OR naked_ribbon OR naked_cloak OR naked_bandage', 
    'sexy': 'NOT (nude OR topless OR (bottomless OR no_panties))',
    'slender': '(solo OR (1girl AND NOT (1boy OR 2boys OR 3boys OR 4boys OR multiple_boys))) AND (slender OR NOT (((muscular OR muscle OR muscular_female OR toned OR abs) OR ((large_breasts OR huge_breasts OR gigantic_breasts) OR (plump OR fat) OR thick_thighs OR wide_hips OR huge_ass))))',
    'vagina': 'pussy',
    'underwear': 'underwear OR panties OR bra OR briefs'
    }
general_dict = {
    '69': '69',
    'age_difference': 'age_difference OR teenage_girl_and_younger_boy',
    'ass': 'ass', 
    'bottomless': 'bottomless AND NOT (topless OR nude)', 
    'breast_rest': 'breast_rest', 
    'character_sheet': 'character_sheet', 
    'condom': 'condom', 
    'concept_art':'concept_art',
    'cowgirl_position': 'cowgirl_position OR reverse_cowgirl_position', 
    'cum': 'cum OR precum OR semen',
    'dancing': 'dancing OR dancer', 
    'doggystyle': 'doggystyle', 
    'eye_contact': 'eye_contact',
    'flashing': 'flashing',
    'furry': 'furry', 
    'futanari': 'futanari', 
    'gesugao': 'crazy_smile OR crazy_eyes OR gesugao', 
    'girl_on_top': 'girl_on_top',
    'japanese_clothes': 'yamakasa OR tabi OR sarashi OR fundoshi OR hakama OR yukata OR kimono OR geta OR happi OR zori',
    'lactation': 'lactation',
    'male_focus': '(male_focus OR (solo AND 1boy) OR (1boy AND NOT (1girl OR 2girls OR 3girls OR 4girls OR multiple_girls))) AND NOT futanari',
    'masturbation': 'masturbation',
    'missionary': 'missionary', 
    'muscular': '(solo OR (1girl AND NOT (1boy OR 2boys OR 3boys OR 4boys OR multiple_boys))) AND (muscular OR muscle OR muscular_female OR toned OR abs)', 
    'nude': 'nude OR functionally_nude OR (bottomless AND topless)', 
    'open_clothes': 'open_clothes OR open_coat OR open_jacket OR open_shirt OR open_robe OR open_kimono OR open_fly OR open_shorts', 
    'orgasm': 'orgasm OR ejaculation', 
    'penis': 'penis', 
    'penis_kiss': 'penis_kiss', 
    'piercings': 'piercings OR earrings OR navel_piercings OR areola_piercing OR back_piercing OR navel_piercing OR nipple_piercing OR ear_piercing OR eyebrow_piercing OR eyelid_piercing OR lip_piercing OR nose_piercing OR tongue_piercing OR clitoris_piercing OR labia_piercing OR penis_piercing OR testicle_piercing OR nipple_chain', 
    'pregnant': 'pregnant', 
    'presenting': 'presenting OR top-down_bottom-up OR ((spread_legs OR spread_pussy) AND (trembling OR (heavy_breathing OR breath) OR (parted_lips AND NOT clenched_teeth))) OR spread_pussy', 
    'pubic_hair': 'pubic_hair',
    'pubic_tattoo': 'pubic_tattoo',
    'pussy': 'pussy OR vagina', 
    'pussy_juice': 'pussy_juice OR pussy_juices OR pussy_juice_trail OR pussy_juice_puddle OR pussy_juice_stain OR pussy_juice_drip_through_clothes', 
    'revealing_clothes': 'revealing_clothes OR torn_clothes OR micro_bikini OR crop_top OR pussy_peek OR midriff OR cleavage_cutout OR wardrobe_malfunction OR breast_slip OR nipple_slip OR areola_slip OR no_panties OR no_bra OR pelvic_curtain OR side_slit OR breasts_outside OR see-through OR partially_visible_vulva OR functionally_nude OR breastless_clothes OR bare_shoulders OR one_breast_out',
    'sex': 'sex OR vaginal OR anal OR facial OR oral OR fellatio OR cunnilingus OR handjob OR frottage OR tribadism', 
    'sex_toys': 'sex_toys OR vibrator OR dildo OR butt_plug OR artificial_vagina',
    'stealth_sex': 'stealth_sex', 
    'stretch':'stretch', 
    'solo': 'solo OR (1girl AND NOT (1boy OR 2boys OR 3boys OR 4boys OR multiple_boys))', 
    'spooning': 'spooning', 
    'standing_sex': '(standing_on_one_leg OR (standing AND (leg_up OR leg_lift))) AND sex',
    'suggestive': 'sexually_suggestive OR (naughty_smile OR fellatio_gesture OR teasing OR blush OR spread_legs OR pulled_by_self OR lifted_by_self OR (come_hither OR beckoning) OR (tongue_out AND (open_mouth OR licking_lips)) OR (bent_over AND (looking_back OR looking_at_viewer)) OR (trembling OR (saliva OR sweat) OR ((heavy_breathing OR breath) OR (parted_lips AND NOT clenched_teeth))) OR (skirt_lift OR bra_lift OR dress_lift OR shirt_lift OR wind_lift OR breast_lift OR kimono_pull) AND NOT (vaginal OR anal OR sex OR erection OR aftersex OR ejaculation OR pussy OR penis))', 
    'suspended_congress': 'suspended_congress OR reverse_suspended_congress',
    'tattoo': 'tattoo', 
    'topless': 'topless AND bare_shoulders AND NOT (bottomless OR nude)', 
    'tribal': 'tribal', 
    'upright_straddle': 'upright_straddle'
    }
rating_dict = {
    'explicit': 'sex OR hetero OR vaginal OR anal OR cum OR penis OR vagina OR pussy OR pussy_juice OR vaginal_juices OR spread_pussy OR erection OR clitoris OR anus OR oral OR fellatio OR fingering OR handjob OR masturbation OR object_insertion', 
    'questionable': 'NOT (sex OR hetero OR vaginal OR anal OR cum OR penis OR vagina OR pussy OR pussy_juice OR vaginal_juices OR spread_pussy OR erection OR clitoris OR anus OR oral OR fellatio OR fingering OR handjob OR masturbation OR object_insertion) AND (nipples OR areola OR areolae OR covered_nipples OR cameltoe OR wedgie OR torn_clothes OR pubic_hair OR topless OR bottomless OR sexually_suggestive OR nude OR wet_panties OR no_panties OR spanking OR bondage OR vore OR bdsm OR open_clothes OR revealing_clothes OR breast_slip OR areoala_slip OR spread_ass OR orgasm OR vibrator OR sex_toy OR bulge OR lactation OR panty_pull OR panties_around_leg OR panties_removed OR partially_visible_vulva OR breast_sucking OR birth OR naked_clothes OR used_condom OR (suggestive AND (blush AND (spread_legs OR undressing OR erect_nipples OR ((miniskirt OR microskirt) AND underwear) OR (clothes_lift AND underwear)))))',
    'safe': 'NOT (sex OR hetero OR vaginal OR anal OR cum OR penis OR vagina OR pussy OR pussy_juice OR vaginal_juices OR spread_pussy OR erection OR clitoris OR anus OR oral OR fellatio OR fingering OR handjob OR masturbation OR object_insertion OR nipples OR areola OR areolae OR covered_nipples OR cameltoe OR wedgie OR torn_clothes OR pubic_hair OR topless OR bottomless OR sexually_suggestive OR nude OR wet_panties OR no_panties OR spanking OR bondage OR vore OR bdsm OR open_clothes OR revealing_clothes OR breast_slip OR areoala_slip OR spread_ass OR orgasm OR vibrator OR sex_toy OR bulge OR lactation OR panty_pull OR panties_around_leg OR panties_removed OR partially_visible_vulva OR breast_sucking OR birth OR naked_clothes OR used_condom OR (suggestive AND (blush AND (spread_legs OR undressing OR erect_nipples OR ((miniskirt OR microskirt) AND underwear) OR (clothes_lift AND underwear)))))'
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

def get_driver(headless=False):

    from selenium import webdriver
    from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
    from selenium.webdriver.firefox.options import Options
    
    options = Options()
    options.headless = headless
    binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
    driver = webdriver.Firefox(firefox_binary=binary, options=options)
    driver.implicitly_wait(10)

    return driver

def login(driver, site, type_=0):
    
    from selenium.webdriver.common.keys import Keys

    if site == 'flickr':

        driver.get('https://identity.flickr.com/login')
        while driver.current_url == 'https://identity.flickr.com/login':
            driver.find_element_by_id('login-email').send_keys(EMAIL)
            driver.find_element_by_id('login-email').send_keys(Keys.RETURN)
            driver.find_element_by_id('login-password').send_keys(PASS)
            driver.find_element_by_id('login-password').send_keys(Keys.RETURN)
            time.sleep(2.5)
    
    elif site== 'gelbooru':

        driver.get('https://gelbooru.com/index.php?page=account&s=login&code=00')
        driver.find_element_by_xpath('//body/div[7]/div/div/form/input[1]').send_keys(USER)
        driver.find_element_by_xpath('//body/div[7]/div/div/form/input[2]').send_keys(PASS)
        driver.find_element_by_xpath("//body/div[7]/div/div/form/input[3]").click()

    elif site == 'sankaku':

        driver.get('https://chan.sankakucomplex.com/user/login')
        driver.find_element_by_xpath('//*[@id="user_name"]').send_keys(USER)
        driver.find_element_by_xpath('//*[@id="user_password"]').send_keys(PASS)
        driver.find_element_by_xpath('//*[@id="user_password"]').send_keys(Keys.RETURN)
        time.sleep(2)
    
    elif site == 'furaffinity':

        driver.get('https://www.furaffinity.net/login/')
        driver.find_element_by_xpath('//*[@id="login"]').send_keys(USER)
        driver.find_element_by_xpath('//body/div[2]/div[2]/form/div/section[1]/div/input[2]').send_keys(PASS)
        while driver.current_url == 'https://www.furaffinity.net/login/': 
            time.sleep(2)
    
    elif site == 'twitter':

        driver.get('https://twitter.com/login')
        element = '//body/div[1]/div[2]/div/div/div[1]/form/fieldset/div[{}]/input'  
        while driver.current_url == 'https://twitter.com/login':
            try:  
                driver.find_element_by_xpath(element.format(1)).send_keys(EMAIL)
                time.sleep(.75)
                driver.find_element_by_xpath(element.format(2)).send_keys(PASS)
                driver.find_element_by_xpath(element.format(2)).send_keys(Keys.RETURN)

            except:
                driver.find_element_by_name('session[username_or_email]').send_keys(EMAIL)
                time.sleep(.75)
                driver.find_element_by_name('session[password]').send_keys(PASS)
                driver.find_element_by_name('session[password]').send_keys(Keys.RETURN)
            
            time.sleep(2)

    elif site == 'posespace':

        driver.get('https://www.posespace.com/')
        driver.find_element_by_xpath("//body/form[1]/div[3]/div[1]/nav/div/div[2]/ul[2]/li[6]/a").click()
        driver.find_element_by_class_name("popModal").click()
        driver.find_element_by_id("loginUsername").send_keys(EMAIL)
        driver.find_element_by_id("loginPassword").send_keys(PASS)
        driver.find_element_by_id("btnLoginSubmit").click()

    elif site == 'pinterest':
        
        if type_: email = EMAIL
        else: email = 'emc1140@hotmail.com'
        passw = 'SchooL1@'
            
        driver.get('https://www.pinterest.com/login/')
        driver.find_element_by_xpath('//*[@id="email"]').send_keys(email)
        driver.find_element_by_xpath('//*[@id="password"]').send_keys(passw)
        driver.find_element_by_xpath('//*[@id="password"]').send_keys(Keys.RETURN)
        time.sleep(5)
        
def save_image(name, image, exif, save=0):
    
    if name.endswith(('.jpg', '.jpeg')):

        img = Image.open(BytesIO(requests.get(image).content))
        if save:
            img.thumbnail(RESIZE)
            img.save(name, exif=exif)
        
    elif name.endswith('.png'):

        name = name.replace('.png', '.jpg')
        img = Image.open(BytesIO(requests.get(image).content))
        if save:
            img.thumbnail(RESIZE)
            img = img.convert('RGBA')
            img = Image.alpha_composite(
                Image.new('RGBA', img.size, (255, 255, 255)), img
                )
            img.convert('RGB').save(name, exif=exif)
    
    elif name.endswith(('.gif','.webm', '.mp4')):
        
        data = requests.get(image).content
        if name.endswith('.gif'): img = Image.open(data)
        else: hash_ = None
        if save:
            with open(name, 'wb') as file: file.write(data)
        
    if name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        
        img.thumbnail([32, 32])
        img = img.convert('L')
        hash_ = f'{imagehash.dhash(img)}'
        
    return hash_

def progress(size, left, site, length=20):
    
    percent = left / size
    padding = int(percent * length)
    bar = f'[{"|" * padding}{" " * (length-padding)}]'
    print(f'{site}  —  {bar} {percent:03.0%} ({left}/{size})')
    sys.stdout.write("\033[F")
    if left == size: print()

def get_tags(driver, path):

    driver.get('http://kanotype.iptime.org:8003/deepdanbooru/')
    driver.find_element_by_xpath('//*[@id="exampleFormControlFile1"]').send_keys(path)
    driver.find_element_by_xpath('//body/div/div/div/form/button').click()

    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    tags = [
        tag.text for tag in 
        html.find('tbody').findAll(href=True)
        ]
    return tags

def generate_tags(
    type=None,artists=[],metadata=[],general=[],custom=[],rating=[],exif=True
    ):

    tags = []
    type = 'Erotica 2' if 'photo' in general else type

    if metadata:
        
        tags.append([
            key for key, val in metadata_dict.items() 
            if evaluate(metadata, val)
            ])
    if general:
        
        tags.append([
            key for key, val in general_dict.items() 
            if evaluate(general, val)
            ])
    if custom:
        
        tags.append([
            key for key, val in custom_dict.items() 
            if evaluate(general, val)
            ])
    if rating:
        
        rating, = [
            key for key, val in rating_dict.items() 
            if evaluate(sum(tags,[]) + general, val)
            ]
    if exif:

        zeroth_ifd = {
            piexif.ImageIFD.XPKeywords: [
                byte for char in '; '.join(sum(tags,[]))for byte in[ord(char),0]
                ],
            piexif.ImageIFD.XPAuthor: [
                byte for char in '; '.join(artists) for byte in [ord(char), 0]
                ]
            }
        exif_ifd = {piexif.ExifIFD.DateTimeOriginal: u'2000:1:1 00:00:00'}
        tags = [' '.join(set(sum(tags, []) + general)), rating] if tags else []
        try: tags += [piexif.dump({"0th":zeroth_ifd, "Exif":exif_ifd})]
        except: return
    
    return tags + [rating] if (rating and not exif) else tags

def evaluate(tags, search):
    
    query = tuple(search.replace('(', '( ').replace(')', ' )').split(' '))
    query = str(query).replace("'(',", '(').replace(", ')'", ')')
    query = query.replace('<','(').replace('>',')')
            
    return parse(tags, ast.literal_eval(query))

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
