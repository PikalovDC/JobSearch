import pytest

from src.hh_api import HH
from src.json_storage import JSONStorage


def test_hh_api_initialization():
    """Тест инициализации HH API"""
    storage = JSONStorage('test.json')
    hh_api = HH(storage)

    assert hh_api._url == 'https://api.hh.ru/vacancies'
    assert "User-Agent" in hh_api._headers
    assert hh_api._params['per_page'] == 100


def test_vacancies_count():
    """Тест подсчета количества вакансий"""
    storage = JSONStorage('test.json')
    hh_api = HH(storage)

    # Изначально вакансий нет
    assert hh_api.get_vacancies_count() == 0

    # Очистка вакансий
    hh_api.clear_vacancies()

    assert hh_api.get_vacancies_count() == 0


def test_save_vacancy_empty():
    """Тест сохранения пустого списка вакансий"""
    storage = JSONStorage('test.json')
    hh_api = HH(storage)

    hh_api.save_vacancies()
