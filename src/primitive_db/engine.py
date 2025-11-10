import shlex
from src.primitive_db import core, utils

DB_FILE = "db_meta.json"

"""
Приветственное сообщение
"""
def welcome():
    while True:
        print('<command> exit - выйти из программы')
        print('<command> help - справочная информация')
        command = input('Введите команду: ')

        if command == 'exit':
            break

        elif command == 'help':
            continue
        
        else:
            print(f"Неизвестная команда: {command}")

"""
Вывод справки
"""
def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

"""
Основная функция
"""
def run():
    print("***База данных***")
    print_help()

    while True:
        try:
            user_input = input(">>>Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError as e:
            print(f"Ошибка парсинга: {e}. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]
        metadata = utils.load_metadata(DB_FILE)

        if command == "exit":
            break
        elif command == "help":
            print_help()
            continue
        elif command == "list_tables":
            core.list_tables(metadata)
        elif command == "create_table":
            if len(args) < 2:
                print("Некорректное значение: недостаточно аргументов для команды create_table.")
            else:
                table_name = args[1]
                column_specs = args[2:]
                new_meta = core.create_table(metadata, table_name, column_specs)
                utils.save_metadata(DB_FILE, new_meta)

        elif command == "drop_table":
            if len(args) != 2:
                print("Некорректное значение: команда drop_table требует ровно одно имя таблицы.")
            else:
                table_name = args[1]
                new_meta = core.drop_table(metadata, table_name)
                utils.save_metadata(DB_FILE, new_meta)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")