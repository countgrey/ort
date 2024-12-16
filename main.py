import asyncio
import requests
import hashlib
import matplotlib.pyplot as plt
from telegram import Bot
from io import BytesIO
from bs4 import BeautifulSoup
from time import sleep

# Конфигурация Telegram Bot
TELEGRAM_TOKEN = "7136874120:AAF88ay_zJ2HDMuD1puy1eOpT8S2H9tILIs"
CHAT_ID = "-4744627600"

# URL сайта с таблицей
url = "http://192.168.0.114:5000"

# Глобальный хэш предыдущего состояния
previous_hash = None

# Функция для вычисления хэша данных
def compute_hash(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

# Функция для парсинга данных
async def parse_data():
    response = requests.get(url)
    response.raise_for_status()  # Проверяем, что запрос успешен

    # Разбираем HTML с помощью BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Ищем таблицу
    table = soup.find('table')  # Найдёт первую таблицу на странице; можно уточнить селектор

    # Извлекаем строки таблицы
    rows = table.find_all('tr')

    # Парсим заголовки (если есть)
    headers = [header.text.strip() for header in rows[0].find_all('th')]

    # Парсим данные строк
    data = []
    for row in rows[1:]:
        cells = row.find_all('td')
        data.append([cell.text.strip() for cell in cells])

    # Генерируем текстовое представление для хэширования
    data_text = "\n".join([",".join(row) for row in data])

    return headers, data, data_text

# Функция для создания изображения таблицы
def create_table_image(headers, data):
    # Создаем таблицу в формате текста для matplotlib
    table_data = [headers] + data

    # Создаем изображение с увеличенной шириной
    fig, ax = plt.subplots(figsize=(30, len(table_data) / 2))  # Увеличиваем ширину фигуры в 3 раза
    ax.axis('tight')
    ax.axis('off')

    # Создаем таблицу
    table = ax.table(cellText=table_data, loc='center', colLabels=None, cellLoc='center', bbox=[0, 0, 1, 1])

    # Настроим шрифт и масштабирование
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)  # Масштабируем таблицу

    # Увеличиваем ширину второго и шестого столбцов
    for (row, col), cell in table.get_celld().items():
        if col == 1:  # Второй столбец (нумерация с 0)
            cell.set_width(1.5 * cell.get_width())  # Увеличиваем ширину в 1.5 раза
        elif col == 5:  # Шестой столбец
            cell.set_width(5 * cell.get_width())  # Увеличиваем ширину в 5 раз

    # Сохраняем изображение в память
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)
    return buf

# Функция для отправки изображения в Telegram
async def send_image(bot, chat_id, image):
    # Отправляем изображение в Telegram
    await bot.send_photo(chat_id=chat_id, photo=image)

# Основной цикл для проверки изменений
async def monitor_changes():
    global previous_hash
    bot = Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            # Получаем текущие данные и их текстовое представление
            headers, data, data_text = await parse_data()

            # Вычисляем хэш текущих данных
            current_hash = compute_hash(data_text)

            # Проверяем, есть ли изменения
            if previous_hash is None or current_hash != previous_hash:
                print("Обнаружены изменения на сайте, отправляем обновление...")
                previous_hash = current_hash

                # Создаем изображение таблицы
                image = create_table_image(headers, data)

                # Отправляем изображение в Telegram
                await send_image(bot, CHAT_ID, image)
            else:
                print("Изменений нет, пропускаем отправку.")
        except Exception as e:
            print(f"Ошибка при проверке данных: {e}")

        # Ждем одну минуту перед следующей проверкой
        await asyncio.sleep(60)

# Запуск асинхронной задачи
if __name__ == "__main__":
    asyncio.run(monitor_changes())
