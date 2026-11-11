# Day_2 — Автотесты для Задачи №1 «Проверка пароля»

Юнит-тесты на `unittest` для функции `check_password()` из решения
[Day_1/Задача №1](../Day_1) (`strong_password_Buldakova.py`).

## Содержимое папки

| Файл | Описание |
|---|---|
| `strong_password_Buldakova.py` | Тестируемое решение (копия из Day_1) |
| `strong_password_Buldakova_test.py` | Автотесты функции `check_password()` |
| `run_tests.py` | Runner: запускает все `*_test.py` из папки |

## Что проверяют тесты

Функция `check_password(password) -> tuple[bool, str]` возвращает
`(True, 'пароль подходит')` или `(False, пояснение)`.

| Тест | Что проверяет |
|---|---|
| `test_returns_tuple` | Функция возвращает кортеж из двух элементов |
| `test_valid_password` | Правильный пароль из условия проходит |
| `test_valid_password_from_task_example` | Второй правильный пример (`aaaAAA111!!!`) проходит |
| `test_invalid_password_from_task_example` | Пример `saucacAusacu8` отклоняется |
| `test_digits` | Пароль без цифр отклоняется |
| `test_lowercase` | Пароль без строчных букв отклоняется |
| `test_uppercase` | Пароль без прописных букв отклоняется |
| `test_special` | Пароль без спецсимволов отклоняется |
| `test_missing_sets_combinations` | Сочетания отсутствующих наборов символов |
| `test_length_min` | Граница длины: 8 символов проходит, 7 — нет |
| `test_length_max` | Граница длины: 15 символов проходит, 16 — нет |
| `test_length_empty` | Пустая строка отклоняется |
| `test_forbidden_symbols` | Кириллица, пробел и другие запрещённые символы отклоняются |
| `test_all_special_chars_allowed` | Каждый спецсимвол из набора `_!@#$%^&` разрешён |
| `test_not_a_string` | Не-строка (число, None, список) отклоняется без исключения |

В тестах `test_missing_sets_combinations`, `test_forbidden_symbols`,
`test_all_special_chars_allowed` и `test_not_a_string` используется
`self.subTest()` — при падении одного из вариантов в выводе будет
показано, какая именно комбинация не прошла.

## Требования

- Python 3.10+ (тесты написаны с аннотацией `tuple[bool, str]`);
- стандартная библиотека `unittest` — ничего устанавливать не нужно.

## Запуск тестов

Все команды выполняются из папки `Day_2/Solutions`:

```bash
cd Day_2/Solutions
```

### Способ 1 — через unittest напрямую

```bash
python -m unittest strong_password_Buldakova_test -v
```

Флаг `-v` включает подробный вывод с именами всех 15 тестов.

### Способ 2 — через runner

```bash
python run_tests.py
```

Runner сам найдёт все файлы `*_test.py` в папке и запустит их.
Возвращает код ошибки 1, если хоть один тест упал.

### Способ 3 — автодискавери unittest

```bash
python -m unittest discover
```

`unittest` ищет файлы по маске `test*.py` в текущей папке.

### Способ 4 — из интерфейса VS Code

1. Установите расширение **Python** (`ms-python.python`).
2. Откройте файл `strong_password_Buldakova_test.py`.
3. Над каждым тестом появится ссылка **Run Test** — клик запускает один тест.
4. Панель **Testing** (иконка колбы слева) показывает дерево всех тестов
   с зелёными/красными отметками.

## Ожидаемый результат

При успешном прогоне:

```
Ran 15 tests in 0.001s

OK
```

## Структура теста (пример)

```python
def test_digits(self):
    """Пароль без цифр не проходит, в сообщении указана причина."""
    ok, reasons = check_password('aaaAAA!@#')
    self.assertFalse(ok)
    self.assertIn('цифру', reasons)
```

- `assertFalse(ok)` — проверяем, что пароль отклонён;
- `assertIn('цифру', reasons)` — проверяем, что в пояснении
  названа причина отказа;
- docstring на русском показывается в выводе при запуске с `-v`.
