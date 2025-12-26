from typing import Any, Dict, List, Optional

import psycopg2

from src.config import DB_CONFIG

"""
Класс для работы с базой данных PostgreSQL
"""


class DBManager:
    """
    Класс для управления базой данных вакансий.
    """

    def __init__(self, db_config: Optional[Dict] = None):
        """
        Инициализация подключения к базе данных.
        """
        self.config = db_config or DB_CONFIG
        self.conn = None
        self._connect()

    def _connect(self):
        """Устанавливает подключение к базе данных."""
        try:
            print("🔧 Подключение к PostgreSQL...")

            self.conn = psycopg2.connect(
                host='localhost',
                port=5432,
                database='hh_vacancies',
                user='postgres',
                password='simple123'
            )

            print("Подключение успешно!")

        except Exception as e:
            print(f"Ошибка подключения: {e}")
            raise

    def close(self):
        """Закрывает соединение с базой данных."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Поддержка контекстного менеджера."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрытие соединения при выходе из контекста."""
        self.close()

    def get_companies_and_vacancies_count(self) -> List[Dict]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        e.name AS company_name,
                        COUNT(v.id) AS vacancies_count
                    FROM employers e
                    LEFT JOIN vacancies v ON e.id = v.employer_id
                    GROUP BY e.id, e.name
                    ORDER BY vacancies_count DESC
                """)

                result = []
                for row in cur.fetchall():
                    result.append({
                        'company': row[0],
                        'vacancies_count': row[1] or 0
                    })

                return result

        except Exception as e:
            print(f"Ошибка при получении списка компаний: {e}")
            return []

    def get_all_vacancies(self) -> List[Dict]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        e.name AS company_name,
                        v.title AS vacancy_title,
                        v.salary_from,
                        v.salary_to,
                        v.currency,
                        v.url AS vacancy_url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.id
                    ORDER BY company_name, v.title
                """)

                result = []
                for row in cur.fetchall():
                    salary_info = self._format_salary(row[2], row[3], row[4])
                    result.append({
                        'company': row[0],
                        'vacancy': row[1],
                        'salary': salary_info,
                        'url': row[5]
                    })

                return result

        except Exception as e:
            print(f"Ошибка при получении списка вакансий: {e}")
            return []

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям.
        """
        try:
            with self.conn.cursor() as cur:
                # Средняя зарплата считается как (salary_from + salary_to) / 2
                # Если одно из значений отсутствует, берем имеющееся
                cur.execute("""
                    SELECT 
                        AVG(
                            CASE 
                                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                                    AND salary_from > 0 AND salary_to > 0 
                                    THEN (salary_from + salary_to) / 2.0
                                WHEN salary_from IS NOT NULL AND salary_from > 0 
                                    THEN salary_from::float
                                WHEN salary_to IS NOT NULL AND salary_to > 0 
                                    THEN salary_to::float
                                ELSE NULL
                            END
                        ) AS avg_salary
                    FROM vacancies
                    WHERE (salary_from IS NOT NULL AND salary_from > 0)
                        OR (salary_to IS NOT NULL AND salary_to > 0)
                """)

                result = cur.fetchone()[0]
                return round(result, 2) if result else 0.0

        except Exception as e:
            print(f"Ошибка при расчете средней зарплаты: {e}")
            return 0.0

    def get_vacancies_with_higher_salary(self) -> List[Dict]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        """
        try:
            avg_salary = self.get_avg_salary()

            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        e.name AS company_name,
                        v.title AS vacancy_title,
                        v.salary_from,
                        v.salary_to,
                        v.currency,
                        v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.id
                    WHERE 
                        (v.salary_from IS NOT NULL AND v.salary_from > %s) OR
                        (v.salary_to IS NOT NULL AND v.salary_to > %s) OR
                        (v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL 
                         AND (v.salary_from + v.salary_to) / 2 > %s)
                    ORDER BY 
                        CASE 
                            WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL 
                                THEN (salary_from + salary_to) / 2
                            WHEN salary_from IS NOT NULL 
                                THEN salary_from
                            ELSE salary_to
                        END DESC
                """, (avg_salary, avg_salary, avg_salary))

                result = []
                for row in cur.fetchall():
                    salary_info = self._format_salary(row[2], row[3], row[4])
                    result.append({
                        'company': row[0],
                        'vacancy': row[1],
                        'salary': salary_info,
                        'url': row[5]
                    })

                return result

        except Exception as e:
            print(f"Ошибка при получении вакансий с высокой зарплатой: {e}")
            return []

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict]:
        """
        Получает список всех вакансий, в названии которых содержатся переданные слова.
        """
        try:
            with self.conn.cursor() as cur:
                # Используем ILIKE для регистронезависимого поиска
                cur.execute("""
                    SELECT 
                        e.name AS company_name,
                        v.title AS vacancy_title,
                        v.salary_from,
                        v.salary_to,
                        v.currency,
                        v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.id
                    WHERE v.title ILIKE %s
                    ORDER BY e.name, v.title
                """, (f'%{keyword}%',))

                result = []
                for row in cur.fetchall():
                    salary_info = self._format_salary(row[2], row[3], row[4])
                    result.append({
                        'company': row[0],
                        'vacancy': row[1],
                        'salary': salary_info,
                        'url': row[5]
                    })

                return result

        except Exception as e:
            print(f"Ошибка при поиске вакансий по ключевому слову: {e}")
            return []

    def insert_employer(self, employer_data: Dict[str, Any]) -> bool:
        """
        Вставляет данные о работодателе в базу данных.
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO employers (id, name, url, description, open_vacancies)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        url = EXCLUDED.url,
                        description = EXCLUDED.description,
                        open_vacancies = EXCLUDED.open_vacancies
                """, (
                    employer_data.get('id'),
                    employer_data.get('name'),
                    employer_data.get('alternate_url'),
                    employer_data.get('description'),
                    employer_data.get('open_vacancies', 0)
                ))

                self.conn.commit()
                return True

        except Exception as e:
            print(f"Ошибка при вставке работодателя: {e}")
            self.conn.rollback()
            return False

    def insert_vacancy(self, vacancy_data: Dict[str, Any]) -> bool:
        """
        Вставляет данные о вакансии в базу данных.
        """
        try:
            # Извлекаем данные с проверкой на None
            vacancy_id = vacancy_data.get('id')
            employer = vacancy_data.get('employer', {})
            employer_id = employer.get('id') if employer else None
            title = vacancy_data.get('name')

            # Проверка обязательных полей
            if not vacancy_id or not employer_id or not title:
                print(f"Пропускаем: недостаточно данных")
                return False

            # Обработка зарплаты (может быть None)
            salary = vacancy_data.get('salary')
            if salary:
                salary_from = salary.get('from')
                salary_to = salary.get('to')
                currency = salary.get('currency')
            else:
                salary_from = None
                salary_to = None
                currency = None

            # Обработка snippet
            snippet = vacancy_data.get('snippet', {})
            description = snippet.get('responsibility', '')
            requirements = snippet.get('requirement', '')

            # Обработка опыта и занятости
            experience_data = vacancy_data.get('experience', {})
            experience = experience_data.get('name', '') if experience_data else ''

            employment_data = vacancy_data.get('employment', {})
            employment = employment_data.get('name', '') if employment_data else ''

            # URL вакансии
            url = vacancy_data.get('alternate_url', '')

            # ВСТАВКА в БД
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO vacancies (
                        id, employer_id, title, salary_from, salary_to, 
                        currency, url, description, requirements, 
                        experience, employment
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        salary_from = EXCLUDED.salary_from,
                        salary_to = EXCLUDED.salary_to,
                        currency = EXCLUDED.currency,
                        url = EXCLUDED.url,
                        description = EXCLUDED.description,
                        requirements = EXCLUDED.requirements,
                        experience = EXCLUDED.experience,
                        employment = EXCLUDED.employment
                """, (
                    vacancy_id,
                    employer_id,
                    title,
                    salary_from,
                    salary_to,
                    currency,
                    url,
                    description,
                    requirements,
                    experience,
                    employment
                ))

                self.conn.commit()
                return True

        except Exception as e:
            print(f"Ошибка при вставке: {e}")
            self.conn.rollback()
            return False

    def get_vacancies_count(self) -> int:
        """Возвращает общее количество вакансий в базе."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM vacancies")
                return cur.fetchone()[0]
        except Exception as e:
            print(f"Ошибка при подсчете вакансий: {e}")
            return 0

    def get_employers_count(self) -> int:
        """Возвращает количество работодателей в базе."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM employers")
                return cur.fetchone()[0]
        except Exception as e:
            print(f"Ошибка при подсчете работодателей: {e}")
            return 0

    # ВСПОМОГАТЕЛЬНЫЙ МЕТОД
    def _format_salary(self, salary_from: Optional[int],
                       salary_to: Optional[int],
                       currency: Optional[str]) -> str:
        """
        Форматирует информацию о зарплате для вывода.

        Аргументы:
            salary_from: Минимальная зарплата
            salary_to: Максимальная зарплата
            currency: Валюта

        Возвращает:
            str: Отформатированная строка с зарплатой
        """
        if not salary_from and not salary_to:
            return "не указана"

        currency = currency or ''

        if salary_from and salary_to:
            return f"{salary_from:,} - {salary_to:,} {currency}".replace(',', ' ')
        elif salary_from:
            return f"от {salary_from:,} {currency}".replace(',', ' ')
        elif salary_to:
            return f"до {salary_to:,} {currency}".replace(',', ' ')
        else:
            return "не указана"
