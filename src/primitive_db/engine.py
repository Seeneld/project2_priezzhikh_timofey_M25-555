import shlex
from src.primitive_db import core, utils
from typing import Dict

DB_FILE = "db_meta.json"

"""
Приветственное сообщение (старая версия)
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
    
    print("\nРабота с записями:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию")
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

"""
Парсинг строки вида 'age = 28'.
Возвращает словарь вида {'age': '28'}.
"""
def parse_where_or_set(clause: str) -> Dict[str, str]:
    clause = clause.strip()
    if ' = ' not in clause:
        raise ValueError(f"Некорректный формат условия: {clause}. Ожидается 'ключ = значение'.")

    key, value = clause.split(' = ', 1)
    key = key.strip()
    value = value.strip()

    if not key:
        raise ValueError(f"Ключ не может быть пустым в: {clause}")

    if not key.replace('_', '').isalnum():
        raise ValueError(f"Некорректное имя столбца: {key}")

    return {key: value}

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

        elif command == "insert":
            if len(args) < 4 or args[1] != "into" or args[3] != "values":
                print("Некорректный синтаксис: insert into <таблица> values (значения...)")
            else:
                table_name = args[2]
                values_str = " ".join(args[4:])
                if values_str.startswith("(") and values_str.endswith(")"):
                    values_str = values_str[1:-1].strip()
                    if values_str == "":
                        values = []
                    else:
                        values = [v.strip() for v in values_str.split(",")]
                else:
                    print("Ожидались значения в скобках: (val1, val2, ...)")
                    continue

                new_data = core.insert(metadata, table_name, values)
                if new_data is not None:
                    utils.save_table_data(table_name, new_data)

        elif command == "select":
            if len(args) < 3 or args[1] != "from":
                print("Некорректный синтаксис: select from <таблица> [where ...]")
            else:
                table_name = args[2]
                where_clause = None
                if len(args) >= 5 and args[3] == "where":
                    where_str = " ".join(args[4:])
                    try:
                        where_clause = parse_where_or_set(where_str)
                    except ValueError as e:
                        print(e)
                        continue

                core.select(metadata, table_name, where_clause)

        elif command == "update":
            if len(args) < 4 or args[2] != "set":
                print("Некорректный синтаксис: update <таблица> set col=val [where ...]")
            else:
                table_name = args[1]
                set_part = []
                where_part = []
                in_set = True
                for arg in args[3:]:
                    if arg == "where":
                        in_set = False
                        continue
                    if in_set:
                        set_part.append(arg)
                    else:
                        where_part.append(arg)

                if not set_part:
                    print("Нет данных для обновления.")
                    continue

                set_str = " ".join(set_part)
                try:
                    set_dict = parse_where_or_set(set_str)
                except ValueError as e:
                    print(e)
                    continue

                if not where_part:
                    print("Условие 'where' обязательно для update.")
                    continue

                where_str = " ".join(where_part)
                try:
                    where_dict = parse_where_or_set(where_str)
                except ValueError as e:
                    print(e)
                    continue

                new_data = core.update(metadata, table_name, set_dict, where_dict)
                if new_data is not None:
                    utils.save_table_data(table_name, new_data)

        elif command == "delete":
            if len(args) < 4 or args[1] != "from" or args[3] != "where":
                print("Некорректный синтаксис: delete from <таблица> where ...")
            else:
                table_name = args[2]
                where_str = " ".join(args[4:])
                try:
                    where_dict = parse_where_or_set(where_str)
                except ValueError as e:
                    print(e)
                    continue

                new_data = core.delete(metadata, table_name, where_dict)
                if new_data is not None:
                    utils.save_table_data(table_name, new_data)

        elif command == "info":
            if len(args) != 2:
                print("Некорректный синтаксис: info <таблица>")
            else:
                table_name = args[1]
                core.info(metadata, table_name)

        else:
            print(f"Команды {command} нет. Попробуйте снова.")