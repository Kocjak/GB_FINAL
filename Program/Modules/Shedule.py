import csv
import datetime
import os
import mysql.connector
from mysql.connector import Error
import Modules.Paths
from pathlib import Path
from datetime import datetime, time, timedelta

#Подключение
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        database='autocalendar',
        user='root',
        password='1111'
    )

#Получение списка файлов (вложена в show_menu)
def list_csv():
    # Получаем путь к директории загрузок
    download_path = Modules.Paths.path_downloads()

    # Получаем список CSV файлов в директории
    csv_files = [f for f in os.listdir(download_path) if f.endswith('.csv')]
    if not csv_files:
        print(f"──────────────────────────────")
        print("\nВ директории нет CSV файлов для обработки")
        print(f"──────────────────────────────")
        return False
    # Выводим список файлов для выбора
    print(f"──────────────────────────────")
    print("Доступные файлы для импорта:")
    print(f"──────────────────────────────")
    for i, file in enumerate(csv_files):
        print(f"{i + 1}. {file}")

    # Запрос ID файла у пользователя
    while True:
        try:
            print(f"──────────────────────────────")
            file_id = int(input("\nВыберите номер файла для импорта: "))
            print(f"──────────────────────────────")
            if 1 <= file_id <= len(csv_files):
                selected_file = csv_files[file_id - 1]
                break
            else:
                print(f"──────────────────────────────")
                print("Неверный номер файла")
                print(f"──────────────────────────────")
        except ValueError:
            print(f"──────────────────────────────")
            print("Пожалуйста, введите число")
            print(f"──────────────────────────────")

    # Формируем полный путь к выбранному файлу
    file_path = Path(download_path) / selected_file
    return file_path

#Функция получения списка мастеров (вложена в show_menu)
def get_masters():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id_master, FIO, Login, PhoneNumber FROM Masters")
        return cursor.fetchall()

#Функция получения текущего расписания (вложена в создание)
def get_existing_schedule(master_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT start_time, end_time 
                FROM Schedule 
                WHERE id_master = %s 
            """, (master_id, ))

            return cursor.fetchall()
    except Error as e:
        print(f"Ошибка при получении расписания: {e}")
        return []

#Функция создания расписания
def create_schedule(start_date, end_date, work_start, work_end, master_id):
    # Получаем существующее расписание
    existing_slots = get_existing_schedule(master_id)
    existing_slots_set = {(slot[0], slot[1]) for slot in existing_slots}

    with get_connection() as conn:
        cursor = conn.cursor()
        current_date = start_date

        while current_date <= end_date:
            start_time = datetime.combine(current_date, work_start)
            end_time = datetime.combine(current_date, work_end)

            while start_time < end_time:
                slot_start = start_time
                slot_end = start_time + timedelta(hours=1)

                # Проверяем, есть ли такой слот в существующем расписании
                if (slot_start, slot_end) not in existing_slots_set:
                    cursor.execute("""
                        INSERT INTO Schedule (start_time, end_time, status, id_master) 
                        VALUES (%s, %s, 'open', %s)
                    """, (slot_start, slot_end, master_id))

                start_time += timedelta(hours=1)

            current_date += timedelta(days=1)
        conn.commit()
        print("\n🎯 Расписание успешно создано без дубликатов!")

#Функция импорта расписания
def import_schedule(file_path, master_id):
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            next(reader)  # пропускаем заголовок

            with get_connection() as conn:
                cursor = conn.cursor()
                for row in reader:
                    try:
                        # Конвертируем формат даты
                        start_time = datetime.strptime(row[1], '%d.%m.%Y %H:%M')
                        end_time = datetime.strptime(row[2], '%d.%m.%Y %H:%M')

                        cursor.execute("""
                        UPDATE Schedule 
                        SET start_time = %s, end_time = %s, status = %s
                        WHERE id = %s AND id_master = %s
                        """, (start_time, end_time, row[3], row[0], master_id))
                    except ValueError as ve:
                        print(f"Ошибка конвертации даты в строке: {row}")
                        print(f"Сообщение ошибки: {ve}")
                        continue
                conn.commit()

        print("Данные успешно обновлены")
        return True
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return False

#Функция экспорта расписания
def export_schedule(master_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Schedule WHERE id_master = %s and status = 'open'", (master_id,))
            rows = cursor.fetchall()

            base_path = Modules.Paths.path_downloads()
            filename = os.path.join(base_path, f"schedule_{master_id}.csv")
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['id', 'start_time', 'end_time', 'status', 'id_master'])
                for row in rows:
                    writer.writerow(row)

            print(f"Файл успешно сохранен: {filename}")
            return True

    except Error as e:
        print(f"Ошибка при экспорте: {e}")
        return False

#Функция меню
def show_menu():
    while True:
        print("\n" + "*" * 29)
        print("| МЕНЮ РАБОТЫ С РАСПИСАНИЕМ |")
        print("*" * 29)

        print("\nВыберите действие:")
        print("1. 📅 Создать расписание")
        print("2. 📋 Импортировать расписание")
        print("3. 📥 Выгрузить текущее расписание")
        print("4. 🔙 Вернуться в главное меню")

        choice = input("\nВаш выбор: ")

        if choice == '1':
            if choice == '1':
                try:
                    masters = get_masters()
                    print("\nСписок мастеров:")
                    for master in masters:
                        print(f"ID: {master[0]}, {master[1]}, Телефон: {master[3]}")

                    master_id = int(input("\nВведите ID мастера: "))

                    # Получаем начальную дату от пользователя
                    start_year = int(input("Введите год начала расписания (YYYY): "))
                    start_month = int(input("Введите месяц начала расписания (MM): "))
                    start_day = int(input("Введите день начала расписания (DD): "))
                    start_date = datetime(start_year, start_month, start_day)

                    # Получаем конечную дату от пользователя
                    end_year = int(input("\nВведите год окончания расписания (YYYY): "))
                    end_month = int(input("Введите месяц окончания расписания (MM): "))
                    end_day = int(input("Введите день окончания расписания (DD): "))
                    end_date = datetime(end_year, end_month, end_day)

                    # Получаем время начала работы
                    work_start_hour = int(input("\nВведите час начала работы (HH): "))
                    work_start_minute = int(input("Введите минуту начала работы (MM): "))
                    work_start = time(work_start_hour, work_start_minute)

                    # Получаем время окончания работы
                    work_end_hour = int(input("\nВведите час окончания работы (HH): "))
                    work_end_minute = int(input("Введите минуту окончания работы (MM): "))
                    work_end = time(work_end_hour, work_end_minute)

                    create_schedule(start_date, end_date, work_start, work_end, master_id)

                except ValueError as e:
                    print(f"Ошибка ввода данных: {e}")
                except Exception as e:
                    print(f"Произошла ошибка: {e}")

        elif choice == '2':
            masters = get_masters()
            print("\nСписок мастеров:")
            for master in masters:
                print(f"ID: {master[0]}, {master[1]}, Телефон: {master[3]}")

            master_id = int(input("\nВведите ID мастера: "))
            file_path = list_csv()
            if os.path.exists(file_path):
                import_schedule(file_path, master_id)
            else:
                print("❌ Файл не найден!")

        elif choice == '3':
            masters = get_masters()
            print("\nСписок мастеров:")
            for master in masters:
                print(f"ID: {master[0]}, {master[1]}, Телефон: {master[3]}")

            master_id = int(input("\nВведите ID мастера: "))
            export_schedule(master_id)

        elif choice == '4':
            break

        else:
            print("⚠️ Неверный выбор!")

if __name__ == "__main__":
    show_menu()
