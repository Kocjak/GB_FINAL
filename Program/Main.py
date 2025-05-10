import Modules.Download
import Modules.initialization
import Modules.Masters
import Modules.services
import Modules.Shedule

#Функция главного меню
def show_menu():
    while True:
        # Форматируем меню с помощью f-strings и разделителей
        print("\n" + "*"*30)
        print("| ГЛАВНОЕ МЕНЮ АВТОКАЛЕНДАРЯ |")
        print("*"*30)
        print("""
Доступные действия:

1. 🔧 Установка и настройка MySQL
2. 🔧 Настройка службы MySQL и настройка БД
3. ✏️ Редактирование таблицы мастеров
4. ✏️ Редактирование таблицы услуг
5. ✏️ Редактирование графика работы
6. 🚪 Выйти
        """)
        # Добавляем подсказку и валидацию ввода
        try:
            choice = int(input("Введите номер действия: "))
            if 1 <= choice <= 6:
                if choice == 1:
                    Modules.Download.show_menu()
                elif choice == 2:
                    Modules.initialization.show_menu()
                elif choice == 3:
                    Modules.Masters.show_menu()
                elif choice == 4:
                    Modules.services.show_menu()
                elif choice == 5:
                    Modules.Shedule.show_menu()
                elif choice == 6:
                    print("\nДо свидания! 👋")
                    break
            else:
                print("\n❌ Неверный выбор, введите число от 1 до 6")
        except ValueError:
            print("\n❌ Пожалуйста, введите число")

if __name__ == "__main__":
    show_menu()