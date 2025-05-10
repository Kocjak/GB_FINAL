import csv
import mysql.connector
from datetime import datetime
import os
import Modules.Paths
from pathlib import Path


def add_master():
    try:
        # Устанавливаем соединение с базой данных
        connection = mysql.connector.connect(
            host='localhost',
            database='autocalendar',
            user='root',
            password='1111'
        )

        # Создаем SQL-запрос с использованием параметров
        insert_query = """
            INSERT INTO masters (FIO, Login, PhoneNumber)
            VALUES (%s, %s, %s)
        """

        # Создаем список для хранения всех записей
        records = []

        while True:
            fio = input("\nВведите ФИО пользователя (или 'exit' для завершения): ")
            if fio.lower() == 'exit':
                break

            login = input("Введите логин пользователя: ")
            phone_number = input("Введите номер пользователя: ")

            # Проверяем, что все обязательные параметры переданы
            if not fio or not login or not phone_number:
                raise ValueError("Все поля должны быть заполнены")

            records.append((fio, login, phone_number))

        # Выполняем массовые вставки
        cursor = connection.cursor()
        cursor.executemany(insert_query, records)
        connection.commit()

        print(f"──────────────────────────────")
        print(f"Успешно добавлено {len(records)} записей!")
        print(f"──────────────────────────────")
        return cursor.lastrowid

    except mysql.connector.Error as error:
        print(f"──────────────────────────────")
        print(f"Ошибка при добавлении мастеров: {error}")
        print(f"──────────────────────────────")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def edit_master():
    try:
        # Устанавливаем соединение с базой данных
        connection = mysql.connector.connect(
            host='localhost',
            database='autocalendar',
            user='root',
            password='1111'
        )

        # Получаем список всех мастеров
        cursor = connection.cursor()
        cursor.execute("SELECT id_master, FIO, Login, PhoneNumber FROM masters")
        masters = cursor.fetchall()

        # Выводим список мастеров
        if not masters:
            print(f"──────────────────────────────")
            print("В базе данных нет мастеров")
            print(f"──────────────────────────────")
            return False

        print(f"──────────────────────────────")
        print("\nСписок мастеров:")
        print(f"──────────────────────────────")
        for master in masters:
            print(f"ID: {master[0]}, ФИО: {master[1]}, Логин: {master[2]}, Телефон: {master[3]}")

        # Получаем ID мастера для редактирования
        master_id = input("\nВведите ID мастера для редактирования: ")

        # Проверяем, существует ли мастер с таким ID
        check_query = "SELECT * FROM masters WHERE id_master = %s"
        cursor.execute(check_query, (master_id,))
        master = cursor.fetchone()

        if not master:
            raise ValueError("Мастер с таким ID не найден")

        # Получаем новые данные
        fio = input("Введите новое ФИО (оставьте пустым, если не нужно менять): ")
        login = input("Введите новый логин (оставьте пустым, если не нужно менять): ")
        phone_number = input("Введите новый номер телефона (оставьте пустым, если не нужно менять): ")

        # Формируем обновляемые поля
        update_fields = []
        update_values = []

        if fio:
            update_fields.append("FIO = %s")
            update_values.append(fio)
        if login:
            update_fields.append("Login = %s")
            update_values.append(login)
        if phone_number:
            update_fields.append("PhoneNumber = %s")
            update_values.append(phone_number)

        # Если нет полей для обновления
        if not update_fields:
            raise ValueError("Не указано ни одного поля для обновления")

        # Создаем SQL-запрос
        update_query = f"UPDATE masters SET {', '.join(update_fields)} WHERE id_master = %s"
        update_values.append(master_id)

        # Выполняем запрос
        cursor.execute(update_query, update_values)
        connection.commit()

        print(f"Информация мастера с ID {master_id} успешно обновлена")
        return True

    except mysql.connector.Error as error:
        print(f"Ошибка при редактировании мастера: {error}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete_master():
    try:
        # Устанавливаем соединение с базой данных
        connection = mysql.connector.connect(
            host='localhost',
            database='autocalendar',
            user='root',
            password='1111'
        )

        # Получаем список всех мастеров
        cursor = connection.cursor()
        cursor.execute("SELECT id_master, FIO, Login, PhoneNumber FROM masters")
        masters = cursor.fetchall()

        # Выводим список мастеров
        if not masters:
            print(f"──────────────────────────────")
            print("В базе данных нет мастеров")
            return False

        print(f"──────────────────────────────")
        print("\nСписок мастеров:")
        print(f"──────────────────────────────")
        for master in masters:
            print(f"ID: {master[0]}, ФИО: {master[1]}, Логин: {master[2]}, Телефон: {master[3]}")

        # Получаем ID мастера для удаления
        master_id = input("\nВведите ID мастера для удаления: ")

        # Проверяем, существует ли мастер с таким ID
        check_query = "SELECT * FROM masters WHERE id_master = %s"
        cursor.execute(check_query, (master_id,))
        master = cursor.fetchone()

        if not master:
            raise ValueError("Мастер с таким ID не найден")

        # Подтверждение удаления
        confirm = input(f"Вы уверены, что хотите удалить мастера с ID {master_id}? (да/нет): ")
        if confirm.lower() != 'да':
            print(f"──────────────────────────────")
            print("Удаление отменено")
            print(f"──────────────────────────────")
            return False

        # Создаем SQL-запрос на удаление
        delete_query = "DELETE FROM masters WHERE id_master = %s"

        # Выполняем запрос
        cursor.execute(delete_query, (master_id,))
        connection.commit()

        print(f"──────────────────────────────")
        print(f"Мастер с ID {master_id} успешно удален")
        print(f"──────────────────────────────")
        return True

    except mysql.connector.Error as error:
        print(f"──────────────────────────────")
        print(f"Ошибка при удалении мастера: {error}")
        print(f"──────────────────────────────")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def show_master():
    try:
        # Устанавливаем соединение с базой данных
        connection = mysql.connector.connect(
            host='localhost',
            database='autocalendar',
            user='root',
            password='1111'
        )

        # Получаем список всех мастеров
        cursor = connection.cursor()
        cursor.execute("SELECT id_master, FIO, Login, PhoneNumber FROM masters")
        masters = cursor.fetchall()

        if not masters:
            print(f"──────────────────────────────")
            print("В базе данных нет мастеров")
            print(f"──────────────────────────────")
            return False

        print(f"──────────────────────────────")
        print("\nСписок мастеров:")
        print(f"──────────────────────────────")
        for master in masters:
            print(f"ID: {master[0]}, ФИО: {master[1]}, Логин: {master[2]}, Телефон: {master[3]}")

    except mysql.connector.Error as error:
        print(f"──────────────────────────────")
        print(f"Ошибка при получении списка мастеров: {error}")
        print(f"──────────────────────────────")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def export_masters_to_csv():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='autocalendar',
            user='root',
            password='1111'
        )

        cursor = connection.cursor()
        cursor.execute("SELECT id_master, FIO, Login, PhoneNumber FROM masters")
        masters = cursor.fetchall()

        if not masters:
            print(f"──────────────────────────────")
            print("В базе данных нет мастеров для экспорта")
            print(f"──────────────────────────────")
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Создаем путь для сохранения файла используя созданный модуль Paths
        base_path = Modules.Paths.path_downloads()
        filename = os.path.join(base_path, f"masters_export_{timestamp}.csv")

        with open(filename, 'w', newline='', encoding='Windows-1251') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'ФИО', 'Логин', 'Телефон'])  # Заголовки

            for master in masters:
                writer.writerow(master)

        print(f"──────────────────────────────")
        print(f"\nДанные успешно экспортированы в файл {filename}")
        print(f"──────────────────────────────")
        return True

    except mysql.connector.Error as error:
        print(f"──────────────────────────────")
        print(f"Ошибка при экспорте мастеров: {error}")
        print(f"──────────────────────────────")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def import_masters_from_csv():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='autocalendar',
            user='root',
            password='1111'
        )

        cursor = connection.cursor()

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

        with open(file_path, 'r', newline='', encoding='Windows-1251') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Пропускаем заголовок

            for row in reader:
                if all(row):
                    try:
                        id_master = int(row[0])

                        cursor.execute(
                            "UPDATE masters SET FIO = %s, Login = %s, PhoneNumber = %s WHERE id_master = %s",
                            (row[1], row[2], row[3], id_master)
                        )

                        connection.commit()

                    except ValueError:
                        print(f"──────────────────────────────")
                        print(f"Ошибка преобразования ID в строке: {row}")
                        print(f"──────────────────────────────")
                        continue
                else:
                    print(f"──────────────────────────────")
                    print("Пропущена строка с пустыми полями")
                    print(f"──────────────────────────────")
                    continue

        print(f"──────────────────────────────")
        print("\nДанные успешно импортированы")
        print(f"──────────────────────────────")

        # Очищаем директорию после успешной обработки
        try:
            os.remove(file_path)
            print(f"──────────────────────────────")
            print(f"\nФайл {selected_file} успешно удален")
            print(f"──────────────────────────────")
        except Exception as e:
            print(f"──────────────────────────────")
            print(f"Ошибка при удалении файла: {e}")
            print(f"──────────────────────────────")

        return True

    except mysql.connector.Error as error:
        print(f"──────────────────────────────")
        print(f"Ошибка при импорте мастеров: {error}")
        print(f"──────────────────────────────")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def show_menu():
    while True:
        # Форматируем меню с помощью f-strings и разделителей
        print("\n" + "*"*47)
        print("| МЕНЮ УПРАВЛЕНИЯ УПРАВЛЕНИЯ СПИСКОМ МАСТЕРОВ |")
        print("*"*47)
        print("""
Доступные действия:

1. 👥 Добавить мастера(ов) (в консоли)
2. ✏️ Отредактировать записи по мастерам (в консоли)
3. 🗑 Удалить мастера (в консоли)
4. 📋 Показать список мастеров (в консоли)
5. 📥 Экспортировать список мастеров в csv (для изменения в csv)
6. 📤 Импортировать изменения из csv
7. 🚪 Вернуться в главное меню
        """)
        # Добавляем подсказку и валидацию ввода
        try:
            choice = int(input("Введите номер действия: "))
            if 1 <= choice <= 7:
                if choice == 1:
                    add_master()
                elif choice == 2:
                    edit_master()
                elif choice == 3:
                    delete_master()
                elif choice == 4:
                    show_master()
                elif choice == 5:
                    export_masters_to_csv()
                elif choice == 6:
                    import_masters_from_csv()
                elif choice == 7:
                    print("\nДо свидания! 👋")
                    break
            else:
                print("\n❌ Неверный выбор, введите число от 1 до 7")
        except ValueError:
            print("\n❌ Пожалуйста, введите число")

if __name__ == "__main__":
    show_menu()


