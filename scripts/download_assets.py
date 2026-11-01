"""Unduh ulang sembilan foto ilustratif berlisensi Unsplash sebagai WebP lokal."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen
import json

root = Path(__file__).resolve().parents[1]
folder = root / 'frontend/public/images/rooms'
credits = json.loads((folder / 'credits.json').read_text(encoding='utf-8'))

def download(item):
    target = folder / item['file']
    url = f'https://images.unsplash.com/{item["image"]}?fit=crop&w=960&h=640&q=80&fm=webp'
    with urlopen(url, timeout=45) as response:
        data = response.read()
        if response.headers.get_content_type() != 'image/webp' or data[:4] != b'RIFF':
            raise RuntimeError(f'Unduhan bukan WebP: {item["file"]}')
    target.write_bytes(data)
    return f'{target.name}: {len(data)} bytes'

if __name__ == '__main__':
    with ThreadPoolExecutor(3) as pool:
        for result in pool.map(download, credits):
            print(result)
