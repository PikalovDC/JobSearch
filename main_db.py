import sys
from src.database import create_database, create_tables
from src.db_manager import DBManager
from src.hh_api import HH
from src.config import COMPANIES
import time

"""
ОСНОВНОЙ СКРИПТ ПРОГРАММЫ для взаимодействия с БД
"""

def load_employers_data():
    """Загружает данные о работодателях и вакансиях с HH.ru"""
    print("=" * 60)
    print("ЗАГРУЗКА ДАННЫХ С HH.RU В БАЗУ ДАННЫХ")
    print("=" * 60)

    print("\nПодготовка базы данных...")
    # ВЫЗОВ КОДА СОЗДАНИЯ БД - соответствует требованию
    create_database()
    # ВЫЗОВ КОДА СОЗДАНИЯ ТАБЛИЦ - соответствует требованию
    create_tables()

    print("Инициализация компонентов...")
    hh_api = HH(file_worker=None)
    db_manager = DBManager()

    total_vacancies = 0
    successful_employers = 0

    for employer_id, company_name in COMPANIES.items():
        print(f"\n{'=' * 40}")
        print(f"Загрузка данных: {company_name} (ID: {employer_id})")
        print(f"{'=' * 40}")

        try:
            # 1. Получаем данные о работодателе
            print(f"Получение информации о работодателе...")
            employer_data = hh_api.get_employer(employer_id)

            if not employer_data:
                print(f"Не удалось получить данные о работодателе {company_name}")
                continue

            # 2. Сохраняем работодателя в БД
            print(f"Сохранение работодателя в БД...")
            if db_manager.insert_employer(employer_data):
                print(f"Работодатель сохранен: {employer_data.get('name', company_name)}")
            else:
                print(f"Ошибка сохранения работодателя")
                continue

            # 3. Получаем вакансии работодателя
            print(f"Получение вакансий...")
            vacancies = hh_api.get_employer_vacancies(employer_id)

            if not vacancies:
                print(f"У работодателя нет открытых вакансий")
                continue

            # 4. Сохраняем вакансии в БД
            print(f"Сохранение вакансий в БД...")
            saved_vacancies = 0

            for vacancy in vacancies:
                if db_manager.insert_vacancy(vacancy):
                    saved_vacancies += 1

            total_vacancies += saved_vacancies
            successful_employers += 1

            print(f"Сохранено вакансий: {saved_vacancies} из {len(vacancies)}")

            time.sleep(0.5)

        except Exception as e:
            print(f"Критическая ошибка при обработке {company_name}: {e}")
            continue

    print(f"\n{'=' * 60}")
    print("ИТОГОВАЯ СТАТИСТИКА")
    print(f"{'=' * 60}")
    print(f"Успешно обработано работодателей: {successful_employers} из {len(COMPANIES)}")
    print(f"Всего сохранено вакансий: {total_vacancies}")

    db_manager.close()
    print(f"\nЗагрузка данных завершена успешно!")


def show_menu():
    """Отображает главное меню"""
    print("\n" + "=" * 60)
    print("МЕНЮ РАБОТЫ С БАЗОЙ ДАННЫХ")
    print("=" * 60)
    print("\nДОСТУПНЫЕ ДЕЙСТВИЯ:")
    print("1. Показать компании и количество вакансий")
    print("2. Показать все вакансии")
    print("3. Показать среднюю зарплату")
    print("4. Показать вакансии с зарплатой выше средней")
    print("5. Найти вакансии по ключевому слову")
    print("6. Показать статистику")
    print("7. Загрузить/обновить данные с HH.ru")
    print("8. Выход")


def show_companies_and_vacancies(db_manager):
    """Показывает список компаний и количество вакансий"""
    print("\nКОМПАНИИ И КОЛИЧЕСТВО ВАКАНСИЙ:")
    print("-" * 50)

    companies = db_manager.get_companies_and_vacancies_count()

    if not companies:
        print("В базе данных нет компаний")
        return

    print(f"{'№':<3} {'Компания':<30} {'Вакансий':>10}")
    print("-" * 50)

    for i, company in enumerate(companies, 1):
        print(f"{i:<3} {company['company'][:30]:<30} {company['vacancies_count']:>10}")

    print(f"\nВсего компаний: {len(companies)}")


