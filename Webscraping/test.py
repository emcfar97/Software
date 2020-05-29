import re, ast

METADATA = {
    '3d':'3d',
    'monochrome':'monochrome', 
    'sketch': 'sketch',
    'lineart': 'lineart',
    'screencap':'screencap',
    'animated':'animated',
    'audio':'audio|has_audio',
    'uncensored': 'uncensored',
    'censored': 'censored',
    'official_art':'official_art',
    'game_cg':'game_cg'
    }
CUSTOM = {
    'aphorisms': '((((nipples OR nipple_slip OR areola OR areolae OR areola_slip OR no_bra) OR (no_panties OR pussy OR no_underwear))) AND ((shawl OR capelet OR cape OR shrug_<clothing> OR open_jacket OR bare_shoulders OR breasts_outside OR breastless_clothes OR underbust OR underboob) OR (sarong OR loincloth OR skirt OR pelvic_curtain OR showgirl_skirt OR belt OR japanese_clothes OR dress OR corset OR side_slit OR tabard)) OR (condom_belt OR leggings OR thighhighs OR thigh_boots) OR naked_clothes) OR amazon_position', 
    'clothes_lift': 'clothes_lift|skirt_lift|shirt_lift|dress_lift|sweater_lift|bra_lift|bikini_lift|kimino_lift|apron_lift',
    'intercrural': 'thigh_sex',
    'loops': 'loops|thigh_strap|necklace|neck_ring|anklet|bracelet|armlet',  
    'naked_clothes': 'naked_belt|naked_apron|naked_shirt|naked_cape|naked_overalls|naked_ribbon|naked_cloak|naked_bandage', 
    'sexy': 'NOT (nude OR topless OR (bottomless OR no_panties))',
    'slender': '(solo OR (1girl AND NOT (1boy OR 2boys OR 3boys OR 4boys OR multiple_boys))) AND (slender OR NOT (((muscular OR muscle OR muscular_female OR toned OR abs) OR ((large_breasts OR huge_breasts OR gigantic_breasts) OR (plump OR fat) OR thick_thighs OR wide_hips OR huge_ass))))',
    'vagina': 'pussy',
    'underwear': 'underwear|panties|bra|briefs'
    }
GENERAL = {
    '69': '69',
    'age_difference': 'age_difference|teenage_girl_and_younger_boy',
    'ass': 'ass', 
    'bottomless': 'bottomless AND NOT (topless|nude)', 
    'breast_rest': 'breast_rest', 
    'character_sheet': 'character_sheet', 
    'condom': 'condom', 
    'concept_art':'concept_art',
    'cowgirl_position': 'cowgirl_position|reverse_cowgirl_position', 
    'cum': 'cum|precum|semen',
    'dancing': 'dancing|dancer', 
    'doggystyle': 'doggystyle', 
    'eye_contact': 'eye_contact',
    'flashing': 'flashing',
    'furry': 'furry', 
    'futanari': 'futanari', 
    'gesugao': 'crazy_smile|crazy_eyes|gesugao', 
    'girl_on_top': 'girl_on_top',
    'japanese_clothes': 'yamakasa|tabi|sarashi|fundoshi|hakama|yukata|kimono|geta|happi|zori',
    'lactation': 'lactation',
    'male_focus': '(male_focus OR (solo AND 1boy) OR (1boy AND NOT (1girl OR 2girls OR 3girls OR 4girls OR multiple_girls))) AND NOT futanari',
    'masturbation': 'masturbation',
    'missionary': 'missionary', 
    'muscular': '(solo OR (1girl AND NOT (1boy OR 2boys OR 3boys OR 4boys OR multiple_boys))) AND (muscular OR muscle OR muscular_female OR toned OR abs)', 
    'nude': 'nude OR functionally_nude OR (bottomless AND topless)', 
    'open_clothes': 'open_clothes|open_coat|open_jacket|open_shirt|open_robe|open_kimono|open_fly|open_shorts', 
    'orgasm': 'orgasm|ejaculation', 
    'penis': 'penis', 
    'penis_kiss': 'penis_kiss', 
    'piercings': 'piercings|earrings|navel_piercings|areola_piercing|back_piercing|navel_piercing|nipple_piercing|ear_piercing|eyebrow_piercing|eyelid_piercing|lip_piercing|nose_piercing|tongue_piercing|clitoris_piercing|labia_piercing|penis_piercing|testicle_piercing|nipple_chain', 
    'pregnant': 'pregnant', 
    'presenting': 'presenting OR top-down_bottom-up OR ((spread_legs OR spread_pussy) AND (trembling OR (heavy_breathing OR breath) OR (parted_lips AND NOT clenched_teeth))) OR spread_pussy', 
    'pubic_hair': 'pubic_hair',
    'pubic_tattoo': 'pubic_tattoo',
    'pussy': 'pussy|vagina', 
    'pussy_juice': 'pussy_juice|pussy_juices|pussy_juice_trail|pussy_juice_puddle|pussy_juice_stain|pussy_juice_drip_through_clothes', 
    'revealing_clothes': 'revealing_clothes|torn_clothes|micro_bikini|crop_top|pussy_peek|midriff|cleavage_cutout|wardrobe_malfunction|breast_slip|nipple_slip|areola_slip|no_panties|no_bra|pelvic_curtain|side_slit|breasts_outside|see-through|partially_visible_vulva|functionally_nude|breastless_clothes|bare_shoulders|one_breast_out',
    'sex': 'sex|vaginal|anal|facial|oral|fellatio|cunnilingus|handjob|frottage|tribadism', 
    'sex_toys': 'sex_toys|vibrator|dildo|butt_plug|artificial_vagina',
    'stealth_sex': 'stealth_sex', 
    'stretch':'stretch', 
    'solo': 'solo OR (1girl AND NOT (1boy OR 2boys OR 3boys OR 4boys OR multiple_boys))', 
    'spooning': 'spooning', 
    'standing_sex': '(standing_on_one_leg OR (standing AND (leg_up OR leg_lift))) AND sex',
    'suggestive': 'sexually_suggestive OR (naughty_smile OR fellatio_gesture OR teasing OR blush OR spread_legs OR pulled_by_self OR lifted_by_self OR (come_hither OR beckoning) OR (tongue_out AND (open_mouth OR licking_lips)) OR (bent_over AND (looking_back OR looking_at_viewer)) OR (trembling OR (saliva OR sweat) OR ((heavy_breathing OR breath) OR (parted_lips AND NOT clenched_teeth))) OR (skirt_lift OR bra_lift OR dress_lift OR shirt_lift OR wind_lift OR breast_lift OR kimono_pull) AND NOT (vaginal OR anal OR sex OR erection OR aftersex OR ejaculation OR pussy OR penis))', 
    'suspended_congress': 'suspended_congress|reverse_suspended_congress',
    'tattoo': 'tattoo', 
    'topless': 'topless AND bare_shoulders AND NOT (bottomless OR nude)', 
    'tribal': 'tribal', 
    'upright_straddle': 'upright_straddle'
    }
