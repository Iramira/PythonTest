"""Промежуточный этап, пункты 6–7: scope='module', пока ещё с return."""

import pytest


@pytest.fixture(scope="module")
def sample_tuple():
    """Общий кортеж для двух тестов этого модуля."""
    # От начальной версии отличается только областью действия.
    # В --setup-show теперь один SETUP M вместо двух SETUP F.
    print("\nSETUP sample_tuple (module)")
    return ((1, "hello"), (2, "python"))


def test_tuple_structure(sample_tuple):
    assert isinstance(sample_tuple, tuple)
    assert len(sample_tuple) == 2


def test_tuple_content(sample_tuple):
    assert sample_tuple == ((1, "hello"), (2, "python"))
