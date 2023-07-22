import argparse, re, bs4, send2trash, subprocess, requests
from pathlib import Path
from urllib.parse import urlparse
from Webscraping import json_generator
from Webscraping.utils import USER, save_image
    
def extract_errors(path, dest):
                
    if path.exists():
        
        images = path.read_text().split()
        
        for image in images:
        
            name = dest / image.split('/')[-1].split('?')[0]
            
            if name.suffix == '': name = name.with_suffix('.webm')
            
            elif name.suffix == '.m3u8':
                
                name = dest / image.split('/')[3]
                name = name.with_suffix('.mp4')
                subprocess.run(['ffmpeg', '-y', '-i', image, str(name)])
                
            if save_image(name, image): images.remove(image)
            
        path.write_text('\n'.join(images))
        
    else: path.touch()

def validate(source, dest):
    
    if isinstance(source, str):
        source = Path(source)
        if source.is_file(): iterator = [source]
        else: iterator = source.glob('*json')
        errors_txt = source.parent / 'errors.log'
        
    elif isinstance(source, list):
        iterator = source
        errors_txt = source / 'errors.log'
        
    elif isinstance(source, Path):
        iterator = source.glob('*json')
        errors_txt = Path(r'Webscraping\errors.log')

    if dest is None: dest = source
    else: dest = USER / dest
    
    return dest, iterator, errors_txt

def main(source, dest=None, headless=True):
    
    dest, iterator, errors_txt = validate(source, dest)
    # extract_errors(errors_txt, dest)
    errors = []
        
    # driver = WEBDRIVER(headless=headless)

    for file in iterator:

        for url in json_generator(file):
            
            path = urlparse(url['url']).path[1:]
            
            # image cleanup
            if re.match('https://www.reddit.com/r/.+', url['url']):
                
                response = requests.get(url['url'])
                html = bs4.BeautifulSoup(response.content, 'lxml')
                try: image = html.find('source', src=True).get('src')
                except AttributeError: errors.append(image); continue
            
            elif re.match('https://preview.redd.it/.+', url['url']):
                
                image = f'https://i.redd.it/{path}'
            
            elif re.match('.+i.imgur.com/.+.gifv', url['url']):
                
                image = url['url'].replace('gifv', 'mp4')
                
            elif re.match('.+imgur.com/a/.+', image):
                    
                # driver.get(image, wait=5)
                # html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
                
                try:
                        
                    continue
                        
                except: errors.append(image); continue
                
            elif re.match('https://imgur.com/.+', image):
                    
                for image in html.findAll('source', src=True):
                    
                    src = image.get('src')
                    name = dest / src.split('/')[-1]
                    if name.exists(): continue
                    save_image(name, src)
                    
                continue
            
            else:
                
                try: image = (
                        f'https://{url["title"]}'
                        if url['url'] == 'about:blank' else 
                        url['url']
                        )
                except KeyError: continue
            
            # name cleanup
            name = dest / path.split('/')[-1]    
            
            if not name.suffix and re.search('redgifs|gfycat', image):
                
                name = dest / image.split('/')[-1].split('?')[0]
                name = name.with_suffix('.webm')
            
            elif name.suffix == '.gifv':
                
                name = name.with_suffix('.mp4')
                
            elif re.match('.+m3u8.+', image):
            
                name = dest / image.split('/')[3]
                name = name.with_suffix('.mp4')
                subprocess.run(['ffmpeg', '-y', '-i', image, str(name)])
                
            # file cleanup
            if name.exists(): continue

            elif not save_image(name, image): errors.append(image)
                    
        errors_txt.write_text(errors_txt.read_text() + '\n' + '\n'.join(errors))
        send2trash.send2trash(str(file))

    # driver.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='extract files', 
        )
    parser.add_argument(
        '-s', '--source', type=str,
        help='Source argument',
        )
    parser.add_argument(
        '-d', '--destination', type=str,
        help='Destination argument (default "")',
        default=''
        )
    parser.add_argument(
        '-he', '--head', type=bool,
        help='Headless argument (default True)',
        default=True
        )

    args = parser.parse_args()
    
    main(args.extract, args.add, args.path)