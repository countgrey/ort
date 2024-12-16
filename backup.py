import sqlite3
import pandas as pd
import schedule
import time
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font

def save_to_excel():
    # Подключение к базе данных SQLite
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    
    # Получение списка колонок без 'id'
    cur.execute('PRAGMA table_info(viezd)')
    columns_info = cur.fetchall()
    columns = [column[1] for column in columns_info if column[1] != 'id']  # исключаем колонку 'id'
    
    # Формирование SQL-запроса без колонки 'id'
    query = f"SELECT {', '.join(columns)} FROM viezd"
    
    # Выполнение запроса
    cur.execute(query)
    db_data = cur.fetchall()
    
    # Заменяем заголовки на нужные
    new_columns = ["Время выезда", "Время начала съёмки", "Журналист", "Оператор", "Водитель", "Место назначения"]
    
    # Создание DataFrame из данных
    df = pd.DataFrame(db_data, columns=columns)
    
    # Применение новых заголовков
    df.columns = new_columns
    
    # Создание директории, если её нет
    backup_dir = 'backup'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Формирование имени файла с текущей датой
    current_date = datetime.now().strftime('%d-%m-%Y')
    file_path = os.path.join(backup_dir, f'{current_date}.xlsx')
    
    # Сохранение в Excel с использованием openpyxl для оформления
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
        workbook = writer.book
        sheet = workbook["Data"]
        
        # Оформление заголовков
        header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
        
        # Устанавливаем ширину столбцов
        column_widths = [15, 20, 20, 20, 20, 80]  # Примерные ширины для каждого столбца
        for i, width in enumerate(column_widths):
            sheet.column_dimensions[chr(65 + i)].width = width  # A=65, B=66, C=67 и т.д.
    
    print(f"Данные успешно сохранены в файл: {file_path}")

save_to_excel()

# Планирование задачи на 22:00 каждый день
schedule.every().day.at("22:00").do(save_to_excel)

# Цикл для выполнения задачи
while True:
    schedule.run_pending()
    time.sleep(60)  # Пауза в 1 минуту, чтобы не перегружать процессор
