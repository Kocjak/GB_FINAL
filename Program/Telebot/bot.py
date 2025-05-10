import telebot
from charset_normalizer import from_path
from pycparser.c_ast import Return
from sqlalchemy.sql.operators import from_
from telebot import types
import mysql.connector
import datetime
import Modules_bot.keyboard as M_key
import Modules_bot.Auto_menu as A_key
import logging

#Вот это дефолтные вещи:
# Инициализация бота
bot = telebot.TeleBot("")
#Подключение
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        database='autocalendar',
        user='root',
        password='1111'
    )
#Функция для отправки главного меню
def send_main_menu(chat_id):
    # Создаем клавиатуру
    markup = types.InlineKeyboardMarkup()

    # Создаем кнопки
    btn1 = types.InlineKeyboardButton(text='Регистрация', callback_data='register')
    btn2 = types.InlineKeyboardButton(text='Авторизация', callback_data='login')
    btn3 = types.InlineKeyboardButton(text='Изменить пароль', callback_data='change_password')

    # Добавляем кнопки в клавиатуру
    markup.add(btn1, btn2, btn3)

    # Отправляем сообщение с кнопками
    bot.send_message(chat_id,
                     "Приветствуем в нашем боте для записи на ноготочки!\n"
                     "Это учебный бот для дипломной работы. Будет удален после защиты.\n"
                     "Не в коем случае не указывайте реальные персональные данные!",
                     reply_markup=markup)




#Вот это функции необходимые для работы обработчика кнопок авторизации:
#Выполняется, если в меню получен callback change password
def change_password(message, user_id):
    new_password = message.text
    try:
        if not new_password:
            bot.send_message(
                chat_id=user_id,
                text="Пароль не введен. Попробуйте снова."
            )
            return send_main_menu(user_id)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT login FROM clients WHERE login = %s",(user_id,)
            )
            result = cursor.fetchone()

            if result:
                update_password(new_password, user_id)

            else:
                bot.send_message(
                    chat_id=user_id,
                    text="Пользователь не найден. Попробуйте снова или выберите 'Регистрация'."
                )
                return send_main_menu(user_id)

    except Exception as e:
        print(f"Ошибка при работе с БД: {e}")
        bot.send_message(
            chat_id=user_id,
            text="Произошла ошибка при обработке запроса"
        )
        return send_main_menu(user_id)

#Обновление пароля
def update_password(new_password, user_id):  # Изменен параметр на логин
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE clients SET password = %s WHERE login = %s", (new_password, user_id))
        conn.commit()

        bot.send_message(
            chat_id=user_id,
            text='Пароль успешно обновлен'
        )
        return send_main_menu(user_id)

    except Exception as e:
        print(f"Ошибка при обновлении пароля: {e}")
        bot.send_message(
            chat_id=user_id,
            text='Произошла ошибка при обновлении пароля'
        )
        return send_main_menu(user_id)

# Функция для регистрации нового пользователя
def registration(callback, cursor, user_id):
    try:
        cursor.execute("SELECT login FROM clients WHERE login = %s", (user_id,))
        user = cursor.fetchone()

        if user:
            bot.edit_message_text('Пользователь с таким логином уже зарегистрирован',
                                  callback.message.chat.id,
                                  callback.message.message_id)
            send_main_menu(callback.message.chat.id)
        else:
            # Создаем клавиатуру
            markup = types.InlineKeyboardMarkup()

            # Создаем кнопки
            btn1 = types.InlineKeyboardButton(text='Отмена', callback_data='undo')

            # Добавляем кнопки в клавиатуру
            markup.add(btn1)

            bot.edit_message_text('Введите ваши ФИО:',
                                  callback.message.chat.id,
                                  callback.message.message_id,
                                  reply_markup=markup)

            # Регистрируем следующий шаг
            bot.register_next_step_handler(callback.message,
                                           get_fio,
                                           user_id=user_id)

    except Exception as e:
        bot.edit_message_text(f'Ошибка: {str(e)}',
                              callback.message.chat.id,
                              callback.message.message_id)

