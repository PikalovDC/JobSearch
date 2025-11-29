import requests

from src.abstract_api import AbstractAPI


class HH(AbstractAPI):
    """
    Класс для работы с API HeadHunter.
    """

    def __init__(self, file_worker):
        self._url = 'https://api.hh.ru/vacancies'
        self._headers = {'User-Agent': 'HH-User-Agent'}
        self._params = {'text': '', 'page': 0, 'per_page': 100}
        self._file_worker = file_worker
        self._vacancies = []

    def load_vacancies(self, keyword: str) -> None:
        """Загружает вакансии по ключевому слову."""
        self._params['text'] = keyword
        self._params['page'] = 0
        self._vacancies = []

        print(f"Поиск вакансий: '{keyword}'")

        while self._params['page'] < 20:
            try:
                response = requests.get(self._url, headers=self._headers, params=self._params)
                response.raise_for_status()

                data = response.json()
                items = data.get('items', [])
                self._vacancies.extend(items)

                # Проверяем последняя ли страница
                pages = data.get('pages', 1)
                if self._params['page'] >= pages - 1:
                    break

                self._params['page'] += 1

            except requests.RequestException as e:
                print(f"Ошибка при запросе к API: {e}")
                break

        print(f"Загружено вакансий: {len(self._vacancies)}")

    def save_vacancies(self) -> None:
        """Сохраняет загруженные вакансии в хранилище."""
        from src.vacancy import Vacancy
        if self._vacancies:
            vacancy_objects = Vacancy.cast_to_object_list(self._vacancies)
            self._file_worker.add_vacancies(vacancy_objects)
            print(f"Сохранено {len(vacancy_objects)} вакансий")
        else:
            print("Нет вакансий для сохранения")

    def get_vacancies_count(self) -> int:
        """Возвращает количество загруженных вакансий."""
        return len(self._vacancies)

    def clear_vacancies(self) -> None:
        """Очищает список вакансий."""
        self._vacancies = []
