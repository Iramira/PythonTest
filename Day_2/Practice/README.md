# Day_2 / Practice — encode / decode

Задача №1: шифр, в котором каждый символ закодирован двумя цифрами.
Отсчёт с `00 -> 'a'`, `01 -> 'b'` ... `25 -> 'z'`, `26 -> ' '` (пробел).

Пример из условия: `'070411111426152419071413' <-> 'hello python'`.

## Содержимое

| Файл | Описание |
|---|---|
| `encode_decode.py` | Решение: функции `encode()`, `decode()`, демо в `main()` |
| `encode_decode_test.py` | 13 автотестов на `unittest` (корректные и некорректные данные) |

## Как работает

- `encode(text)` — текст -> строка цифр; каждая буква заменяется её номером
  в алфавите (`'h' -> '07'`), пробел -> `'26'`;
- `decode(cipher)` — обратное преобразование: строка цифр -> текст;
- некорректные входные данные не «роняют» программу: обе функции
  поднимают `ValueError` с понятным пояснением
  (нечётная длина, не-цифры, код больше 26, заглавные буквы и т.п.).

## Запуск

Из папки `Day_2/Practice`:

```bash
python encode_decode.py          # демо: шифровка и расшифровка 'hello python'
python -m unittest encode_decode_test -v   # тесты
```

Ожидаемый вывод тестов: `Ran 13 tests ... OK`.

## Тесты

| Тест | Что проверяет |
|---|---|
| `test_decode_example_from_task` | Пример из условия декодируется в `'hello python'` |
| `test_encode_example_from_task` | `'hello python'` кодируется в строку из условия |
| `test_round_trip` | `decode(encode(text)) == text` для разных фраз |
| `test_decode_pairs` | `00->'a'`, `01->'b'`, `25->'z'`, `26->' '` |
| `test_encode_single_chars` | Каждый символ даёт свою пару цифр |
| `test_empty_string` | Пустая строка кодируется и декодируется в пустую |
| `test_decode_odd_length` | Нечётная длина шифра -> `ValueError` |
| `test_decode_not_digits` | Буквы в шифре -> `ValueError` |
| `test_decode_code_out_of_range` | Код 27 -> `ValueError` с позицией |
| `test_decode_all_codes` | Все коды 27–99 отклоняются (через `subTest`) |
| `test_decode_not_a_string` | Число, `None`, список -> `ValueError` |
| `test_encode_forbidden_chars` | Заглавные, цифры, кириллица -> `ValueError` |
| `test_encode_not_a_string` | Не-строка -> `ValueError` |

Забавная деталь: тест `test_empty_string` на самом деле нашёл баг в первой
версии решения — пустой шифр отклонялся проверкой `isdigit()` (для пустой
строки она возвращает `False`). Именно поэтому пункт 1.4 (тесты) и нужен.
