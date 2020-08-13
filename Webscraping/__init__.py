import os
import mysql.connector as sql
    
ROOT = os.getcwd()[:2].upper()
PATH = rf'{ROOT}\Users\Emc11\Dropbox\Videos\ん'
SELECT = [
    'SELECT href FROM imageData WHERE site=%s',
    'SELECT href FROM favorites WHERE site=%s',
    'SELECT href FROM imageData WHERE site=%s AND ISNULL(path)',
    'SELECT href FROM favorites WHERE site=%s AND ISNULL(path)',
    f'SELECT REPLACE(path, "C:", "{ROOT}"), href, src, site FROM favorites WHERE NOT (checked OR ISNULL(path))',
    f'''
        SELECT REPLACE(save_name, "{ROOT}", "C:"),'/artworks/'||image_id,'pixiv' FROM pixiv_master_image UNION
        SELECT REPLACE(save_name, "{ROOT}", "C:"), '/artworks/'||image_id, 'pixiv' FROM pixiv_manga_image
        ''',
    ]
INSERT = [
    'INSERT INTO imageData(href, type, site) VALUES(%s, %s, %s)',
    'INSERT INTO favorites(href, site) VALUES(%s, %s)',
    f'INSERT IGNORE INTO favorites(path, href, site) VALUES(REPLACE(%s, "{ROOT}", "C:"), %s, %s)',
    'INSERT INTO imageData(artist, type, src, site) VALUES(%s, %s, %s, %s)',
    ]
UPDATE = [
    f'UPDATE imageData SET path=REPLACE(%s, "{ROOT}", "C:"), src=%s, hash=%s, type=%s WHERE href=%s',
    f'UPDATE favorites SET path=REPLACE(%s, "{ROOT}", "C:"), hash=%s, src=%s WHERE href=%s',
    f'REPLACE INTO imageData(path,hash,href,site) VALUES(REPLACE(%s, "{ROOT}", "C:"),%s,%s,%s)',
    f'UPDATE imageData SET path=REPLACE(%s, "{ROOT}", "C:"), artist=%s, tags=%s, rating=%s, src=%s, hash=%s WHERE href=%s',
    f'UPDATE favorites SET checked=%s, saved=%s WHERE path=REPLACE(%s, "{ROOT}", "C:")',
    f'INSERT INTO favorites(path, hash, src, href, site) VALUES(REPLACE(%s, "{ROOT}", "C:"), %s, %s, %s, %s)'
    ]

class CONNECT:

    def __init__(self):

        self.DATAB, self.CURSOR = self.connect()

    def connect(self):

        DATAB = sql.connect(
            user='root', password='SchooL1@', database='userData', 
            host='127.0.0.1' if ROOT == 'C:' else '192.168.1.43'
            )
        CURSOR = DATAB.cursor(buffered=True)

        return DATAB, CURSOR

    def execute(self, statement, arguments=None, many=0, commit=0, fetch=0):
        
        for _ in range(20):

            try:
                if many: self.CURSOR.executemany(statement, arguments)
                else: self.CURSOR.execute(statement, arguments)

                if commit: self.DATAB.commit()
                elif fetch: return self.CURSOR.fetchall()

            except sql.errors.OperationalError: continue
            
            except sql.errors.DatabaseError: self.DATAB, self.CURSOR = self.connect()                

    def close(self): self.DATAB.close()

CONNECTION = CONNECT()