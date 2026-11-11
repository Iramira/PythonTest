# -*- coding: utf-8 -*-
"""
Тесты к задаче Day_2 «encode / decode» (пункт 1.4).

Запуск из папки Day_2/Practice:
    python -m unittest encode_decode_test -v
"""

import unittest

from encode_decode import encode, decode


class TestEncodeDecode(unittest.TestCase):
    """Проверки корректных данных (пункты 1.1, 1.2)."""

    def test_decode_example_from_task(self):
        """Пример из условия: '070411111426152419071413' -> 'hello python'."""
        self.assertEqual(decode('070411111426152419071413'), 'hello python')

    def test_encode_example_from_task(self):
        """Шифровка 'hello python' даёт строку из условия."""
        self.assertEqual(encode('hello python'), '070411111426152419071413')

    def test_round_trip(self):
        """encode + decode возвращают исходный текст (взаимная обратимость)."""
        texts = ['a', 'hello', 'a b', 'hello python', 'xyz']
        for text in texts:
            with self.subTest(text=text):
                self.assertEqual(decode(encode(text)), text)

    def test_decode_pairs(self):
        """Каждая пара декодируется по правилу 00->a, 25->z, 26->пробел."""
        self.assertEqual(decode('00'), 'a')
        self.assertEqual(decode('01'), 'b')
        self.assertEqual(decode('25'), 'z')
        self.assertEqual(decode('26'), ' ')

    def test_encode_single_chars(self):
        """Каждый символ кодируется двумя цифрами."""
        self.assertEqual(encode('a'), '00')
        self.assertEqual(encode('z'), '25')
        self.assertEqual(encode(' '), '26')

    def test_empty_string(self):
        """Пустая строка кодируется и декодируется в пустую."""
        self.assertEqual(encode(''), '')
        self.assertEqual(decode(''), '')


class TestInvalidInput(unittest.TestCase):
    """Проверки некорректных данных (пункт 1.3)."""

    def test_decode_odd_length(self):
        """Нечётная длина шифра -> ValueError с пояснением."""
        with self.assertRaises(ValueError) as ctx:
            decode('072')
        self.assertIn('нечётная', str(ctx.exception))

    def test_decode_not_digits(self):
        """Буквы внутри шифра -> ValueError."""
        with self.assertRaises(ValueError) as ctx:
            decode('07ab')
        self.assertIn('только из цифр', str(ctx.exception))

    def test_decode_code_out_of_range(self):
        """Пара больше 26 -> ValueError с указанием позиции."""
        with self.assertRaises(ValueError) as ctx:
            decode('0727')
        self.assertIn('27', str(ctx.exception))

    def test_decode_all_codes(self):
        """Все недопустимые коды 27-99 отклоняются."""
        for code in range(27, 100):
            with self.subTest(code=code):
                with self.assertRaises(ValueError):
                    decode(f'{code:02d}')

    def test_decode_not_a_string(self):
        """Не-строка (число, None) -> ValueError, а не TypeError."""
        for value in (123, None, ['07']):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    decode(value)

    def test_encode_forbidden_chars(self):
        """Заглавные буквы, цифры, кириллица -> ValueError."""
        for text in ['Hello', 'h1', 'привет', 'hello!']:
            with self.subTest(text=text):
                with self.assertRaises(ValueError) as ctx:
                    encode(text)
                self.assertIn('Недопустимые символы', str(ctx.exception))

    def test_encode_not_a_string(self):
        """Не-строка -> ValueError."""
        for value in (123, None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    encode(value)


if __name__ == '__main__':
    unittest.main(verbosity=2)
