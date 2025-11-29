import os

import pytest

from src.json_storage import JSONStorage
from src.vacancy import Vacancy


def test_storage_initialization():
    """Тест инициализации хранилища"""
    storage = JSONStorage("test_vacancies.json")
    assert storage._filename == "test_vacancies.json"


def test_add_and_get_vacancies():
    """Тест добавления и получения вакансий"""
    storage = JSONStorage("test_vacancies.json")
    storage.clear()

    vacancy = Vacancy(
        title="Test Developer",
        url="https://hh.ru/vacancy/999",
        salary={"from": 100000, "currency": "RUR"},
        description="Test description",
        requirements="Test requirements"
    )

    # Добавляем вакансию
    storage.add_vacancy(vacancy)

    # Получаем вакансии
    vacancies = storage.get_vacancies()

    assert len(vacancies) == 1
    assert vacancies[0].title == "Test Developer"
    assert vacancies[0].avg_salary == 100000

    # Очищаем тестовый файл
    storage.clear()
    if os.path.exists("test_vacancies.json"):
        os.remove("test_vacancies.json")


def test_filter_by_min_salary():
    """Тест фильтрации по минимальной зарплате"""
    storage = JSONStorage("test_vacancies.json")
    storage.clear()

    # Создаем тестовые вакансии с разной зарплатой
    vacancy1 = Vacancy("High Salary", "url1", {"from": 200000}, "desc1", "req1")
    vacancy2 = Vacancy("Low Salary", "url2", {"from": 50000}, "desc2", "req2")

    storage.add_vacancies([vacancy1, vacancy2])

    # Фильтруем по минимальной зарплате
    filtered = storage.get_vacancies(min_salary=100000)

    assert len(filtered) == 1
    assert filtered[0].title == "High Salary"

    storage.clear()
    if os.path.exists("test_vacancies.json"):
        os.remove("test_vacancies.json")


def test_filter_by_keyword():
    """Тест фильтрации по ключевому слову"""
    storage = JSONStorage("test_vacancies.json")
    storage.clear()

    vacancy1 = Vacancy("Python Developer", "url1", {"from": 100000}, "Работа с Django", "Python опыт")
    vacancy2 = Vacancy("Java Developer", "url2", {"from": 100000}, "Работа с Spring", "Java опыт")

    storage.add_vacancies([vacancy1, vacancy2])

    # Ищем Python вакансии
    python_vacancies = storage.get_vacancies(keyword="Python")
    django_vacancies = storage.get_vacancies(keyword="Django")

    assert len(python_vacancies) == 1
    assert len(django_vacancies) == 1
    assert python_vacancies[0].title == "Python Developer"

    storage.clear()
    if os.path.exists("test_vacancies.json"):
        os.remove("test_vacancies.json")


def test_duplicate_handling():
    """Тест обработки дубликатов"""
    storage = JSONStorage("test_vacancies.json")
    storage.clear()

    vacancy = Vacancy(
        title="Duplicate Job",
        url="https://hh.ru/vacancy/111",
        salary={"from": 100000},
        description="Test",
        requirements="Test"
    )

    # Добавляем одну и ту же вакансию дважды
    storage.add_vacancies([vacancy, vacancy])

    vacancies = storage.get_vacancies()

    # Дубликаты должны быть удалены
    assert len(vacancies) == 1

    storage.clear()
    if os.path.exists("test_vacancies.json"):
        os.remove("test_vacancies.json")
