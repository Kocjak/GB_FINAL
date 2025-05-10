import win32serviceutil
import time
import mysql.connector
from mysql.connector import Error


# Функция получения статуса службы (вложена в функцию управления)
def get_service_status(service):
    status = (win32serviceutil.QueryServiceStatus(service)[1] == 4)
    if not status:
        time.sleep(3)
        status = (win32serviceutil.QueryServiceStatus(service)[1] == 4)
    return status

# Функция остановки службы (вложена в функцию управления)
def stop_service(service):
    if get_service_status(service):
        win32serviceutil.StopService(service)
        if get_service_status(service):
            print(f"──────────────────────────────")
            print(f"\033[91mНе удалось остановить службу ({service}) (???)\033[0m")
            print(f"──────────────────────────────")
            return False
        print(f"──────────────────────────────")
        print(f"\033[92mСлужба ({service}) успешно остановлена\033[0m")
        print(f"──────────────────────────────")
        return True
    else:
        print(f"──────────────────────────────")
        print(f"\033[91mНе удалось остановить службу ({service}), т.к. она не запущена\033[0m")
        print(f"──────────────────────────────")
        return False

# Функция запуска службы (вложена в функцию управления)
def start_service(service):
    if not get_service_status(service):
        win32serviceutil.StartService(service)
        if not get_service_status(service):
            print(f"──────────────────────────────")
            print(f"\033[91mНе удалось запустить службу ({service}) (???)\033[0m")
            print(f"──────────────────────────────")
            return False
        print(f"──────────────────────────────")
        print(f"\033[92mСлужба ({service}) запущена успешно\033[0m")
        print(f"──────────────────────────────")
        return True
    else:
        print(f"──────────────────────────────")
        print(f"\033[91mНе удалось запустить службу ({service}), уже запущена\033[0m")
        print(f"──────────────────────────────")
        return False

# Функция управления службой
def service_info(action, service):
    action = action.lower()
    servnam = f'service ({service})'

    if action == 'stop':
        return stop_service(service)
    elif action == 'start':
        return start_service(service)
    elif action == 'status':
        if get_service_status(service):
            print(f"──────────────────────────────")
            print(f"\033[92m{servnam} запущена\033[0m")
            print(f"──────────────────────────────")
        else:
            print(f"──────────────────────────────")
            print(f"\033[92m{servnam} остановлена\033[0m")
            print(f"──────────────────────────────")
        return None
    else:
        print(f"──────────────────────────────")
        print(f"\033[93mНеизвестное событие ({action}) при вызове службы {servnam}\033[0m")
        print(f"──────────────────────────────")
        return None

