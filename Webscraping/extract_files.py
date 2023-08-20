import argparse, re, bs4, send2trash, subprocess, requests
from pathlib import Path
from urllib.parse import urlparse, unquote
from Webscraping import json_generator
from Webscraping.utils import save_image
    
def extract_errors(path, dest):
                
    if path.exists():
        
        images = list(set(path.read_text().split()))
        
        for image in images:

            name = dest / image.split('/')[-1].split('?')[0]
            
            if name.suffix == '': name = name.with_suffix('.webm')
            
            elif name.suffix == '.m3u8':
                
                name = dest / image.split('/')[3]
                name = name.with_suffix('.mp4')
                subprocess.run(['ffmpeg', '-y', '-i', image, str(name)])
                
            if save_image(name, image):
                
                images.remove(image)
                path.write_text('\n'.join(images))
        
    else: path.touch()

def validate(source, dest):
    
    if isinstance(source, str):
        source = Path(source)
        iterator = [source]
        errors_txt = source.parent / 'errors.log'
        
    elif isinstance(source, list):
        iterator = source
        errors_txt = source / 'errors.log'
        
    elif isinstance(source, Path):
        iterator = source.glob('*json')
        errors_txt = Path(r'Webscraping\errors.log')

    if dest is None: dest = source
    else: dest = Path(dest)
    
    return dest, iterator, errors_txt

def main(source, dest=None):
    
    dest, iterator, errors_txt = validate(source, dest)
    extract_errors(errors_txt, dest)
    errors = []
    
    for file in iterator:
        
        for url in json_generator(file):
            
            path = urlparse(url['url']).path[1:]
            
            # image fetching
            if re.match('https://www.reddit.com/r/.+', url['url']):
                
                response = requests.get(url['url'])
                html = bs4.BeautifulSoup(response.content, 'lxml')
                try: image = html.find('source', src=True).get('src')
                except AttributeError: errors.append(image); continue
            
            elif re.match('https://preview.redd.it/.+', url['url']):
                
                image = f'https://i.redd.it/{path}'
                
            elif re.match('https://www.reddit.com/media.+', url['url']):
                
                path = urlparse(url['title'].split(' - ')[-1]).path[1:]
                image = f'https://i.redd.it/{path}'
            
            elif re.match('.+i.imgur.com/.+.gifv', url['url']):
                
                image = url['url'].replace('gifv', 'mp4')
                
            elif re.match('.+imgur.com/a/.+', url['url']):
                    
                stem = url['url'].split('/')[-1]
                image = f'https://i.imgur.com/{stem}.mp4'
                
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
                
                name = name.with_suffix('.webm')
                
            elif re.match('.+m3u8.+', image):
            
                name = dest / image.split('/')[3]
                name = name.with_suffix('.webm')
                subprocess.run(['ffmpeg', '-y', '-i', image, str(name)])
             
            # file cleanup
            if name.exists() or (name.with_suffix('.webp')).exists() or (name.with_suffix('.webm')).exists(): 
                continue

            elif not save_image(name, image): 
                errors.append(image)
                
            else: errors.append(image)
                    
        errors_txt.write_text(errors_txt.read_text() + '\n' + '\n'.join(errors))
        send2trash.send2trash(str(file))

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
        help='Destination argument (default None)',
        default=None
        )

    args = parser.parse_args()
    
    main(args.source, args.destination)