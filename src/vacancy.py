class Vacancy:
    """
    Класс для представления вакансии.
    """

    __slots__ = ('title', 'url', 'salary', 'description', 'requirements', '_avg_salary')

    def __init__(self, title: str, url: str, salary: dict, description: str, requirements: str):
        self.title = title
        self.url = url
        self.salary = salary
        self.description = description
        self.requirements = requirements
        self._avg_salary = None  # Кэшируем вычисленную зарплату

        # Валидация данных
        self._validate_data()

    def _validate_data(self):
        """Валидация данных вакансии."""
        if not self.title or not isinstance(self.title, str):
            self.title = "Название не указано"

        if not self.url or not isinstance(self.url, str):
            self.url = "Ссылка не указана"
        elif not self.url.startswith(('http://', 'https://')):
            self.url = "Ссылка не указана"

        if not self.salary or not isinstance(self.salary, dict):
            self.salary = {"from": 0, "to": 0, "currency": "Не указана"}
        else:
            self.salary = {
                'from': self.salary.get('from', 0) or 0,
                'to': self.salary.get('to', 0) or 0,
                'currency': self.salary.get('currency', 'Не указана') or 'Не указана'
            }

        if not self.description or not isinstance(self.description, str):
            self.description = "Описание не указано"

        if not self.requirements or not isinstance(self.requirements, str):
            self.requirements = "Требования не указаны"

    @property
    def avg_salary(self) -> int:
        """Вычисляет среднюю зарплату. С кэшированием"""
        if self._avg_salary is not None:
            return self._avg_salary

        from_salary = self.salary.get('from', 0)
        to_salary = self.salary.get('to', 0)

        if from_salary and to_salary:
            return (from_salary + to_salary) // 2
        elif from_salary:
            return from_salary
        elif to_salary:
            return to_salary
        else:
            return 0

    def __str__(self) -> str:
        salary_info = f"{self.avg_salary} {self.salary.get('currency', '')}"
        if self.avg_salary == 0:
            salary_info = "Зарплата не указана"

        return (f"Вакансия: {self.title}\n"
                f"Зарплата: {salary_info}\n"
                f"Ссылка: {self.url}\n"
                f"Описание: {self.description[:100]}...")

    def __repr__(self) -> str:
        return f"Vacancy('{self.title}', {self.avg_salary})"

    # Методы для сравнения:
    def __eq__(self, other) -> bool:  # ==
        if not isinstance(other, Vacancy):
            return False
        return self.avg_salary == other.avg_salary

    def __ne__(self, other) -> bool:  # !=
        if not isinstance(other, Vacancy):
            return False
        return self.avg_salary != other.avg_salary

    def __lt__(self, other) -> bool:  # <
        if not isinstance(other, Vacancy):
            return False
        return self.avg_salary < other.avg_salary

    def __le__(self, other) -> bool:  # <=
        if not isinstance(other, Vacancy):
            return False
        return self.avg_salary <= other.avg_salary

    def __gt__(self, other) -> bool:  # >
        if not isinstance(other, Vacancy):
            return False
        return self.avg_salary > other.avg_salary

    def __ge__(self, other) -> bool:  # >=
        if not isinstance(other, Vacancy):
            return False
        return self.avg_salary >= other.avg_salary

    @classmethod
    def cast_to_object_list(cls, vacancies_data: list) -> list:
        """Преобразует сырые данные в список объектов Vacancy."""
        vacancies = []
        for data in vacancies_data:
            try:
                title = data.get('name', '')
                url = data.get('alternate_url', '')
                salary = data.get('salary')
                snippet = data.get('snippet', {})
                description = snippet.get('responsibility', '')
                requirements = snippet.get('requirement', '')

                vacancy = cls(title, url, salary, description, requirements)
                vacancies.append(vacancy)
            except Exception:
                continue

        return vacancies