# Функция для получения ФИО
def get_fio(message, user_id):
    try:
        # Создаем клавиатуру
        markup = types.InlineKeyboardMarkup()

        # Создаем кнопки
        btn1 = types.InlineKeyboardButton(text='Отмена', callback_data='undo')

        # Добавляем кнопки в клавиатуру
        markup.add(btn1)

        fio = message.text
        bot.send_message(message.chat.id, 'Введите ваш номер телефона:',
                                  reply_markup=markup)

        # Регистрируем следующий шаг
        bot.register_next_step_handler(message,
                                       get_phone,
                                       user_id=user_id,
                                       fio=fio)

    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка: {str(e)}')

# Функция для получения номера телефона
def get_phone(message, user_id, fio):
    try:
        # Создаем клавиатуру
        markup = types.InlineKeyboardMarkup()

        # Создаем кнопки
        btn1 = types.InlineKeyboardButton(text='Отмена', callback_data='undo')

        # Добавляем кнопки в клавиатуру
        markup.add(btn1)

        phone = message.text
        bot.send_message(message.chat.id, 'Введите пароль:',
                                  reply_markup=markup)

        # Регистрируем следующий шаг
        bot.register_next_step_handler(message,
                                       save_registration,
                                       user_id=user_id,
                                       fio=fio,
                                       phone=phone)


    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка: {str(e)}')

# Функция для сохранения данных регистрации
def save_registration(message, user_id, fio, phone):
    # Устанавливаем соединение с БД
    conn = get_connection()
    cursor = conn.cursor()

    try:
        password = message.text

        # Проверяем активность соединения
        if not conn.is_connected():
            conn.ping(reconnect=True)

        cursor.execute("INSERT INTO clients (Login, FIO, Password, PhoneNumber) VALUES (%s, %s, %s, %s)",
                       (user_id, fio, password, phone))
        conn.commit()

        bot.send_message(message.chat.id, 'Регистрация успешно завершена!')

    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при регистрации: {str(e)}')
        conn.rollback()

    finally:
        cursor.close()
        conn.close()
        send_main_menu(message.chat.id)

#Функция авторизации
def process_password(message, user_id):
    input_password = message.text
    try:
        if not input_password:
            bot.send_message(
                chat_id=user_id,
                text="Пароль не введен. Попробуйте снова."
            )
            return send_main_menu(user_id)

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT Password FROM clients WHERE login = %s",
                (user_id,)
            )
            result = cursor.fetchone()

            if result:
                db_password = result[0]

                if input_password == db_password:
                    bot.send_message(
                        chat_id=user_id,
                        text=f"Успешная авторизация!\nВаш ID: {user_id}"
                    )
                    return auto_menu(user_id)
                else:
                    bot.send_message(
                        chat_id=user_id,
                        text="Неверный пароль. Попробуйте снова или выберите 'Сменить пароль'."
                    )
                    return send_main_menu(user_id)
            else:
                bot.send_message(
                    chat_id=user_id,
                    text="Пользователь не найден. Попробуйте снова или выберите 'Сменить пароль'."
                )
                return send_main_menu(user_id)

    except Exception as e:
        print(f"Ошибка при работе с БД: {e}")
        bot.send_message(
            chat_id=user_id,
            text="Произошла ошибка при обработке запроса"
        )
        return send_main_menu(user_id)

#Обработчик команды start вызывает главное меню
@bot.message_handler(commands=['start'])
def start(message):
    send_main_menu(message.chat.id)

