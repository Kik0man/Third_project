# Настройки подключения к базе данных PostgreSQL
DB_CONFIG: dict[str, str | int] = {
    "host": "localhost",
    "database": "hh_analytica",
    "user": "postgres",
    "password": "your_password",
    "port": 5432,
}

# Список интересующих компаний (нефтяные и IT компании)
EMPLOYERS: list[dict[str, str | int]] = [
    {"id": 39305, "name": "Газпром нефть"},
    {"id": 3529, "name": "Лукойл"},
    {"id": 4181, "name": "Роснефть"},
    {"id": 4181, "name": "НК Роснефть"},
    {"id": 3776, "name": "РН-Информ"},
    # IT компании
    {"id": 1740, "name": "Yandex"},
    {"id": 78638, "name": "Тинькофф"},
    {"id": 8550, "name": "SberTech"},
    {"id": 84585, "name": "Aston"},
    {"id": 41862, "name": "OZON"},
    {"id": 1057, "name": "Лаборатория Касперского"},
]
