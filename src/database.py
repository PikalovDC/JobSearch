import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.config import DB_CONFIG

"""
Создание и управление базой данных PostgreSQL
"""


def create_database():
    """
    Создает базу данных если она не существует
    """
    # Подключаемся к серверу PostgreSQL без выбора базы данных
    conn_config = DB_CONFIG.copy()
    database_name = conn_config.pop('database')  # Убираем имя БД из настроек

    try:
        # Подключаемся к серверу PostgreSQL
        conn = psycopg2.connect(**conn_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Проверяем существование базы данных
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database_name}'")
        exists = cur.fetchone()

        if not exists:
            # Создаем базу данных
            cur.execute(f"CREATE DATABASE {database_name}")
            print(f"База данных '{database_name}' создана")
        else:
            print(f"База данных '{database_name}' уже существует")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        raise


def create_tables():
    """
    Создает таблицы в базе данных
    """
    try:
        # Подключаемся к созданной базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Создаем таблицу работодателей
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url VARCHAR(255),
                description TEXT,
                open_vacancies INTEGER
            )
        """)

        # Создаем таблицу вакансий
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY,
                employer_id INTEGER REFERENCES employers(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                currency VARCHAR(10),
                url VARCHAR(255) NOT NULL,
                description TEXT,
                requirements TEXT,   
                experience VARCHAR(100),
                employment VARCHAR(100)
            )
        """)

        # Создаем индекс для быстрого поиска по зарплате
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_salary_from ON vacancies(salary_from)
        """)

        # Создаем индекс для быстрого поиска по работодателю
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_employer_id ON vacancies(employer_id)
        """)

        conn.commit()
        print("Таблицы созданы успешно")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
        raise


def drop_tables():
    """
    Удаляет таблицы из базы данных (для тестов)
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS vacancies CASCADE")
        cur.execute("DROP TABLE IF EXISTS employers CASCADE")

        conn.commit()
        print("Таблицы удалены")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Ошибка при удалении таблиц: {e}")
        raise


if __name__ == "__main__":
    # Для тестирования: создаем БД и таблицы
    create_database()
    create_tables()