# Обработчик callback главного меню
@bot.callback_query_handler(func=lambda call: call.data in ['register', 'login','change_password','undo'])
def callback_message(callback):
    user_id = callback.message.chat.id
    conn = get_connection()
    cursor = conn.cursor()

    # Создаем клавиатуру
    markup = types.InlineKeyboardMarkup()

    # Создаем кнопки
    btn1 = types.InlineKeyboardButton(text='Отмена', callback_data='undo')

    # Добавляем кнопки в клавиатуру
    markup.add(btn1)

    try:
        if callback.data == 'register':
            registration(callback, cursor, user_id)

        elif callback.data == 'login':

            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Введите ваш пароль:',
                reply_to_message_id=callback.message.message_id,
                reply_markup=markup
            )
            bot.register_next_step_handler(callback.message, process_password, user_id=user_id)

        elif callback.data == 'change_password':
            bot.send_message(
                chat_id=callback.message.chat.id,
                text='Введите новый пароль:',
                reply_to_message_id=callback.message.message_id,
                reply_markup=markup
            )
            bot.register_next_step_handler(callback.message, change_password, user_id=user_id)

        elif callback.data == 'undo':
            send_main_menu(callback.message.chat.id)
        else:
            bot.edit_message_text(
                'Неизвестная команда',
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id
            )

    except Exception as e:
        print(f"Ошибка при работе с БД: {e}")
        bot.edit_message_text(
            'Произошла ошибка при обработке запроса',
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id
        )

    finally:
        cursor.close()
        conn.close()




#Вот это функции необходимые для работы обработчика кнопок авторизированных пользователей:
# Функция для отправки меню для авторизовавшихся пользователей
def auto_menu(chat_id):
    # Создаем клавиатуру
    markup = types.InlineKeyboardMarkup()

    # Создаем кнопки
    btn1 = types.InlineKeyboardButton(text='Записаться', callback_data='appointment')
    btn2 = types.InlineKeyboardButton(text='Проверить записи', callback_data='check_appointments')
    btn3 = types.InlineKeyboardButton(text='Отменить запись', callback_data='cancel_appointment')

    # Добавляем кнопки в клавиатуру
    markup.add(btn1, btn2, btn3)

    # Отправляем сообщение с кнопками
    bot.send_message(chat_id,
                     "Выберите действие:\n"
                     "\n"
                     "💄 Записаться на процедуру\n"
                     "📅 Проверить свои записи\n"
                     "❌ Отменить запись\n"
                     "\n"
                     "Для вашего удобства все услуги доступны 24/7",
                     reply_markup=markup,
                     parse_mode='Markdown')

# Обработчик callback авторизованных пользователей
# Создаем словарь для хранения данных
user_data = {}

# Обработчик меню для авторизованных
@bot.callback_query_handler(func=lambda call: call.data in ['appointment', 'check_appointments', 'cancel_appointment'])
def callback_message(callback):
    user_id = callback.message.chat.id

    try:
        if callback.data == 'appointment':
            keyboard = M_key.get_service_list()
            bot.send_message(
                chat_id=user_id,
                text="Выберите услугу:",
                reply_markup=keyboard
            )
        elif callback.data == 'check_appointments':
            text = A_key.get_appointments_list(user_id)
            bot.send_message(
                chat_id=user_id,
                text=text
            )

            return auto_menu(user_id)

        elif callback.data == 'cancel_appointment':
            keyboard = A_key.get_booking_id(user_id)

            # Проверяем, что вернула функция
            if isinstance(keyboard, str):
                bot.send_message(
                    chat_id=user_id,
                    text=keyboard  # Если нет записей, отправляем сообщение
                )

                return auto_menu(user_id)
            else:
                bot.send_message(
                    chat_id=user_id,
                    text="Выберите запись для отмены:",
                    reply_markup=keyboard
                )

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        bot.send_message(
            chat_id=user_id,
            text="Произошла ошибка при получении данных"
        )

