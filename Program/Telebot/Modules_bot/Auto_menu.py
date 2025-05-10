import mysql.connector
from telebot import types
import telebot

#Подключение
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        database='autocalendar',
        user='root',
        password='1111'
    )

# Функция для получения списка записей для пользователя
def get_appointments_list(chat_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Дата, Час, ФИО_Мастера, Услуга, `Цена, руб` FROM `записанные пользователи` WHERE id_пользователя=%s",
            (chat_id,))
        appointments = cursor.fetchall()

        if not appointments:
            return "У вас нет записей"

        result = "Ваши записи:\n"
        for appointment in appointments:
            result += f"Дата: {appointment[0]}\n"
            result += f"Время: {appointment[1]}\n"
            result += f"Мастер: {appointment[2]}\n"
            result += f"Услуга: {appointment[3]}\n"
            result += f"Цена: {appointment[4]} руб.\n\n"

        return result

# Функция для удаления записей
def get_booking_id(chat_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id_booking, START_time AS Время, servicename AS Услуга FROM bookings t1
                        JOIN clients t2 ON t2.id_client=t1.id_client 
                        JOIN schedule t3 ON t3.id=t1.id_schedule
                        join services t4 on t4.id_service = t1.id_service
                        WHERE t2.Login=%s''',
            (chat_id,))
        appointments = cursor.fetchall()

        if not appointments:
            return "У вас нет записей для отмены"

        # Создаем клавиатуру
        keyboard_appointments = types.InlineKeyboardMarkup()
        for appointment in appointments:
            keyboard_appointments.add(types.InlineKeyboardButton(
                text=f"Время: {appointment[1]}, Услуга: {appointment[2]}",
                callback_data=f"select_appointment_{appointment[0]}"
            ))

        return keyboard_appointments

#Функция для удаления записи
def delete_booking(id_booking):
    with get_connection() as conn:
        cursor = conn.cursor()

        # Проверяем существование записи перед удалением
        cursor.execute(
            "SELECT COUNT(*) FROM bookings WHERE id_booking = %s",
            (id_booking,)
        )

        if cursor.fetchone()[0] == 0:
            return False  # Запись не найдена

        # Выполняем удаление
        cursor.execute(
            "DELETE FROM bookings WHERE id_booking = %s",
            (id_booking,)
        )

        # Проверяем количество удаленных строк
        if cursor.rowcount == 0:
            return False  # Удаление не произошло

        conn.commit()
        return True
