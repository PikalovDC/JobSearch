from abc import ABC, abstractmethod


class AbstractStorage(ABC):
    """
    Абстрактный класс для работы с хранилищем вакансий.
    """

    @abstractmethod
    def add_vacancy(self, vacancy) -> None:
        """Добавляет одну вакансию в хранилище."""
        pass

    @abstractmethod
    def get_vacancies(self, **criteria) -> list:
        """Получает вакансии по критериям."""
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy) -> None:
        """Удаляет вакансию из хранилища."""
        pass

    @abstractmethod
    def add_vacancies(self, vacancies: list) -> None:
        """Добавляет список вакансий в хранилище."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Очищает хранилище."""
        pass
