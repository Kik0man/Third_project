"""Модуль для управления базой данных PostgreSQL."""

from typing import Any

import psycopg2
from psycopg2.extensions import connection, cursor

from src.config import DB_CONFIG


class DBManager:
    """Класс для управления данными в БД PostgreSQL."""

    def __init__(self) -> None:
        """Инициализирует подключение к базе данных."""
        self.conn: connection = psycopg2.connect(**DB_CONFIG)
        self.cur: cursor = self.conn.cursor()
        print("Подключение к базе данных установлено")

    def create_tables(self) -> None:
        """Создает таблицы employers и vacancies."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS employers (
                employer_id INT PRIMARY KEY,
                employer_name VARCHAR(255) NOT NULL,
                description TEXT,
                site_url VARCHAR(255),
                open_vacancies INT,
                hh_url VARCHAR(255)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id INT PRIMARY KEY,
                employer_id INT NOT NULL REFERENCES employers(employer_id) ON DELETE CASCADE,
                vacancy_name VARCHAR(255) NOT NULL,
                salary_from INT,
                salary_to INT,
                currency VARCHAR(10),
                vacancy_url VARCHAR(255),
                requirement TEXT,
                responsibility TEXT
            );
            """,
        ]

        try:
            for query in queries:
                self.cur.execute(query)
            self.conn.commit()
            print("Таблицы успешно созданы")
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Ошибка при создании таблиц: {e}")
            raise

    def insert_employer(self, employer_data: dict[str, Any]) -> None:
        """Вставляет данные о компании в таблицу employers."""
        query = """
            INSERT INTO employers (employer_id, employer_name, description, site_url, open_vacancies, hh_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (employer_id) DO NOTHING;
        """
        values = (
            employer_data["id"],
            employer_data["name"],
            employer_data.get("description"),
            employer_data.get("site_url"),
            employer_data.get("open_vacancies"),
            employer_data.get("alternate_url"),
        )

        try:
            self.cur.execute(query, values)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Ошибка при вставке компании {employer_data.get('name')}: {e}")

    def insert_vacancy(self, vacancy_data: dict[str, Any], employer_id: Any) -> None:
        """Вставляет данные о вакансии в таблицу vacancies."""
        salary = vacancy_data.get("salary")
        salary_from = None
        salary_to = None
        currency = None

        if salary:
            salary_from = salary.get("from")
            salary_to = salary.get("to")
            currency = salary.get("currency")

        query = """
            INSERT INTO vacancies (vacancy_id, employer_id, vacancy_name,
                                  salary_from, salary_to, currency, vacancy_url,
                                  requirement, responsibility)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (vacancy_id) DO NOTHING;
        """
        values = (
            vacancy_data["id"],
            employer_id,
            vacancy_data["name"],
            salary_from,
            salary_to,
            currency,
            vacancy_data.get("alternate_url"),
            vacancy_data.get("snippet", {}).get("requirement"),
            vacancy_data.get("snippet", {}).get("responsibility"),
        )

        try:
            self.cur.execute(query, values)
            self.conn.commit()
        except psycopg2.Error as e:
            print(f"Ошибка при вставке вакансии {vacancy_data.get('name')}: {e}")

    def get_companies_and_vacancies_count(self) -> Any:
        """Возвращает список компаний и количество их вакансий."""
        query = """
            SELECT e.employer_name, COUNT(v.vacancy_id) as vacancies_count
            FROM employers e
            LEFT JOIN vacancies v USING(employer_id)
            GROUP BY e.employer_name
            ORDER BY vacancies_count DESC;
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_all_vacancies(self) -> Any:
        """Возвращает список всех вакансий с деталями."""
        query = """
            SELECT e.employer_name, v.vacancy_name, v.salary_from, v.salary_to, v.vacancy_url
            FROM vacancies v
            JOIN employers e USING(employer_id)
            ORDER BY e.employer_name, v.vacancy_name;
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_avg_salary(self) -> float:
        """Возвращает среднюю зарплату по всем вакансиям."""
        query = """
            SELECT ROUND(AVG(
                CASE
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                        THEN (salary_from + salary_to) / 2.0
                    WHEN salary_from IS NOT NULL
                        THEN salary_from
                    WHEN salary_to IS NOT NULL
                        THEN salary_to
                    ELSE NULL
                END
            )) as avg_salary
            FROM vacancies
            WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL;
        """
        self.cur.execute(query)
        result = self.cur.fetchone()[0]
        return result if result is not None else 0.0

    def get_vacancies_with_higher_salary(self) -> Any:
        """Возвращает вакансии с зарплатой выше средней."""
        avg_salary = self.get_avg_salary()

        query = """
            SELECT e.employer_name, v.vacancy_name, v.salary_from, v.salary_to, v.vacancy_url
            FROM vacancies v
            JOIN employers e USING(employer_id)
            WHERE (
                CASE
                    WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
                        THEN (v.salary_from + v.salary_to) / 2.0
                    WHEN v.salary_from IS NOT NULL
                        THEN v.salary_from
                    WHEN v.salary_to IS NOT NULL
                        THEN v.salary_to
                    ELSE 0
                END
            ) > %s
            ORDER BY (
                CASE
                    WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
                        THEN (v.salary_from + v.salary_to) / 2.0
                    WHEN v.salary_from IS NOT NULL
                        THEN v.salary_from
                    WHEN v.salary_to IS NOT NULL
                        THEN v.salary_to
                    ELSE 0
                END
            ) DESC;
        """
        self.cur.execute(query, (avg_salary,))
        return self.cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> Any:
        """Возвращает вакансии, в названии которых есть ключевое слово."""
        query = """
            SELECT e.employer_name, v.vacancy_name, v.salary_from, v.salary_to, v.vacancy_url
            FROM vacancies v
            JOIN employers e USING(employer_id)
            WHERE LOWER(v.vacancy_name) LIKE %s
            ORDER BY e.employer_name, v.vacancy_name;
        """
        self.cur.execute(query, (f"%{keyword.lower()}%",))
        return self.cur.fetchall()

    def close(self) -> None:
        """Закрывает соединение с базой данных."""
        if hasattr(self, "cur") and self.cur:
            self.cur.close()
        if hasattr(self, "conn") and self.conn:
            self.conn.close()
        print("Соединение с базой данных закрыто")

    def __del__(self) -> None:
        """Деструктор для гарантированного закрытия соединения."""
        if hasattr(self, "cur") or hasattr(self, "conn"):
            self.close()
