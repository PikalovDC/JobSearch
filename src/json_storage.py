import json

from src.abstract_storage import AbstractStorage
from src.vacancy import Vacancy


class JSONStorage(AbstractStorage):
    """
    Класс для сохранения информации о вакансиях в JSON-файл.
    """

    def __init__(self, filename: str = 'vacancies.json'):
        self._filename = filename

    def add_vacancy(self, vacancy: Vacancy) -> None:
        vacancies = self._load_vacancies()
        vacancies.append(self._vacancy_to_dict(vacancy))
        self._save_vacancies(vacancies)

    def get_vacancies(self, **criteria) -> list:
        vacancies_data = self._load_vacancies()
        vacancies = [self._dict_to_vacancy(data) for data in vacancies_data]

        filtered_vacancies = []
        for vacancy in vacancies:
            if self._matches_criteria(vacancy, criteria):
                filtered_vacancies.append(vacancy)

        return filtered_vacancies

    def delete_vacancy(self, vacancy: Vacancy) -> None:
        vacancies = self._load_vacancies()
        vacancy_dict = self._vacancy_to_dict(vacancy)
        vacancies = [v for v in vacancies if v != vacancy_dict]
        self._save_vacancies(vacancies)

    def add_vacancies(self, vacancies: list) -> None:
        existing_vacancies = self._load_vacancies()
        new_vacancies = [self._vacancy_to_dict(v) for v in vacancies]

        all_vacancies = existing_vacancies + new_vacancies
        unique_vacancies = []
        seen = set()

        for vacancy in all_vacancies:
            vacancy_tuple = (vacancy['title'], vacancy['url'])
            if vacancy_tuple not in seen:
                seen.add(vacancy_tuple)
                unique_vacancies.append(vacancy)

        self._save_vacancies(unique_vacancies)

    def clear(self) -> None:
        self._save_vacancies([])

    def _load_vacancies(self) -> list:
        try:
            with open(self._filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_vacancies(self, vacancies: list) -> None:
        with open(self._filename, 'w', encoding='utf-8') as f:
            json.dump(vacancies, f, ensure_ascii=False, indent=2)

    def _vacancy_to_dict(self, vacancy: Vacancy) -> dict:
        return {
            'title': vacancy.title,
            'url': vacancy.url,
            'salary': vacancy.salary,
            'description': vacancy.description,
            'requirements': vacancy.requirements
        }

    def _dict_to_vacancy(self, data: dict) -> Vacancy:
        return Vacancy(
            title=data['title'],
            url=data['url'],
            salary=data['salary'],
            description=data['description'],
            requirements=data['requirements']
        )

    def _matches_criteria(self, vacancy: Vacancy, criteria: dict) -> bool:
        # Проверка по ключевому слову в названии, описании и требованиях
        if 'keyword' in criteria:
            keyword = criteria['keyword'].lower()
            if (keyword not in vacancy.title.lower() and
                    keyword not in vacancy.description.lower() and
                    keyword not in vacancy.requirements.lower()):
                return False

        # Проверка по названию
        if 'title' in criteria and criteria['title'].lower() not in vacancy.title.lower():
            return False

        # Проверка по минимальной зарплате
        if 'min_salary' in criteria and vacancy.avg_salary < criteria['min_salary']:
            return False

        # Проверка по максимальной зарплате
        if 'max_salary' in criteria and vacancy.avg_salary > criteria['max_salary']:
            return False

        # Проверка по валюте
        if 'currency' in criteria and criteria['currency'].lower() not in vacancy.salary.get('currency', '').lower():
            return False

        return True
