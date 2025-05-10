import os
from pathlib import Path

def path_downloads():
    current_path = os.getcwd()
    path_parts = current_path.split(os.sep)
    program_index = path_parts.index('Program')

    if len(path_parts) == program_index + 1:
        new_path = os.path.join(current_path, 'Downloads')
    else:
        new_path = os.path.join(*path_parts[:program_index + 1], 'Downloads')

    # Исправляем путь, добавляя разделитель после буквы диска
    drive, tail = os.path.splitdrive(str(new_path))
    if drive and not tail.startswith(os.sep):
        new_path = Path(drive + os.sep + tail)
    return Path(new_path)

if __name__ == "__main__":
    new_path = path_downloads()  # Сохраняем результат функции
    if new_path:
        print(new_path)

