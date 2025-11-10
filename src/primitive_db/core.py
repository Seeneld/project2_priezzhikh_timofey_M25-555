from typing import Dict, List, Tuple


SUPPORTED_TYPES = {"int", "str", "bool"}
DB_FILE = "db_meta.json"

"""
Валидация данных в колонке таблицы
"""
def validate_column_spec(column: str) -> Tuple[str, str]:
    if ':' not in column:
        raise ValueError(f"Некорректное значение: {column}. Ожидается формат 'имя:тип'.")
    name, typ = column.split(':', 1)
    if not name:
        raise ValueError(f"Некорректное значение: {column}. Имя столбца не может быть пустым.")
    if typ not in SUPPORTED_TYPES:
        raise ValueError(f"Некорректное значение: {typ}. Поддерживаемые типы: {', '.join(SUPPORTED_TYPES)}")
    return name, typ

"""
Создание таблицы в метаданных
"""
def create_table(metadata: Dict[str, List[str]], table_name: str, column_specs: List[str]) -> Dict[str, List[str]]:
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    columns = ["ID:int"]
    for spec in column_specs:
        try:
            name, typ = validate_column_spec(spec)
            columns.append(f"{name}:{typ}")
        except ValueError as e:
            print(e)
            return metadata

    new_metadata = metadata.copy()
    new_metadata[table_name] = columns
    print(f'Таблица "{table_name}" успешно создана со столбцами: {", ".join(columns)}')
    return new_metadata

"""
Удаление таблицы из метаданных
"""
def drop_table(metadata: Dict[str, List[str]], table_name: str) -> Dict[str, List[str]]:
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    new_metadata = metadata.copy()
    del new_metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return new_metadata

"""
Вывод списка таблиц
"""
def list_tables(metadata: Dict[str, List[str]]):
    if not metadata:
        print("Нет таблиц.")
    else:
        for table in metadata:
            print(f"- {table}")