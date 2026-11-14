"""Упаковка сайта в архив с версией: ../releases/<папка-сайта>-vN-ГГГГ-ММ-ДД.zip

python pack.py   — собирает сайт (build.py) и пакует public/ в новый архив со следующим номером версии.
"""
import datetime
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
REL = ROOT.parent / 'releases'
REL.mkdir(exist_ok=True)
NAME = 'svyazka'   # префикс архива

subprocess.run([sys.executable, str(ROOT / 'build.py')], check=True)

nums = [int(m.group(1)) for f in REL.glob(f'{NAME}-v*.zip') if (m := re.match(re.escape(NAME) + r'-v(\d+)-', f.name))]
ver = max(nums, default=0) + 1
out = REL / f'{NAME}-v{ver}-{datetime.date.today():%Y-%m-%d}.zip'
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted((ROOT / 'public').rglob('*')):
        if f.is_file():
            z.write(f, f.relative_to(ROOT / 'public').as_posix())
print(f'Архив: {out}  ({out.stat().st_size // 1_000_000} МБ)')
