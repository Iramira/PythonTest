"""Начальный этап, пункты 4–5: return и scope по умолчанию (function)."""

import pytest


@pytest.fixture()
def sample_tuple():
    """Свежий кортеж для каждого запрашивающего теста."""
    # Сравниваем эту версию с test_fixtures_module.py.
    print("\nSETUP sample_tuple (function)")
    return ((1, "hello"), (2, "python"))


def test_tuple_structure(sample_tuple):
    assert isinstance(sample_tuple, tuple)
    assert len(sample_tuple) == 2


def test_tuple_content(sample_tuple):
    assert sample_tuple == ((1, "hello"), (2, "python"))
