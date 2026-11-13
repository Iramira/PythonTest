"""Итог упражнения: module-фикстура с yield и зависимые function-фикстуры."""

import pytest


@pytest.fixture(scope="module")
def sample_tuple():
    """Общий кортеж пар для двух прямых тестов и зависимых фикстур."""
    # Пункты 6–10: подготовка один раз на модуль, завершение после
    # последнего использующего её теста. Это демонстрация жизненного цикла.
    # Кортеж неизменяемый: тесты не могут случайно изменить общие пары.
    print("\nSETUP sample_tuple: подготовка общего кортежа")
    yield ((1, "hello"), (2, "python"))
    # Реального внешнего ресурса здесь нет, поэтому закрывать нечего.
    # В реальном проекте здесь можно закрыть соединение или удалить файл.
    print("\nTEARDOWN sample_tuple: завершение работы с общим кортежем")


@pytest.fixture()
def sample_list(sample_tuple):
    """Новый список пар на основе общего кортежа для каждого теста."""
    # Scope по умолчанию — function. Новый список исключает перенос
    # изменений списка из одного теста в другой.
    return list(sample_tuple)


@pytest.fixture()
def sample_dict(sample_tuple):
    """Новый словарь: номер слова → слово."""
    # Фикстуры можно запрашивать в других фикстурах, как в примере занятия.
    return dict(sample_tuple)


def test_tuple_structure(sample_tuple):
    """Первый тест общей фикстуры: тип и количество пар."""
    assert isinstance(sample_tuple, tuple)
    assert len(sample_tuple) == 2
    assert all(isinstance(pair, tuple) and len(pair) == 2 for pair in sample_tuple)


def test_tuple_content(sample_tuple):
    """Второй тест той же фикстуры: точные значения."""
    assert sample_tuple == ((1, "hello"), (2, "python"))


def test_list_content(sample_list):
    assert isinstance(sample_list, list)
    assert sample_list == [(1, "hello"), (2, "python")]


def test_list_can_be_changed_locally(sample_list):
    # Изменяем только собственный function-scoped список.
    # Тест не зависит от порядка запуска других тестов.
    sample_list.append((3, "pytest"))
    assert sample_list == [(1, "hello"), (2, "python"), (3, "pytest")]


def test_dict_content(sample_dict):
    assert isinstance(sample_dict, dict)
    assert sample_dict == {1: "hello", 2: "python"}


def test_fixtures_agree(sample_tuple, sample_list, sample_dict):
    """Один тест может одновременно использовать несколько фикстур."""
    assert tuple(sample_list) == sample_tuple
    assert dict(sample_list) == sample_dict
