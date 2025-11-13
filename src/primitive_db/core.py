from typing import Any, Dict, List, Optional, Tuple

from prettytable import PrettyTable

from src.primitive_db.constants import SUPPORTED_TYPES
from src.primitive_db.decorators import confirm_action, handle_db_errors, log_time
from src.primitive_db.utils import load_table_data

"""
Валидация данных в колонке таблицы
"""
def validate_column_spec(
        column: str
        
        ) -> Tuple[str, str]:
    if ':' not in column:
        raise ValueError(f"Некорректное значение: {column}. \
                         Ожидается формат 'имя:тип'.")
    name, typ = column.split(':', 1)
    if not name:
        raise ValueError(f"Некорректное значение: {column}. \
                         Имя столбца не может быть пустым.")
    if typ not in SUPPORTED_TYPES:
        raise ValueError(f"Некорректное значение: {typ}. \
                         Поддерживаемые типы: {', '.join(SUPPORTED_TYPES)}")
    return name, typ

"""
Создание таблицы в метаданных
"""
@handle_db_errors
def create_table(
    metadata: Dict[str, List[str]], 
    table_name: str, 
    column_specs: List[str]
) -> Dict[str, List[str]]:
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    columns = ["ID:int"]
    for spec in column_specs:
        name, typ = validate_column_spec(spec)
        columns.append(f"{name}:{typ}")

    new_metadata = metadata.copy()
    new_metadata[table_name] = columns
    print(f'Таблица "{table_name}" успешно создана со столбцами:\
           {", ".join(columns)}')
    return new_metadata

"""
Удаление таблицы из метаданных
"""
@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata:
                Dict[str, List[str]], 
                table_name: str
                ) -> Dict[str, List[str]]:
    if table_name not in metadata:
        raise KeyError(table_name)

    new_metadata = metadata.copy()
    del new_metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return new_metadata

"""
Вывод списка таблиц
"""
@handle_db_errors
def list_tables(metadata: Dict[str, List[str]]) -> None:
    if not metadata:
        print("Нет таблиц.")
    else:
        for table in metadata:
            print(f"- {table}")

"""
Преобразование строки в значение нужного типа.
"""
def cast_value(value_str: str, target_type: str) -> Any:
    value_str = value_str.strip()
    if target_type == "int":
        return int(value_str)
    elif target_type == "bool":
        if value_str.lower() in ("true", "1"):
            return True
        elif value_str.lower() in ("false", "0"):
            return False
        else:
            raise ValueError(f"Некорректное булево значение\
                             : {value_str}")
    elif target_type == "str":
            return value_str
    else:
        raise ValueError(f"Неизвестный тип: {target_type}")

"""
Валидация и приведение значения к нужному типу
"""
def validate_and_cast_values(schema: List[str],
                              values: List[str]) -> Dict[str, Any]:
    data_columns = schema[1:] 
    if len(values) != len(data_columns):
        raise ValueError(f"Ожидалось {len(data_columns)}\
                          значений, получено {len(values)}.")

    record = {}
    for spec, val_str in zip(data_columns, values):
        col_name, col_type = spec.split(":", 1)
        record[col_name] = cast_value(val_str, col_type)
    return record

"""
Добавление записи в таблицу
"""
@handle_db_errors
@log_time
def insert(
    metadata: Dict[str, List[str]], 
    table_name: str, 
    values: List[str]
) -> Optional[List[Dict[str, Any]]]:
    if table_name not in metadata:
        raise KeyError(table_name)

    schema = metadata[table_name]
    record_data = validate_and_cast_values(schema, values)

    table_data = load_table_data(table_name)
    new_id = max((row.get("ID", 0) for row in table_data),
                  default=0) + 1
    record = {"ID": new_id, **record_data}
    table_data.append(record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


"""
Вывод записи таблицы
"""
@handle_db_errors
@log_time
def select(
    metadata: Dict[str, List[str]], 
    table_name: str, 
    where_clause: Optional[Dict[str, Any]] = None
) -> None:
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    table_data = load_table_data(table_name)
    schema = metadata[table_name]
    columns = [spec.split(":", 1)[0] for spec in schema]

    if where_clause:
        filtered = []
        for row in table_data:
            match = True
            for col, val in where_clause.items():
                if str(row.get(col, "")) != str(val):
                    match = False
                    break
            if match:
                filtered.append(row)
        table_data = filtered

    if not table_data:
        print("Нет записей.")
        return

    pt = PrettyTable()
    pt.field_names = columns
    for row in table_data:
        pt.add_row([row.get(col, "") for col in columns])
    print(pt)


"""
Обновление записи по условию
"""
@handle_db_errors
def update(
    metadata: Dict[str, List[str]], 
    table_name: str, 
    set_clause: Dict[str, str], 
    where_clause: Dict[str, Any]
) -> Optional[List[Dict[str, Any]]]:
    if table_name not in metadata:
        raise KeyError(table_name)

    table_data = load_table_data(table_name)
    schema_dict = {
        spec.split(":", 1)[0]: spec.split(":", 1)[1]
        for spec in metadata[table_name]
    }

    validated_set = {}
    for col, val_str in set_clause.items():
        if col not in schema_dict:
            raise KeyError(col)
        validated_set[col] = cast_value(val_str, schema_dict[col])

    updated = False
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if str(row.get(col, "")) != str(val):
                match = False
                break
        if match:
            for col, new_val in validated_set.items():
                row[col] = new_val
            updated = True
            print(f'Запись с ID={row["ID"]} в таблице\
                   "{table_name}" успешно обновлена.')

    if not updated:
        print("Ни одна запись не соответствует условию.")

    return table_data if updated else None


"""
Удаление записи по условию
"""
@handle_db_errors
@confirm_action("удаление записи")
def delete(
    metadata: Dict[str, List[str]], 
    table_name: str, 
    where_clause: Dict[str, Any]
) -> Optional[List[Dict[str, Any]]]:
    if table_name not in metadata:
        raise KeyError(table_name)

    table_data = load_table_data(table_name)
    new_table_data = []
    deleted = False

    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if str(row.get(col, "")) != str(val):
                match = False
                break
        if match:
            deleted = True
            print(f'Запись с ID={row["ID"]} \
                  успешно удалена из таблицы "{table_name}".')
        else:
            new_table_data.append(row)

    if not deleted:
        print("Ни одна запись не соответствует условию.")

    return new_table_data if deleted else None


"""
Вывод информации о таблице
"""
@handle_db_errors
def info(metadata: Dict[str, List[str]], table_name: str) -> None:
    if table_name not in metadata:
        raise KeyError(table_name)

    schema = metadata[table_name]
    table_data = load_table_data(table_name)
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {', '.join(schema)}")
    print(f"Количество записей: {len(table_data)}")