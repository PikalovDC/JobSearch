from src.hh_api import HH
from src.json_storage import JSONStorage


def user_interaction():
    """
    Функция для взаимодействия с пользователем через консоль.
    """
    print("=" * 50)
    print("ПАРСЕР ВАКАНСИЙ С HEADHUNTER")
    print("=" * 50)

    # Создаем хранилище
    storage = JSONStorage('vacancies.json')

    # Создаем парсер HH
    hh_parser = HH(storage)

    while True:
        print("\nДОСТУПНЫЕ ДЕЙСТВИЯ:")
        print("1. Поиск вакансий на hh.ru")
        print("2. Показать топ N вакансий по зарплате")
        print("3. Найти вакансии по ключевым словом в описании")
        print("4. Очистить базу вакансий")
        print("5. Выход")

        choice = input("\nВыберите действие (1-5): ").strip()

        if choice == '1':
            search_vacancies(hh_parser)
        elif choice == '2':
            show_top_vacancies(storage)
        elif choice == '3':
            search_by_keyword(storage)
        elif choice == '4':
            clear_vacancies(storage)
        elif choice == '5':
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


def search_vacancies(hh_parser):
    """
    Запрашивает поисковый запрос и загружает вакансии с hh.ru.
    """
    print("\nПОИСК ВАКАНСИЙ НА HH.RU")
    print("-" * 30)

    keyword = input("Введите поисковый запрос (например: 'Python разработчик'): ").strip()

    if not keyword:
        print("Поисковый запрос не может быть пустым!")
        return

    # Загружаем вакансии
    hh_parser.load_vacancies(keyword)

    # Спрашиваем, сохранять ли результаты
    save_choice = input("Сохранить результаты в базу? (да/нет): ").strip().lower()
    if save_choice in ['да', 'д', 'yes', 'y']:
        hh_parser.save_vacancies()
    else:
        print("Результаты не сохранены.")


def show_top_vacancies(storage):
    """
    Показывает топ N вакансий по зарплате.
    """
    print("\nТОП ВАКАНСИЙ ПО ЗАРПЛАТЕ")
    print("-" * 30)

    try:
        n = int(input("Сколько вакансий показать? (топ N): ").strip())

        if n <= 0:
            print("Число должно быть больше 0!")
            return

        # Получаем все вакансии и сортируем по зарплате
        all_vacancies = storage.get_vacancies()

        if not all_vacancies:
            print("В базе нет вакансий. Сначала выполните поиск.")
            return

        # Сортируем по убыванию зарплаты
        sorted_vacancies = sorted(all_vacancies, reverse=True)

        # Берем топ N
        top_vacancies = sorted_vacancies[:n]

        print(f"\nТОП-{n} ВАКАНСИЙ ПО ЗАРПЛАТЕ:")
        print("=" * 60)

        for i, vacancy in enumerate(top_vacancies, 1):
            salary_info = f"{vacancy.avg_salary} {vacancy.salary.get('currency', '')}"
            if vacancy.avg_salary == 0:
                salary_info = "не указана"

            print(f"{i}. {vacancy.title}")
            print(f"Зарплата: {salary_info}")
            print(f"Ссылка: {vacancy.url}")
            print(f"Описание: {vacancy.description[:100]}...")
            print("-" * 60)

    except ValueError:
        print("Пожалуйста, введите корректное число!")


def search_by_keyword(storage):
    """
    Ищет вакансии по ключевому слову в описании.
    """
    print("\nПОИСК ПО КЛЮЧЕВОМУ СЛОВУ В ОПИСАНИИ")
    print("-" * 40)

    keyword = input("Введите ключевое слово для поиска в описании: ").strip()

    if not keyword:
        print("Ключевое слово не может быть пустым!")
        return

    # Ищем вакансии с ключевым словом
    found_vacancies = storage.get_vacancies(keyword=keyword)

    if not found_vacancies:
        print(f"Вакансий с ключевым словом '{keyword}' не найдено.")
        return

    print(f"\nНайдено вакансий: {len(found_vacancies)}")
    print("=" * 60)

    for i, vacancy in enumerate(found_vacancies, 1):
        salary_info = f"{vacancy.avg_salary} {vacancy.salary.get('currency', '')}"
        if vacancy.avg_salary == 0:
            salary_info = "не указана"

        print(f"{i}. {vacancy.title}")
        print(f"Зарплата: {salary_info}")
        print(f"Ссылка: {vacancy.url}")
        print(f"Описание: {vacancy.description[:100]}...")
        print("-" * 60)


def clear_vacancies(storage):
    """
    Очищает базу вакансий.
    """
    print("\nОЧИСТКА БАЗЫ ВАКАНСИЙ")
    print("-" * 25)

    confirm = input("Вы уверены, что хотите очистить базу вакансий? (да/нет): ").strip().lower()

    if confirm in ['да', 'д', 'yes', 'y']:
        storage.clear()
        print("База вакансий очищена!")
    else:
        print("Очистка отменена.")


if __name__ == "__main__":
    user_interaction()
