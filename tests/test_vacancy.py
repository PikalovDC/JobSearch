import pytest

from src.vacancy import Vacancy


def test_vacancy_creation():
    """Тест создания вакансии с полными данными"""
    vacancy = Vacancy(
        title="Python Developer",
        url="https://hh.ru/vacancy/123",
        salary={"from": 100000, "to": 150000, "currency": "RUR"},
        description="Разработка backend приложений",
        requirements="Опыт Python 3+"
    )

    assert vacancy.title == "Python Developer"
    assert vacancy.url == "https://hh.ru/vacancy/123"
    assert vacancy.salary == {"from": 100000, "to": 150000, "currency": "RUR"}
    assert vacancy.description == "Разработка backend приложений"
    assert vacancy.requirements == "Опыт Python 3+"


def test_vacancy_validation_empty_data():
    """Тест валидации пустых данных"""
    vacancy = Vacancy("", "", None, "", "")

    assert vacancy.title == "Название не указано"
    assert vacancy.url == "Ссылка не указана"
    assert vacancy.salary == {"from": 0, "to": 0, "currency": "Не указана"}
    assert vacancy.description == "Описание не указано"
    assert vacancy.requirements == "Требования не указаны"


def test_avg_salary_calculation():
    """Тест расчета средней зарплаты"""
    # Зарплата от и до
    vacancy1 = Vacancy("Test", "url", {"from": 100000, "to": 150000, "currency": "RUR"}, "", "")
    assert vacancy1.avg_salary == 125000

    # Только от
    vacancy2 = Vacancy("Test", "url", {"from": 100000, "currency": "RUR"}, "", "")
    assert vacancy2.avg_salary == 100000

    # Только до
    vacancy3 = Vacancy("Test", "url", {"to": 150000, "currency": "RUR"}, "", "")
    assert vacancy3.avg_salary == 150000

    # Нет зарплаты
    vacancy4 = Vacancy("Test", "url", None, "", "")
    assert vacancy4.avg_salary == 0


def test_salary_comparison():
    """Тест сравнения вакансий по зарплате"""
    vacancy_low = Vacancy("Low", "url", {"from": 50000}, "", "")
    vacancy_high = Vacancy("High", "url", {"from": 100000}, "", "")

    assert vacancy_high > vacancy_low
    assert vacancy_low < vacancy_high
    assert vacancy_high != vacancy_low


def test_cast_to_object_list():
    """Тест преобразования сырых данных в объекты Vacancy"""
    raw_data = [
        {
            'name': 'Python Developer',
            'alternate_url': 'https://hh.ru/vacancy/123',
            'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
            'snippet': {
                'responsibility': 'Backend development',
                'requirement': 'Python experience'
            }
        },
        {
            'name': 'Data Scientist',
            'alternate_url': 'https://hh.ru/vacancy/456',
            'salary': None,
            'snippet': {
                'responsibility': '',
                'requirement': ''
            }
        }
    ]

    vacancies = Vacancy.cast_to_object_list(raw_data)

    assert len(vacancies) == 2
    assert isinstance(vacancies[0], Vacancy)
    assert vacancies[0].title == "Python Developer"
    assert vacancies[1].title == "Data Scientist"


def test_str_representation():
    """Тест строкового представления вакансии"""
    vacancy = Vacancy(
        title="Python Developer",
        url="https://hh.ru/vacancy/123",
        salary={"from": 100000, "to": 150000, "currency": "RUR"},
        description="Разработка backend приложений на Python",
        requirements="Опыт работы от 1 года"
    )

    result = str(vacancy)
    assert "Python Developer" in result
    assert "125000" in result
    assert "https://hh.ru/vacancy/123" in result
    assert "Разработка backend" in result
