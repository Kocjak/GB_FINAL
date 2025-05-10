import csv
import mysql.connector
from datetime import datetime
import os
import Modules.Paths
from pathlib import Path


def add_service():
    try:
        # Устанавливаем соединение с базой данных
        connection = mysql.connector.connect(
            host='localhost',
            database='autocalendar',
            user='root',
            password='1111'
        )

        # Создаем список для хранения данных всех записей
        data_list = []

        # Запрашиваем у пользователя, сколько записей нужно добавить
        num_records = int(input("Введите количество записей, которые хотите добавить: "))

        # Цикл для ввода данных всех записей
        for i in range(num_records):
            ServiceName = input(f"\nВведите название услуги для записи {i + 1}: ")
            Duration = 1  # Часы, по умолчанию продолжительность сеанса - 1 час
            Cost = input(f"Введите стоимость услуги для записи {i + 1}: ")

            # Проверяем, что все обязательные параметры переданы
            if not ServiceName or not Cost:
                raise ValueError("Все поля должны быть заполнены")

            # Добавляем данные в список
            data_list.append((ServiceName, Duration, Cost))

        # Создаем SQL-запрос для массовой вставки
        insert_query = """
            INSERT INTO services (ServiceName, Duration, Cost)
            VALUES (%s, %s, %s)
        """

        # Выполняем массовую вставку
        cursor = connection.cursor()
        cursor.executemany(insert_query, data_list)
        connection.commit()

        # Возвращаем количество добавленных записей
        print(f"\nИнформация в количестве {cursor.rowcount} записей успешно добавлена")
        return cursor.rowcount


    except mysql.connector.Error as error:
        print(f"Ошибка при добавлении списка услуг: {error}")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def edit_service():
    try:
        # Устанавливаем соединение с базой данных
        connection = mysql.connector.connect(
            host='localhost',
            database='autocalendar',
            user='root',
            password='1111'
        )

        # Получаем список всех услуг
        cursor = connection.cursor()
        cursor.execute("SELECT id_service, ServiceName, Duration, Cost FROM services")
        services = cursor.fetchall()

        # Выводим список услуг
        if not services:
            print("В базе данных нет списка услуг")
            return False

        print("\nСписок услуг:")
        for service in services:
            print(f"ID: {service[0]}, Название: {service[1]}, Длительность: {service[2]}, Цена: {service[3]}")

        # Получаем ID услуги для редактирования
        id_service = input("\nВведите ID услуги для редактирования: ")

        # Проверяем, существует ли услуга с таким ID
        check_query = "SELECT * FROM services WHERE id_service = %s"
        cursor.execute(check_query, (id_service,))
        services = cursor.fetchone()

        if not services:
            raise ValueError("Услуга с таким ID не найдена")

        # Получаем новые данные
        ServiceName = input("Введите новое название (оставьте пустым, если не нужно менять): ")
        Duration = input("Введите новую длительность (оставьте пустым, если не нужно менять): ")
        Cost = input("Введите новую стоимость (оставьте пустым, если не нужно менять): ")

        # Формируем обновляемые поля
        update_fields = []
        update_values = []

        if ServiceName:
            update_fields.append("ServiceName = %s")
            update_values.append(ServiceName)
        if Duration:
            update_fields.append("Duration = %s")
            update_values.append(Duration)
        if Cost:
            update_fields.append("Cost = %s")
            update_values.append(Cost)

        # Если нет полей для обновления
        if not update_fields:
            raise ValueError("Не указано ни одного поля для обновления")

        # Создаем SQL-запрос
        update_query = f"UPDATE services SET {', '.join(update_fields)} WHERE id_service = %s"
        update_values.append(id_service)

        # Выполняем запрос
        cursor.execute(update_query, update_values)
        connection.commit()

        print(f"Информация об услуге с ID {id_service} успешно обновлена")
        return True

    except mysql.connector.Error as error:
        print(f"Ошибка при редактировании списка услуг: {error}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete_services():
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
        cursor.execute("SELECT id_service, ServiceName, Duration, Cost FROM services")
        services = cursor.fetchall()

        # Выводим список услуг
        if not services:
            print("В базе данных нет списка услуг")
            return False

        print("\nСписок услуг:")
        for service in services:
            print(f"ID: {service[0]}, Название: {service[1]}, Длительность: {service[2]}, Цена: {service[3]}")

        # Получаем ID услуги для удаления
        id_service = input("\nВведите ID мастера для удаления: ")

        # Проверяем, существует ли услуга с таким ID
        check_query = "SELECT * FROM services WHERE id_service = %s"
        cursor.execute(check_query, (id_service,))
        services = cursor.fetchone()

        if not services:
            raise ValueError("Услуга с таким ID не найдена")

        # Подтверждение удаления
        confirm = input(f"Вы уверены, что хотите удалить услугу с ID {id_service}? (да/нет): ")
        if confirm.lower() != 'да':
            print("Удаление отменено")
            return False

        # Создаем SQL-запрос на удаление
        delete_query = "DELETE FROM services WHERE id_service = %s"

        # Выполняем запрос
        cursor.execute(delete_query, (id_service,))
        connection.commit()

        print(f"Услуга с ID {id_service} успешно удалена")
        return True

    except mysql.connector.Error as error:
        print(f"Ошибка при удалении услуги: {error}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def show_service():
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
        cursor.execute("SELECT id_service, ServiceName, Duration, Cost FROM services")
        services = cursor.fetchall()

        if not services:
            print("В базе данных нет услуг")
            return False

        print("\nСписок услуг:")
        for service in services:
            print(f"ID: {service[0]}, Название: {service[1]}, Длительность: {service[2]}, Цена: {service[3]}")

    except mysql.connector.Error as error:
        print(f"Ошибка при получении списка услуг: {error}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def export_services_to_csv():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='autocalendar',
            user='root',
            password='1111'
        )

        cursor = connection.cursor()
        cursor.execute("SELECT id_service, ServiceName, Duration, Cost FROM services")
        masters = cursor.fetchall()

        if not masters:
            print("В базе данных нет списка услуг для экспорта")
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Создаем путь для сохранения файла используя созданный модуль Paths
        base_path = Modules.Paths.path_downloads()
        filename = os.path.join(base_path, f"masters_export_{timestamp}.csv")

        with open(filename, 'w', newline='', encoding='Windows-1251') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Название_услуги', 'Длительность', 'Цена'])  # Заголовки

            for master in masters:
                writer.writerow(master)

        print(f"\nДанные успешно экспортированы в файл {filename}")
        return True

    except mysql.connector.Error as error:
        print(f"Ошибка при экспорте списка услуг: {error}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def import_services_from_csv():
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
            print("\nВ директории нет CSV файлов для обработки")
            return False

        # Выводим список файлов для выбора
        print("Доступные файлы для импорта:")
        for i, file in enumerate(csv_files):
            print(f"{i + 1}. {file}")

        # Запрос ID файла у пользователя
        while True:
            try:
                file_id = int(input("\nВыберите номер файла для импорта: "))
                if 1 <= file_id <= len(csv_files):
                    selected_file = csv_files[file_id - 1]
                    break
                else:
                    print("Неверный номер файла")
            except ValueError:
                print("Пожалуйста, введите число")

        # Формируем полный путь к выбранному файлу
        file_path = Path(download_path) / selected_file

        with open(file_path, 'r', newline='', encoding='Windows-1251') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Пропускаем заголовок

            for row in reader:
                if all(row):
                    try:
                        id_service = int(row[0])

                        cursor.execute(
                            "UPDATE services SET ServiceName = %s, Duration = %s, Cost = %s WHERE id_service = %s",
                            (row[1], row[2], row[3], id_service)
                        )

                        connection.commit()

                    except ValueError:
                        print(f"Ошибка преобразования ID в строке: {row}")
                        continue
                else:
                    print("Пропущена строка с пустыми полями")
                    continue

        print("\nДанные успешно импортированы")

        # Очищаем директорию после успешной обработки
        try:
            os.remove(file_path)
            print(f"\nФайл {selected_file} успешно удален")
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")

        return True

    except mysql.connector.Error as error:
        print(f"Ошибка при импорте списка услуг: {error}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def show_menu():
    while True:
        # Форматируем меню с помощью f-strings и разделителей
        print("\n" + "*"*44)
        print("| МЕНЮ УПРАВЛЕНИЯ УПРАВЛЕНИЯ СПИСКОМ УСЛУГ |")
        print("*"*44)
        print("""
Доступные действия:

1. 👥 Добавить список услуг (в консоли)
2. ✏️ Отредактировать список услуг (в консоли)
3.  🗑 Удалить услугу (в консоли)
4. 📋 Показать список услуг (в консоли)
5. 📥 Экспортировать список услуг в csv (для изменения в csv)
6. 📤 Импортировать изменения из csv
7. 🚪 Вернуться в главное меню
        """)
        # Добавляем подсказку и валидацию ввода
        try:
            choice = int(input("Введите номер действия: "))
            if 1 <= choice <= 7:
                if choice == 1:
                    add_service()
                elif choice == 2:
                    edit_service()
                elif choice == 3:
                    delete_services()
                elif choice == 4:
                    show_service()
                elif choice == 5:
                    export_services_to_csv()
                elif choice == 6:
                    import_services_from_csv()
                elif choice == 7:
                    print("\nДо свидания! 👋")
                    break
            else:
                print("\n❌ Неверный выбор, введите число от 1 до 7")
        except ValueError:
            print("\n❌ Пожалуйста, введите число")

if __name__ == "__main__":
    show_menu()
