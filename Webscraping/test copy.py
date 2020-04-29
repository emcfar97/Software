import re, requests, bs4
import mysql.connector as sql
from utils import DATAB, CURSOR, get_name, generate_tags

SELECT = 'SELECT href FROM imageData WHERE site="gelbooru" AND tags=" {tags} " AND NOT ISNULL(src)'
UPDATE = 'UPDATE imageData SET tags=%s WHERE href=%s'
CURSOR.execute(SELECT)

for href, in CURSOR.fetchall():

    url = f'https://gelbooru.com/{href}'
    page_source = requests.get(url).content
    html = bs4.BeautifulSoup(page_source, 'lxml')

    artists = [
        '_'.join(artist.text.split(' ')[1:-1]) for artist in 
        html.findAll(class_='tag-type-artist')
        ]
    tags = [
        '_'.join(tag.text.split(' ')[1:-1]) for tag in 
        html.findAll(class_='tag-type-general')
        ]
    metadata = [
        '_'.join(tag.text.split(' ')[1:-1]) for tag in 
        html.findAll(class_='tag-type-metadata')
        ]
    tags = generate_tags(
        metadata=metadata, general=tags, custom=True, rating=False, exif=False
        )
    
    while True:
        try:
            CURSOR.execute(UPDATE, (tags, href))
            DATAB.commit()
            break
        except: continue