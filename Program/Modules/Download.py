import wget
import os, sys
import subprocess

def downmysql():
    url = 'https://dev.mysql.com/get/Downloads/MySQL-9.3/mysql-9.3.0-winx64.msi'
    file_Path = 'Modules/mysql.msi'

    if os.path.exists(file_Path):
        print('Установщик Mysql уже загружен, загружать не требуется!')
    else:
        print('Начинаем загрузку mysql.msi')
        wget.download(url, file_Path, bar=bar_progress)
        print('downloaded')

def bar_progress(current, total, width=80):
    progress_message = "Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total)
    sys.stdout.write("\r" + progress_message)
    sys.stdout.flush()

def installmysql():
    msi_location = 'Modules/mysql.msi'
    # Проверяем существование файла перед установкой
    if not os.path.exists(msi_location):
        print("Ошибка: файл установщика MySQL не найден! Сначала загрузите его.")
        return show_menu()

    try:
        # Выводим инструкцию
        show_instruction()
        # Запускаем установку
        result = subprocess.run(['msiexec', '/i', msi_location], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print("MySQL установлен успешно!")
        else:
            print(f"Ошибка установки MySQL: {result.stderr}")

    except Exception as e:
        print(f"Произошла ошибка при установке: {str(e)}")
        sys.exit(1)

def show_instruction():
    file_name = 'Modules\Инструкция MySQL.md'
    # Получаем текущий путь
    file_path = os.getcwd()
    # Формируем полный путь к файлу
    full_path = os.path.join(file_path, file_name)
    # Проверяем существование файла
    if os.path.exists(full_path):
        try:
            # Открываем файл и читаем его содержимое
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
                print("\nИнструкция:\n" + content)
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
    else:
        print(f"Файл {full_path} не найден.")

def show_menu():
    while True:
        # Форматируем меню с помощью f-strings и разделителей
        print("\n" + "*"*24)
        print("| МЕНЮ УСТАНОВКИ MYSQL |")
        print("*"*24)
        print("""
Доступные действия:

1. 💿 Скачать MySQL
2. 🔧 Установить MySQL
3. 📘 Инструкция установки MySQL
4. 🚪 Вернуться в главное меню
        """)

        # Добавляем подсказку и валидацию ввода
        try:
            choice = int(input("Введите номер действия: "))
            if 1 <= choice <= 4:
                if choice == 1:
                    downmysql()
                elif choice == 2:
                    installmysql()
                elif choice == 3:
                    show_instruction()
                elif choice == 4:
                    print("\nДо свидания! 👋")
                    break
            else:
                print("\n❌ Неверный выбор, введите число от 1 до 4")
        except ValueError:
            print("\n❌ Пожалуйста, введите число")

if __name__ == "__main__":
    show_menu()