# Функция создания БД
def create_database():
    try:
        # Создаем соединение с MySQL
        connection = mysql.connector.connect(
            host="localhost",
            user=input("\nВведите имя пользователя: "),
            password=input("Введите пароль: "),
            auth_plugin='mysql_native_password'  # для совместимости
        )

        # Создаем базу данных
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS Autocalendar")
        print("База данных успешно создана")

        # Подключаемся к созданной базе данных
        connection.database = "Autocalendar"

        # Создаем таблицу Clients
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Clients (
                id_client INT AUTO_INCREMENT PRIMARY KEY,
                FIO VARCHAR(100) NOT NULL,
                Login BIGINT UNIQUE NOT NULL,
                Password VARCHAR(255) NOT NULL,  -- добавлено поле для пароля
                PhoneNumber VARCHAR(20) NOT NULL
            )
        ''')

        # Создаем таблицу Masters
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Masters (
            id_master INT AUTO_INCREMENT PRIMARY KEY,
            FIO VARCHAR(100) NOT NULL,
            Login VARCHAR(50) UNIQUE NOT NULL,
            PhoneNumber VARCHAR(20) NOT NULL
        )
        ''')



        # Создаем таблицу Services
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Services (
            id_service INT AUTO_INCREMENT PRIMARY KEY,
            ServiceName VARCHAR(100) NOT NULL,
            DURATION INT NOT NULL,
            Cost INT NOT NULL
        )
        ''')

        # Создаем таблицу Schedule с нужной структурой
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Schedule (
            id INT AUTO_INCREMENT PRIMARY KEY,
            start_time DATETIME,
            end_time DATETIME,
            status VARCHAR(10) DEFAULT 'closed',
            id_master INT,
            FOREIGN KEY (id_master) REFERENCES Masters(id_master)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
        ''')

        # Создаем таблицу Bookings с нужной структурой для записи клиентов
        cursor.execute('''CREATE TABLE IF NOT EXISTS Bookings (
            id_booking INT AUTO_INCREMENT PRIMARY KEY,
            id_client INT NOT NULL,
            id_schedule INT NOT NULL,
            id_service INT NOT NULL,
            booking_status VARCHAR(20) DEFAULT 'Забронировано',  
            FOREIGN KEY (id_client) REFERENCES Clients(id_client)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (id_schedule) REFERENCES Schedule(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (id_service) REFERENCES Services(id_service)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
        ''')

        try:
            # Создаем представление
            cursor.execute('''
            CREATE ALGORITHM = UNDEFINED DEFINER=`root`@`localhost` 
            SQL SECURITY DEFINER 
            VIEW `записанные пользователи` AS 
            SELECT 
                CAST(t2.start_time AS DATE) AS `Дата`,
                HOUR(t2.start_time) AS `Час`,
                t3.FIO AS `ФИО_Мастера`,
                t4.ServiceName AS `Услуга`,
                t4.Cost AS `Цена, руб`,
                t5.login AS 'ID_пользователя' 
            FROM 
                bookings t1 
                JOIN schedule t2 ON (t2.id = t1.id_schedule)
                JOIN masters t3 ON (t3.id_master = t2.id_master)
                JOIN services t4 ON (t4.id_service = t1.id_service)
                JOIN clients t5 ON (t5.id_client=t1.id_client)
            WHERE 
                t1.booking_status = 'Забронировано'
            ''')
            connection.commit()
            print("VIEW успешно создан")
        except mysql.connector.Error as err:
            print(f"Ошибка при создании VIEW: {err}")

        # Создаем EVENT для обновления VIEW
        cursor.execute('''
        CREATE EVENT IF NOT EXISTS update_view_event
        ON SCHEDULE EVERY 5 MINUTE
        STARTS CURRENT_TIMESTAMP
        DO
        BEGIN
            DROP VIEW IF EXISTS `записанные пользователи`;
            CREATE ALGORITHM = UNDEFINED DEFINER=`root`@`localhost` 
            SQL SECURITY DEFINER 
            VIEW `записанные пользователи` AS 
            SELECT 
                CAST(t2.start_time AS DATE) AS `Дата`,
                HOUR(t2.start_time) AS `Час`,
                t3.FIO AS `ФИО_Мастера`,
                t4.ServiceName AS `Услуга`,
                t4.Cost AS `Цена, руб`,
                t5.login AS 'ID_пользователя' 
            FROM 
                bookings t1 
                JOIN schedule t2 ON (t2.id = t1.id_schedule)
                JOIN masters t3 ON (t3.id_master = t2.id_master)
                JOIN services t4 ON (t4.id_service = t1.id_service)
                JOIN clients t5 ON (t5.id_client=t1.id_client)
            WHERE 
                t1.booking_status = 'Забронировано';
        END
        ''')

        # Создаем EVENT для автоматической проверки, если есть запись в bookings
        cursor.execute('''
        CREATE EVENT IF NOT EXISTS auto_check_slots
        ON SCHEDULE EVERY 15 MINUTE
        STARTS CURRENT_TIMESTAMP
        DO
        BEGIN
         UPDATE schedule 
         SET status = 'closed'
         WHERE status = 'open' 
         AND start_time < NOW() 
         AND NOT EXISTS (
         SELECT 1 FROM bookings 
         WHERE id_schedule = schedule.id
         );
        END
        ''')

        # Триггер для вставки
        cursor.execute('''
        CREATE TRIGGER update_status_on_insert
        BEFORE INSERT ON schedule
        FOR EACH ROW
        SET NEW.status = IF(NEW.status IS NULL, 
                            IF(NEW.start_time < NOW(), 'closed', 'open'), 
                            NEW.status)
        ''')

        # Триггер для обновления
        cursor.execute('''
        CREATE TRIGGER update_status_on_update
        BEFORE UPDATE ON schedule
        FOR EACH ROW
        SET NEW.status = IF(NEW.status IS NULL, 
                            IF(NEW.start_time < NOW(), 'closed', 'open'), 
                            NEW.status)
        ''')



        connection.commit()
        print("\nТаблицы успешно созданы")

    except Error as e:
        print(f"Произошла ошибка: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Соединение закрыто")


# Функция меню выбора действия
def show_menu():
    while True:
        # Форматируем меню с помощью f-strings и разделителей
        print("\n" + "*"*46)
        print("| МЕНЮ  НАСТРОЙКИ СЛУЖБЫ MySQL И СОЗДАНИЯ БД |")
        print("*"*46)
        print("""
Доступные действия:

1. 📥 Получить текущий статус службы
2. 📥 Запустить службу
3. 📥 Остановить служб
4. ✏️ Создать базу данных
5. 🚪 Вернуться в главное меню
        """)
        # Добавляем подсказку и валидацию ввода
        try:
            service = 'MySQL93'
            choice = int(input("Введите номер действия: "))
            if 1 <= choice <= 5:
                if choice == 1:
                    service_info('status', service)
                elif choice == 2:
                    service_info('start', service)
                elif choice == 3:
                    service_info('stop', service)
                elif choice == 4:
                    create_database()
                elif choice == 5:
                    print("\nДо свидания! 👋")
                    break
            else:
                print("\n❌ Неверный выбор, введите число от 1 до 5")
        except ValueError:
            print("\n❌ Пожалуйста, введите число")


if __name__ == '__main__':
    show_menu()