#Обработчик нажатия на клавиатуру с удалением записи
@bot.callback_query_handler(func=lambda call: call.data.startswith('select_appointment_'))
def select_appointment(call):
    # Извлекаем ID записи из callback_data
    id_booking = int(call.data.split('_')[-1])

    try:
        result = A_key.delete_booking(id_booking)

        if result:
            bot.send_message(
                chat_id=call.message.chat.id,
                text="Запись успешно удалена"
            )
        else:
            bot.send_message(
                chat_id=call.message.chat.id,
                text="Ошибка при удалении записи"
            )

    except ValueError:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Произошла ошибка при удалении записи"
        )

    return auto_menu(call.message.chat.id)

#Обработчик нажатия на клавиатуру с услугами
@bot.callback_query_handler(func=lambda call: call.data.startswith('select_service_'))
def select_service(call):
    # Извлекаем ID мастера из callback_data
    service_id = int(call.data.split('_')[-1])

    # Сохраняем service_id в словарь
    user_data.setdefault(call.message.chat.id, {})
    user_data[call.message.chat.id]['service_id'] = service_id

    # Получаем свободные слоты для выбранного мастера
    keyboard = M_key.get_masters_list()

    # Отправляем сообщение с датами
    bot.send_message(
        chat_id=call.message.chat.id,
        text="Выберите мастера:",
        reply_markup=keyboard
    )

    # Подтверждаем выбор мастера
    bot.answer_callback_query(call.id, f"Выбрана услуга с ID: {service_id}")

#Обработчик нажатия на клавиатуру с мастерами
@bot.callback_query_handler(func=lambda call: call.data.startswith('select_master_'))
def select_master(call):
    # Извлекаем ID мастера из callback_data
    master_id = int(call.data.split('_')[-1])

    # Сохраняем master_id в словарь
    user_data.setdefault(call.message.chat.id, {})
    user_data[call.message.chat.id]['master_id'] = master_id

    # Получаем свободные слоты для выбранного мастера
    keyboard = M_key.get_free_slots(master_id)

    if keyboard is False:  # Проверяем, если слотов нет
        masters_keyboard = M_key.get_masters_list()
        bot.send_message(
            chat_id=call.message.chat.id,
            text="У мастера нет доступных слотов для записи, выберите другого мастера. Выберите другого мастера:",
            reply_markup=masters_keyboard
        )
    else:
        # Отправляем сообщение с датами
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Выберите дату:",
            reply_markup=keyboard
        )

    # Подтверждаем выбор мастера
    bot.answer_callback_query(call.id, f"Выбран мастер с ID: {master_id}")

#Обработчик нажатия на клавиатуру с датами
@bot.callback_query_handler(func=lambda call: call.data.startswith('select_date_'))
def select_date(call):
    # Извлекаем дату из callback_data
    date_str = call.data.split('_')[-1]

    # Получаем ID мастера из текущего сообщения
    master_id = user_data.get(call.message.chat.id, {}).get('master_id')

    # Получаем свободные слоты для выбранного мастера
    keyboard = M_key.get_free_hours(date_str, master_id)

    # Отправляем сообщение с временем
    bot.send_message(
        chat_id=call.message.chat.id,
        text="Выберите час:",
        reply_markup=keyboard
    )

    # Отправляем подтверждение
    bot.answer_callback_query(call.id, f"Выбрана дата: {date_str}")

#Обработчик записи
@bot.callback_query_handler(func=lambda call: call.data.startswith('select_time_'))
def select_time(call):
    # Извлекаем ID записи из callback_data
    schedule_id = int(call.data.split('_')[-1])

    # Получаем ID услуги из словаря
    service_id = user_data.get(call.message.chat.id, {}).get('service_id')

    # Получаем ID клиента
    id_client = M_key.get_client_id(call.message.chat.id)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Bookings (id_client, id_schedule, id_service)
            VALUES (%s, %s, %s)
        ''', (id_client, schedule_id, service_id))
        conn.commit()

    bot.answer_callback_query(call.id, "Запись успешно создана")
    bot.send_message(
        chat_id=call.message.chat.id,
        text="Ваша запись успешно создана!")

    return auto_menu(call.message.chat.id)

bot.polling(none_stop=True)



