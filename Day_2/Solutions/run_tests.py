# -*- coding: utf-8 -*-
"""
Запуск всех тестов в этой папке одной командой:

    python run_tests.py
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def run_tests() -> None:
    """Находит и запускает все *_test.py в текущей папке."""
    loader = unittest.TestLoader()
    suite = loader.discover(HERE, pattern='*_test.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # exit-код 1, если хоть один тест упал, — удобно для CI и терминала.
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    run_tests()
