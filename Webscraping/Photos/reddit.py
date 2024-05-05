import argparse, re, bs4, time
from .. import CONNECT, WEBDRIVER, INSERT, SELECT, DELETE, get_credentials
from ..utils import IncrementalBar, save_image, get_hash, get_name, get_redgif, get_tags, generate_tags

SITE = 'reddit'
REMOVE = ['r/mbti', 'r/writing', 'r/nhentai']

def initialize(url, query, limit=5, retry=0):
    
    DRIVER.get(f'https://{SITE}.com{url}/upvoted')
    last_pass = ()

    while True:
        
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        hrefs = [
            (href, SITE, 1) for href in
            {
                href.get('permalink') for href in 
                html.findAll('shreddit-post')
                if href.get('subreddit-prefixed-name') not in REMOVE
                } - query
            ]
        MYSQL.execute(INSERT[0], hrefs, many=1)
        
        if not hrefs or hrefs == last_pass:
            if retry < limit: retry += 1
            else: break
        else: 
            retry = 0
        last_pass = hrefs
            
        DRIVER.driver.execute_script(
            "window.scrollTo(0, window.scrollY + 1080)"
            )
        time.sleep(2)
                
    MYSQL.commit()

def fetch_image(html, href):

    site = SITE
    
    if re.match('https://www.reddit.com/r/.+', href):
        
        site = 'reddit'

    elif re.match('https://www.reddit.com/media.+', href):
        
        site = 'reddit'
        href = f'https://i.redd.it/{stem.split("/")[-1]}'
        stem = stem.split("/")[-1]
        
        if 'mp4' in href: name = name.with_suffix('.mp4')

    elif re.match('https://www.reddit.com/gallery.+', href):
        
        site = 'reddit'
        gallery = html.find('gallery-carousel')
        href = list(set(
            image.get('src') for image in gallery.findAll('img', src=True)
            ))
    
    elif re.match('https://v.redd.it/.+', href):
        
        site = 'reddit'
        href = [html.find('shreddit-player').get('src')]
    
    elif re.match('https://preview.redd.it/.+', href):
        
        site = 'reddit'
        href = [f'https://i.redd.it/{path}']

    elif re.match('https://packaged-media.redd.it.+', href):
        
        site = 'reddit'
        href = [href]

    elif re.match('.+i.imgur.com/.+.gifv', href):
        
        site = 'imgur'        
        href = [href.replace('gifv', 'mp4')]

    elif re.match('.+imgur.com/a/.+', href):
        
        site = 'imgur'        
        stem = href.split("/")[-1]
        href = [f'https://i.imgur.com/{stem}.mp4']
        
    elif re.match('https://imgur.com/.+', href):
            
        site = 'imgur'            
        stem = href.split('/')[-1]
        href = [f'https://i.imgur.com/{stem}.mp4']

    elif re.match('.+redgifs.com.+', href):
        
        site = 'redgifs'
        href = [get_redgif(href.split('/')[-1])]
        
    else: href = [href]
    
    return href, site

def page_handler(hrefs):
    
    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs:
        
        progress.next()
        DRIVER.get(f'https://www.{SITE}.com{href}')
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        post = html.find('shreddit-post')
        
        if post.find(text=re.compile('.+ deleted by .+')):
            
            MYSQL.execute(DELETE[5], (href,), commit=1)
            continue
        
        artist = post.get('author').replace('-', '_').lower()
        if artist == '[deleted]': artist = ''
        
        records = []
        images, site = fetch_image(html, post.get('content-href'))
        
        for image in images:
            
            name = get_name(image)
            save_image(name, image)
            
            if 'packaged-media' in image: hash_ = get_hash(name, 0)
            elif 'redgifs' in image: hash_ = get_hash(name, 0)
            else: hash_ = get_hash(image, 1)

            tags, rating = generate_tags(
                general=get_tags(name, True), 
                custom=True, rating=True
                )
            records.append((
                name.name, ' '.join([artist]), tags, 
                rating, 1, hash_, image, site, href
                ))     

        # insert image
        if MYSQL.execute(INSERT[3], records, many=True):
            if name.exists():
                MYSQL.execute(DELETE[5], (href,))
                MYSQL.commit()
            else: MYSQL.rollback()
    
    print()

def main(initial=True, headless=True):
        
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)

    if initial:
        query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))
        initialize(*get_credentials(SITE, 'user'), query)
        # MYSQL.execute(INSERT[0], hrefs, many=1, commit=1)
    
    page_handler(MYSQL.execute(SELECT[1], (SITE,), fetch=1))
    DRIVER.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='reddit', 
        )
    parser.add_argument(
        '-i', '--init', type=int,
        help='Initial argument (default 1)',
        default=1
        )
    parser.add_argument(
        '-he', '--head', type=bool,
        help='Headless argument (default True)',
        default=True
        )

    args = parser.parse_args()
    
    main(args.init, args.head)