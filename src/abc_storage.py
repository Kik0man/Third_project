"""Абстрактный базовый класс для хранилища данных."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseStorage(ABC):
    """Абстрактный базовый класс для хранилища данных.

    Определяет интерфейс для работы с базой данных,
    позволяя легко заменить PostgreSQL на другую БД.
    """

    @abstractmethod
    def create_tables(self) -> None:
        """Создает необходимые таблицы."""
        pass

    @abstractmethod
    def insert_employer(self, employer_data: dict[str, Any]) -> None:
        """Сохраняет данные о компании."""
        pass

    @abstractmethod
    def insert_vacancy(self, vacancy_data: dict[str, Any], employer_id: int) -> None:
        """Сохраняет данные о вакансии."""
        pass

    @abstractmethod
    def get_companies_and_vacancies_count(self) -> list[tuple[str, int]]:
        """Возвращает список компаний и количество их вакансий."""
        pass

    @abstractmethod
    def get_all_vacancies(self) -> list[tuple[str, str, Optional[int], Optional[int], str]]:
        """Возвращает список всех вакансий."""
        pass

    @abstractmethod
    def get_avg_salary(self) -> float:
        """Возвращает среднюю зарплату."""
        pass

    @abstractmethod
    def get_vacancies_with_higher_salary(self) -> list[tuple[str, str, Optional[int], Optional[int], str]]:
        """Возвращает вакансии с зарплатой выше средней."""
        pass

    @abstractmethod
    def get_vacancies_with_keyword(self, keyword: str) -> list[tuple[str, str, Optional[int], Optional[int], str]]:
        """Возвращает вакансии по ключевому слову."""
        pass
