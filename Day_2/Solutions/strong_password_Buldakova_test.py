# -*- coding: utf-8 -*-
"""
Автотесты для Задачи №1 «Проверка пароля» (strong_password_Buldakova.py).

Запуск (из папки, где лежит файл):
    python -m unittest strong_password_Buldakova_test -v
или короче:
    python -m unittest -v
или через runner-файл:
    python run_tests.py
"""

import os
import sys
import unittest

# Гарантируем, что папка с тестируемым модулем видна Python'у,
# откуда бы мы ни запускали тесты.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from strong_password_Buldakova import check_password  # noqa: E402


class TestCheckPassword(unittest.TestCase):
    """Тесты функции check_password."""

    # --- Базовое поведение -------------------------------------------

    def test_returns_tuple(self):
        """Функция возвращает кортеж (bool, str)."""
        result = check_password('aaaAAA111!!!')
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], bool)
        self.assertIsInstance(result[1], str)

    def test_valid_password(self):
        """Правильный пароль из примера к задаче проходит."""
        ok, reasons = check_password('o58anuahaunH!')
        self.assertTrue(ok)
        self.assertEqual(reasons, 'пароль подходит')

    def test_valid_password_from_task_example(self):
        """Второй правильный пример из условия: aaaAAA111!!!."""
        ok, reasons = check_password('aaaAAA111!!!')
        self.assertTrue(ok)

    def test_invalid_password_from_task_example(self):
        """Пример из условия, который НЕ проходит: saucacAusacu8."""
        ok, reasons = check_password('saucacAusacu8')
        self.assertFalse(ok)
        self.assertIn('спецсимвол', reasons)

    # --- Обязательный символ из каждого набора ------------------------

    def test_digits(self):
        """Пароль без цифр не проходит, в сообщении указана причина."""
        ok, reasons = check_password('aaaAAA!@#')
        self.assertFalse(ok)
        self.assertIn('цифру', reasons)

    def test_lowercase(self):
        """Пароль без строчных букв не проходит."""
        ok, reasons = check_password('AAA111!@#')
        self.assertFalse(ok)
        self.assertIn('строчную', reasons)

    def test_uppercase(self):
        """Пароль без прописных букв не проходит."""
        ok, reasons = check_password('aaa111!@#')
        self.assertFalse(ok)
        self.assertIn('прописную', reasons)

    def test_special(self):
        """Пароль без спецсимволов не проходит."""
        ok, reasons = check_password('aaaAAA111')
        self.assertFalse(ok)
        self.assertIn('спецсимвол', reasons)

    def test_missing_sets_combinations(self):
        """Разные сочетания отсутствующих наборов дают False."""
        passwords = [
            'aaaa!@#',        # нет цифр и прописных
            '1111!@#',        # нет букв вообще
            'aaaa111',        # нет прописных и спецсимволов
            'AAAA!!!!AAAAA',  # нет цифр и строчных
        ]
        for password in passwords:
            with self.subTest(password=password):
                ok, reasons = check_password(password)
                self.assertFalse(ok, f'{password!r} должен быть отклонён')

    # --- Длина пароля --------------------------------------------------

    def test_length_min(self):
        """Минимальная длина 8 символов: 8 проходит, 7 — нет."""
        ok, _ = check_password('a1A!' + 'a' * 4)    # ровно 8
        self.assertTrue(ok, 'пароль из 8 символов должен проходить')
        ok, reasons = check_password('a1A!' + 'a' * 3)  # ровно 7
        self.assertFalse(ok, 'пароль из 7 символов должен быть отклонён')
        self.assertIn('длина', reasons)

    def test_length_max(self):
        """Максимальная длина 15 символов: 15 проходит, 16 — нет."""
        ok, _ = check_password('a1A!' + 'a' * 11)   # ровно 15
        self.assertTrue(ok, 'пароль из 15 символов должен проходить')
        ok, reasons = check_password('a1A!' + 'a' * 12)  # ровно 16
        self.assertFalse(ok, 'пароль из 16 символов должен быть отклонён')
        self.assertIn('длина', reasons)

    def test_length_empty(self):
        """Пустой пароль отклоняется с пояснением про длину."""
        ok, reasons = check_password('')
        self.assertFalse(ok)
        self.assertIn('длина', reasons)

    # --- Недопустимые символы ------------------------------------------

    def test_forbidden_symbols(self):
        """Символы вне четырёх наборов отклоняются."""
        passwords = [
            'a1A!aaaaä',    # латинская с умлаутом
            'a1A!aaaa ',    # пробел
            'парольAa1!',   # кириллица
            'a1A!aaaa~',    # тильда — её нет в наборе _!@#$%^&
            'a1A!aaaa(abc)',  # скобки
        ]
        for password in passwords:
            with self.subTest(password=password):
                ok, reasons = check_password(password)
                self.assertFalse(ok, f'{password!r} должен быть отклонён')
                self.assertIn('недопустимые символы', reasons)

    def test_all_special_chars_allowed(self):
        """Каждый спецсимвол набора _!@#$%^& — допустим."""
        for symbol in '_!@#$%^&':
            with self.subTest(symbol=symbol):
                password = 'a1A' + 'a' * 4 + symbol  # длина 8
                ok, _ = check_password(password)
                self.assertTrue(ok, f'символ {symbol!r} должен быть разрешён')

    # --- Нестроковый ввод ----------------------------------------------

    def test_not_a_string(self):
        """Не-строка (число, None) отклоняется без исключения."""
        for value in (12345, None, ['a1A!aaaa']):
            with self.subTest(value=value):
                ok, reasons = check_password(value)
                self.assertFalse(ok)
                self.assertIn('строкой', reasons)


if __name__ == '__main__':
    unittest.main(verbosity=2)
