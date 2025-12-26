import os

from dotenv import load_dotenv

"""
Конфигурация приложения
"""


# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройки базы данных
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'hh_vacancies'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD') or 'simple123'
}

# Список компаний для сбора данных
COMPANIES = {
    1740: "Яндекс",
    3529: "Сбер",
    15478: "VK",
    2180: "Ozon",
    733: "Лаборатория Касперского",
    67611: "Тинькофф",
    1122462: "Skyeng",
    3776: "МТС",
    87021: "WILDBERRIES",
    4181: "2ГИС"
}
