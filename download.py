import os
import requests
from tqdm import tqdm

# Функция для скачивания файла
def download_file(url, destination):
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        total_size = int(response.headers.get('Content-Length', 0))
        with open(destination, 'wb') as f, tqdm(
            desc=destination,
            total=total_size,
            unit='B',
            unit_scale=True,
            ncols=100
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                f.write(data)
                bar.update(len(data))
    else:
        print(f"Ошибка при скачивании файла: {response.status_code}")

# Пример URL для скачивания файла из публичной папки
file_url = 'https://disk.yandex.ru/d/DeydF2pH_gMSIA'  # Замените на ваш реальный URL файла
destination = 'downloaded_file.zip'  # Имя для сохранённого файла

download_file(file_url, destination)