RATING = {
    2: 'sex|hetero|vaginal|anal|cum|penis|vagina|pussy|pussy_juice|vaginal_juices|spread_pussy|erection|clitoris|anus|oral|fellatio|fingering|handjob|masturbation|object_insertion', 
    1: 'NOT (sex OR hetero OR vaginal OR anal OR cum OR penis OR vagina OR pussy OR pussy_juice OR vaginal_juices OR spread_pussy OR erection OR clitoris OR anus OR oral OR fellatio OR fingering OR handjob OR masturbation OR object_insertion) AND (nipples OR areola OR areolae OR covered_nipples OR cameltoe OR wedgie OR torn_clothes OR pubic_hair OR topless OR bottomless OR sexually_suggestive OR nude OR wet_panties OR no_panties OR spanking OR bondage OR vore OR bdsm OR open_clothes OR revealing_clothes OR breast_slip OR areoala_slip OR spread_ass OR orgasm OR vibrator OR sex_toy OR bulge OR lactation OR panty_pull OR panties_around_leg OR panties_removed OR partially_visible_vulva OR breast_sucking OR birth OR naked_clothes OR used_condom OR (suggestive AND (blush AND (spread_legs OR undressing OR erect_nipples OR ((miniskirt OR microskirt) AND underwear) OR (clothes_lift AND underwear)))))',
    0: 'NOT (sex OR hetero OR vaginal OR anal OR cum OR penis OR vagina OR pussy OR pussy_juice OR vaginal_juices OR spread_pussy OR erection OR clitoris OR anus OR oral OR fellatio OR fingering OR handjob OR masturbation OR object_insertion OR nipples OR areola OR areolae OR covered_nipples OR cameltoe OR wedgie OR torn_clothes OR pubic_hair OR topless OR bottomless OR sexually_suggestive OR nude OR wet_panties OR no_panties OR spanking OR bondage OR vore OR bdsm OR open_clothes OR revealing_clothes OR breast_slip OR areoala_slip OR spread_ass OR orgasm OR vibrator OR sex_toy OR bulge OR lactation OR panty_pull OR panties_around_leg OR panties_removed OR partially_visible_vulva OR breast_sucking OR birth OR naked_clothes OR used_condom OR (suggestive AND (blush AND (spread_legs OR undressing OR erect_nipples OR ((miniskirt OR microskirt) AND underwear) OR (clothes_lift AND underwear)))))'
    }

def evaluate(tags, pattern):
    
    if re.search('AND|OR|NOT', pattern):
        query = tuple(pattern.replace('(', '( ').replace(')', ' )').split(' '))
        query = str(query).replace("'(',", '(').replace(", ')'", ')')
        query = query.replace('<','(').replace('>',')')
                
        return parse(tags.split(), ast.literal_eval(query))
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


string = 'feet 1boy animated long_hair nude witch_hat breasts erection armpits eyes_closed sparkle happy flat_chest hair_over_one_eye open_mouth slender pink_hair toes androgynous audio nipples solo skirt_lift trap navel penis stomach male_focus arms_up blush_stickers curly_hair naked_belt purple_skin hat striped_hat jumping'
string = 'breasts towel barefoot nipples lips solo 1girl'
tags = []

tags.extend(
    key for key in GENERAL if evaluate(string, GENERAL[key])
    )

tags.extend(
    key for key in CUSTOM if evaluate(string, CUSTOM[key])
    )

temp = ' '.join(tags) + ' ' + string
rating, = [
    key for key in RATING if evaluate(temp, RATING[key])
    ]
pass