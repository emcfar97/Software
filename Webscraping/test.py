import re

metadata_dict = {
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
custom_dict = {
    'aphorisms': '((((nipples|nipple_slip|areola|areolae|areola_slip|no_bra)|(no_panties|pussy|no_underwear))) AND ((shawl|capelet|cape|shrug_<clothing>|open_jacket|bare_shoulders|breasts_outside|breastless_clothes|underbust|underboob)|(sarong|loincloth|skirt|pelvic_curtain|showgirl_skirt|belt|japanese_clothes|dress|corset|side_slit))|(condom_belt|leggings|thighhighs|thigh_boots)|naked_clothes)', 
    'clothes_lift': 'clothes_lift|skirt_lift|shirt_lift|dress_lift|sweater_lift|bra_lift|bikini_lift|kimino_lift|apron_lift',
    'intercrural': 'thigh_sex',
    'loops': 'loops|thigh_strap|necklace|neck_ring|anklet|bracelet|armlet',  
    'naked_clothes': 'naked_belt|naked_apron|naked_shirt|naked_cape|naked_overalls|naked_ribbon|naked_cloak|naked_bandage', 
    'sexy': 'NOT (nude|topless|(bottomless|no_panties))',
    'slender': '(solo|(1girl AND NOT (1boy|2boys|3boys|4boys|multiple_boys))) AND (slender|NOT (((muscular|muscle|muscular_female|toned|abs)|((large_breasts|huge_breasts|gigantic_breasts)|(plump|fat)|thick_thighs|wide_hips|huge_ass))))',
    'vagina': 'pussy',
    'underwear': 'underwear|panties|bra|briefs'
    }
general_dict = {
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
    'male_focus': '(male_focus|(solo AND 1boy)|(1boy AND NOT (1girl|2girls|3girls|4girls|multiple_girls))) AND NOT futanari',
    'masturbation': 'masturbation',
    'missionary': 'missionary', 
    'muscular': '(solo|(1girl AND NOT (1boy|2boys|3boys|4boys|multiple_boys))) AND (muscular|muscle|muscular_female|toned|abs)', 
    'nude': 'nude|functionally_nude|(bottomless AND topless)', 
    'open_clothes': 'open_clothes|open_coat|open_jacket|open_shirt|open_robe|open_kimono|open_fly|open_shorts', 
    'orgasm': 'orgasm|ejaculation', 
    'penis': 'penis', 
    'penis_kiss': 'penis_kiss', 
    'piercings': 'piercings|earrings|navel_piercings|areola_piercing|back_piercing|navel_piercing|nipple_piercing|ear_piercing|eyebrow_piercing|eyelid_piercing|lip_piercing|nose_piercing|tongue_piercing|clitoris_piercing|labia_piercing|penis_piercing|testicle_piercing|nipple_chain', 
    'pregnant': 'pregnant', 
    'presenting': 'presenting|top-down_bottom-up|((spread_legs|spread_pussy) AND (trembling|(heavy_breathing|breath)|(parted_lips AND NOT clenched_teeth)))|spread_pussy', 
    'pubic_hair': 'pubic_hair',
    'pubic_tattoo': 'pubic_tattoo',
    'pussy': 'pussy|vagina', 
    'pussy_juice': 'pussy_juice|pussy_juices|pussy_juice_trail|pussy_juice_puddle|pussy_juice_stain|pussy_juice_drip_through_clothes', 
    'revealing_clothes': 'revealing_clothes|torn_clothes|micro_bikini|crop_top|pussy_peek|midriff|cleavage_cutout|wardrobe_malfunction|breast_slip|nipple_slip|areola_slip|no_panties|no_bra|pelvic_curtain|side_slit|breasts_outside|see-through|partially_visible_vulva|functionally_nude|breastless_clothes|bare_shoulders|one_breast_out',
    'sex': 'sex|vaginal|anal|facial|oral|fellatio|cunnilingus|handjob|frottage|tribadism', 
    'sex_toys': 'sex_toys|vibrator|dildo|butt_plug|artificial_vagina',
    'stealth_sex': 'stealth_sex', 
    'stretch':'stretch', 
    'solo': 'solo|(1girl AND NOT (1boy|2boys|3boys|4boys|multiple_boys))', 
    'spooning': 'spooning', 
    'standing_sex': '(standing_on_one_leg|(standing AND (leg_up|leg_lift))) AND sex',
    'suggestive': 'sexually_suggestive|(naughty_smile|fellatio_gesture|teasing|blush|spread_legs|pulled_by_self|lifted_by_self|(come_hither|beckoning)|(tongue_out AND (open_mouth|licking_lips))|(bent_over AND (looking_back|looking_at_viewer))|(trembling|(saliva|sweat)|((heavy_breathing|breath)|(parted_lips AND NOT clenched_teeth)))|(skirt_lift|bra_lift|dress_lift|shirt_lift|wind_lift|breast_lift|kimono_pull) AND NOT (vaginal|anal|sex|erection|aftersex|ejaculation|pussy|penis))', 
    'suspended_congress': 'suspended_congress|reverse_suspended_congress',
    'tattoo': 'tattoo', 
    'topless': 'topless AND bare_shoulders AND NOT (bottomless|nude)', 
    'tribal': 'tribal', 
    'upright_straddle': 'upright_straddle'
    }
rating_dict = {
    '2': 'sex|hetero|vaginal|anal|cum|penis|vagina|pussy|pussy_juice|vaginal_juices|spread_pussy|erection|clitoris|anus|oral|fellatio|fingering|handjob|masturbation|object_insertion', 
    '1': 'NOT (sex|hetero|vaginal|anal|cum|penis|vagina|pussy|pussy_juice|vaginal_juices|spread_pussy|erection|clitoris|anus|oral|fellatio|fingering|handjob|masturbation|object_insertion) AND (nipples|areola|areolae|covered_nipples|cameltoe|wedgie|torn_clothes|pubic_hair|topless|bottomless|sexually_suggestive|nude|wet_panties|no_panties|spanking|bondage|vore|bdsm|open_clothes|revealing_clothes|breast_slip|areoala_slip|spread_ass|orgasm|vibrator|sex_toy|bulge|lactation|panty_pull|panties_around_leg|panties_removed|partially_visible_vulva|breast_sucking|birth|naked_clothes|used_condom|(suggestive AND (blush AND (spread_legs|undressing|erect_nipples|((miniskirt|microskirt) AND underwear)|(clothes_lift AND underwear)))))',
    '0': 'NOT (sex|hetero|vaginal|anal|cum|penis|vagina|pussy|pussy_juice|vaginal_juices|spread_pussy|erection|clitoris|anus|oral|fellatio|fingering|handjob|masturbation|object_insertion|nipples|areola|areolae|covered_nipples|cameltoe|wedgie|torn_clothes|pubic_hair|topless|bottomless|sexually_suggestive|nude|wet_panties|no_panties|spanking|bondage|vore|bdsm|open_clothes|revealing_clothes|breast_slip|areoala_slip|spread_ass|orgasm|vibrator|sex_toy|bulge|lactation|panty_pull|panties_around_leg|panties_removed|partially_visible_vulva|breast_sucking|birth|naked_clothes|used_condom|(suggestive AND (blush AND (spread_legs|undressing|erect_nipples|((miniskirt|microskirt) AND underwear)|(clothes_lift AND underwear)))))'
    }

string = 'feet 1boy long_hair nude witch_hat breasts erection armpits eyes_closed sparkle happy flat_chest hair_over_one_eye open_mouth slender pink_hair toes androgynous nipples solo trap navel penis stomach male_focus arms_up blush_stickers curly_hair purple_skin hat striped_hat jumping'
tags = []

tags.append([
    key for key, val in metadata_dict.items() 
    if bool(re.search(string, val))
    ])

tags.append([
    key for key, val in general_dict.items() 
    if bool(re.search(string, val))
    ])

tags.append([
    key for key, val in custom_dict.items() 
    if bool(re.search(string, val))
    ])

rating, = [
    key for key, val in rating_dict.items() 
    if bool(re.search(string, val))
    ]