def show_all_vacancies(db_manager):
    """Показывает все вакансии"""
    print("\nВСЕ ВАКАНСИИ:")
    print("-" * 80)

    vacancies = db_manager.get_all_vacancies()

    if not vacancies:
        print("В базе данных нет вакансий")
        return

    print(f"{'№':<3} {'Компания':<20} {'Вакансия':<30} {'Зарплата':<20}")
    print("-" * 80)

    for i, vacancy in enumerate(vacancies[:20], 1):
        company = vacancy['company'][:20] if vacancy['company'] else "Не указано"
        position = vacancy['vacancy'][:30] if vacancy['vacancy'] else "Не указано"
        salary = vacancy['salary'][:20] if vacancy['salary'] else "Не указано"

        print(f"{i:<3} {company:<20} {position:<30} {salary:<20}")

    if len(vacancies) > 20:
        print(f"\nПоказано 20 из {len(vacancies)} вакансий")

    print(f"\nВсего вакансий: {len(vacancies)}")


def work_with_database():
    """Основная функция работы с базой данных"""
    print("\nЗапуск режима работы с базой данных...")

    try:
        # Подключаемся к базе данных
        db_manager = DBManager()

        while True:
            show_menu()

            choice = input("\nВыберите действие (1-8): ").strip()

            if choice == '1':
                show_companies_and_vacancies(db_manager)
            elif choice == '2':
                show_all_vacancies(db_manager)
            elif choice == '3':
                avg_salary = db_manager.get_avg_salary()
                print(f"\nСРЕДНЯЯ ЗАРПЛАТА: {avg_salary:,.2f} руб.".replace(',', ' '))
            elif choice == '4':
                vacancies = db_manager.get_vacancies_with_higher_salary()
                print(f"\nВАКАНСИЙ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ: {len(vacancies)}")
                for i, v in enumerate(vacancies[:10], 1):
                    print(f"{i}. {v['company']} - {v['vacancy']}: {v['salary']}")
            elif choice == '5':
                keyword = input("Введите ключевое слово: ").strip()
                if keyword:
                    vacancies = db_manager.get_vacancies_with_keyword(keyword)
                    print(f"\nНайдено вакансий: {len(vacancies)}")
                    for i, v in enumerate(vacancies[:10], 1):
                        print(f"{i}. {v['company']} - {v['vacancy']}")
            elif choice == '6':
                print(f"\nСТАТИСТИКА БАЗЫ ДАННЫХ:")
                print(f"Компаний: {db_manager.get_employers_count()}")
                print(f"Вакансий: {db_manager.get_vacancies_count()}")
                print(f"Средняя зарплата: {db_manager.get_avg_salary():,.2f} руб.".replace(',', ' '))
            elif choice == '7':
                db_manager.close()
                print("\nПереход к загрузке данных...")
                load_employers_data()
                db_manager = DBManager()  # Переподключаемся
            elif choice == '8':
                print("\nДо свидания!")
                break
            else:
                print("Неверный выбор. Пожалуйста, введите число от 1 до 8.")

            input("\nНажмите Enter для продолжения...")

        # Закрываем соединение с БД
        db_manager.close()

    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")


def main():
    """
    ОСНОВНАЯ ФУНКЦИЯ ПРОГРАММЫ - соответствует требованиям:
    1. Вызывает код создания БД
    2. Вызывает код создания таблиц
    3. Предоставляет единый интерфейс
    """
    print("=" * 60)
    print("ПАРСЕР ВАКАНСИЙ С HEADHUNTER")
    print("=" * 60)

    print("\nВыберите режим работы:")
    print("1.ЗАГРУЗИТЬ данные с HH.ru (первый запуск)")
    print("2.РАБОТАТЬ с базой данных")
    print("3.ВЫХОД")

    choice = input("\nВаш выбор (1-3): ").strip()

    if choice == '1':
        # Загружаем данные
        load_employers_data()
        # После загрузки переходим к работе с БД
        print("\nДанные загружены. Переход к работе с базой...")
        work_with_database()
    elif choice == '2':
        # Работаем с существующей БД
        work_with_database()
    elif choice == '3':
        print("До свидания!")
        sys.exit(0)
    else:
        print("Неверный выбор")

if __name__ == "__main__":
    main()