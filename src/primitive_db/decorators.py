import time
from typing import Callable

import prompt

"""
Обработка ошибок
"""
def handle_db_errors(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. \
                  Возможно, база данных не инициализирована.")
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
        except UnboundLocalError as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper

"""
Подтверждение действия
"""
def confirm_action(action_name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            answer = prompt.string(f'Вы уверены,\
                                    что хотите выполнить "{action_name}"? [y/n]: ')
            if answer.lower() == 'y':
                return func(*args, **kwargs)
            else:
                print("Операция отменена.")
        return wrapper
    return decorator

"""
Логирование времени выполнения
"""
def log_time(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(f'Функция {func.__name__} выполнилась за {end - start:.5f} секунд.')
        return result
    return wrapper