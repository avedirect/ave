"""Загрузка сайта (папка public/) на Beget по FTP.

python deploy_ftp.py
Хост, логин и папку спросит скрипт (Enter — значение по умолчанию), пароль вводится скрыто.
"""
import ftplib
import getpass
from pathlib import Path

LOCAL = Path(__file__).parent / 'public'
host = input('FTP-хост [ave98ivu.beget.tech]: ').strip() or 'ave98ivu.beget.tech'
user = input('Логин: ').strip()
pwd = getpass.getpass('Пароль (не отображается): ')
remote = input('Папка сайта на сервере [public_html]: ').strip() or 'public_html'

ftp = ftplib.FTP(host, timeout=60)
ftp.encoding = 'utf-8'
ftp.login(user, pwd)
ftp.cwd(remote)
print('Подключено, папка:', ftp.pwd())
root = ftp.pwd()

dirs = set()
files = [f for f in LOCAL.rglob('*') if f.is_file()]
for i, f in enumerate(files, 1):
    rel = f.relative_to(LOCAL).as_posix()
    d = rel.rsplit('/', 1)[0] if '/' in rel else ''
    if d and d not in dirs:
        path = root
        for part in d.split('/'):
            path += '/' + part
            try:
                ftp.mkd(path)
            except ftplib.error_perm:
                pass
        dirs.add(d)
    with open(f, 'rb') as fh:
        ftp.storbinary(f'STOR {root}/{rel}', fh)
    print(f'[{i}/{len(files)}] {rel}')
ftp.quit()
print('Готово: загружено файлов —', len(files))
