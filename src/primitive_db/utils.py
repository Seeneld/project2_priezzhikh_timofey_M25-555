import json
from typing import Any, Dict

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
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)