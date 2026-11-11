# -*- coding: utf-8 -*-
"""
Задача №1 (Day_2, практика)

1.1 Программа расшифровывает строку: каждый символ закодирован
    двумя цифрами. Отсчёт с 00 -> 'a', 01 -> 'b' ... 25 -> 'z',
    26 -> ' ' (пробел, в набор букв не входит).
1.2 Расшифровка и зашифровка реализованы через функции:
    decode('070411111426152419071413') -> 'hello python'
    encode('hello python')            -> '070411111426152419071413'
1.3 Некорректные входные данные не «роняют» программу:
    функции поднимают ValueError с понятным пояснением.
1.4 Тесты — в файле encode_decode_test.py.
"""

# Символ, кодирующий пробел (в алфавит не входит)
SPACE_CODE = 26

# 'abcdefghijklmnopqrstuvwxyz' -> коды 00..25
ALPHABET = ''.join(chr(code) for code in range(ord('a'), ord('z') + 1))


def encode(text: str) -> str:
    """Зашивровывает текст в строку цифр.

    Каждый символ превращается в две цифры:
    'a'..'z' -> '00'..'25', пробел -> '26'.

    >>> encode('hello python')
    '070411111426152419071413'

    :param text: текст из строчных латинских букв и пробелов
    :return: строка из цифр (длина всегда чётная)
    :raises ValueError: если текст содержит недопустимые символы
    """
    if not isinstance(text, str):
        raise ValueError('Текст должен быть строкой')

    wrong = sorted({ch for ch in text if ch not in ALPHABET and ch != ' '})
    if wrong:
        shown = ''.join(wrong)
        raise ValueError(
            f'Недопустимые символы в тексте: {shown}. '
            'Разрешены только строчные латинские буквы a-z и пробел'
        )

    return ''.join(
        f'{SPACE_CODE:02d}' if ch == ' ' else f'{ALPHABET.index(ch):02d}'
        for ch in text
    )


def decode(cipher: str) -> str:
    """Расшифровывает строку цифр обратно в текст.

    >>> decode('070411111426152419071413')
    'hello python'

    :param cipher: строка из цифр, длина обязана быть чётной,
                   каждая пара — число от 00 до 26
    :return: текст
    :raises ValueError: если шифр некорректен (с пояснением причины)
    """
    if not isinstance(cipher, str):
        raise ValueError('Шифр должен быть строкой')

    if len(cipher) % 2 != 0:
        raise ValueError(
            f'Длина шифра {len(cipher)} нечётная: '
            'каждый символ кодируется двумя цифрами'
        )

    # Пустая строка — корректный шифр пустого текста,
    # поэтому проверяем isdigit() только для непустого шифра.
    if cipher and not cipher.isdigit():
        raise ValueError('Шифр должен состоять только из цифр')

    result = []
    for i in range(0, len(cipher), 2):
        code = int(cipher[i:i + 2])
        if code > SPACE_CODE:
            raise ValueError(
                f'Пара "{cipher[i:i + 2]}" на позициях {i}-{i + 1}: '
                'коды больше 26 не существуют (00-25 буквы, 26 пробел)'
            )
        result.append(' ' if code == SPACE_CODE else ALPHABET[code])

    return ''.join(result)


def main() -> None:
    """Демонстрация: шифруем текст и расшифровываем обратно."""
    text = 'hello python'
    cipher = encode(text)
    print(f'Текст:  {text!r}')
    print(f'Шифр:   {cipher!r}')
    print(f'Обратно: {decode(cipher)!r}')

    # Пример обработки ошибок (пункт 1.3)
    try:
        decode('072')
    except ValueError as exc:
        print(f'\nПример ошибки: {exc}')


if __name__ == '__main__':
    main()
