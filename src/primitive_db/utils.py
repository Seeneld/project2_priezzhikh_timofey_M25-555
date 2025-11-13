import json
from typing import Any, Dict, List

"""
Загрузка метаданных из JSON файла
"""
def load_metadata(filepath: str) -> Dict[str, Any]:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

"""
Сохранение метаданных в JSON файл
"""
def save_metadata(filepath: str, data: Dict[str, Any]):
    if data is None:
        data = {}
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

"""
Загрузка данных таблиц из папки data/
"""
def load_table_data(table_name: str) -> List[Dict[str, Any]]:
    filepath = f"data/{table_name}.json"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

"""
Сохранение данных таблиц в папку data/
"""
def save_table_data(table_name: str, data: List[Dict[str, Any]]) -> None:
    filepath = f"data/{table_name}.json"
    if data is None:
        data = {}
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)