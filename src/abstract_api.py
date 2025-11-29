from abc import ABC, abstractmethod


class AbstractAPI(ABC):
    """
    Абстрактный класс для работы с API сервиса с вакансиями.
    """

    @abstractmethod
    def load_vacancies(self, keyword: str) -> list:
        """
        Получает вакансии по ключевому слову. Возвращает список вакансий
        """
        pass
