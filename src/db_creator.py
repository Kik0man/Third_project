"""Модуль для создания базы данных."""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.config import DB_CONFIG


def create_database() -> None:
    """Создает базу данных, если она не существует."""
    # Подключаемся к стандартной базе postgres
    conn_params = DB_CONFIG.copy()
    db_name = conn_params.pop("database")  # Убираем название БД из параметров

    try:
        # Подключаемся к postgres
        conn = psycopg2.connect(
            database="postgres",
            user=conn_params["user"],
            password=conn_params["password"],
            host=conn_params["host"],
            port=conn_params.get("port", 5432),
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Проверяем, существует ли база данных
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone()

        if not exists:
            print(f"Создание базы данных {db_name}...")
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"✓ База данных {db_name} успешно создана")
        else:
            print(f"✓ База данных {db_name} уже существует")

        cur.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"✗ Ошибка при создании базы данных: {e}")
        raise


if __name__ == "__main__":
    create_database()
