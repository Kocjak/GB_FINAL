import mysql.connector
from telebot import types

#Подключение
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        database='autocalendar',
        user='root',
        password='1111'
    )

#Функция для получения списка услуг
def get_service_list():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM services
        ''')

        sevices = cursor.fetchall()

        # Создаем клавиатуру
        keyboard_service = types.InlineKeyboardMarkup()
        for sevice in sevices:
            keyboard_service.add(types.InlineKeyboardButton(
                text=f"{sevice[1]} - {sevice[3]} руб.",
                callback_data=f"select_service_{sevice[0]}"
            ))

        return keyboard_service

# Функция для получения списка мастеров
def get_masters_list():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id_master, FIO FROM Masters")
        masters = cursor.fetchall()

        # Создаем клавиатуру
        keyboard_masters = types.InlineKeyboardMarkup()
        for master in masters:
            keyboard_masters.add(types.InlineKeyboardButton(
                text=f"{master[1]}",
                callback_data=f"select_master_{master[0]}"
            ))

        return keyboard_masters

# Функция для получения доступных слотов
def get_free_slots(master_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
             SELECT DATE(start_time) AS Дата, t2.FIO, COUNT(*) 
             FROM schedule t1
         	 JOIN masters t2 ON t1.id_master=t2.id_master 
             WHERE status = 'open' AND t1.id_master = %s AND 
             t1.id NOT IN (SELECT id_schedule FROM bookings)
             GROUP BY DATE(start_time), t2.FIO
             HAVING COUNT(*) > 0 
             ORDER BY DATE(start_time)
             LIMIT 7
         ''', (master_id,))

        slots = cursor.fetchall()

        # Добавляем проверку на отсутствие слотов
        if not slots:
            return False

        # Создаем клавиатуру
        keyboard_date = types.InlineKeyboardMarkup()
        for slot in slots:
            keyboard_date.add(types.InlineKeyboardButton(
                text=f"Дата: {slot[0]}, доступный(ые) слот(ы): {slot[2]}",
                callback_data=f"select_date_{slot[0]}"
            ))

        return keyboard_date

#Функция для выбора времени
def get_free_hours(date_str, master_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, HOUR(start_time) as Hour, t2.FIO
            FROM schedule t1
            JOIN masters t2 ON t1.id_master=t2.id_master 
            WHERE status = 'open' AND t1.id_master = %s AND DATE(start_time)=%s AND 
             t1.id NOT IN (SELECT id_schedule FROM bookings)
        ''', (master_id, date_str))

        times = cursor.fetchall()
        # Создаем клавиатуру
        keyboard_date = types.InlineKeyboardMarkup()
        for time in times:
            keyboard_date.add(types.InlineKeyboardButton(
                text=f"Час: {time[1]}",
                callback_data=f"select_time_{time[0]}"
            ))

        return keyboard_date

#Функция для получения client_id
def get_client_id(client_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id_client FROM clients
            WHERE	clients.login=%s
        ''', (client_id, ))

        id_client = cursor.fetchone()

        return id_client[0] if id_client else None






