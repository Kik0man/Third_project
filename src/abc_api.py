"""Абстрактный базовый класс для работы с API вакансий."""

from abc import ABC, abstractmethod
from typing import Any


class BaseJobAPI(ABC):
    """Абстрактный базовый класс для API по поиску работы.

    Определяет интерфейс, который должны реализовывать все API
    для получения данных о компаниях и вакансиях.
    """

    @abstractmethod
    def get_employer_data(self, employer_id: int) -> dict[str, Any] | None:
        """Получает данные о компании по ID.

        Args:
            employer_id: ID компании

        Returns:
            Данные компании или None, если компания не найдена
        """
        pass

    @abstractmethod
    def get_vacancies_from_employer(self, employer_id: int, page: int) -> list[dict[str, Any]]:
        """Получает страницу вакансий компании.

        Args:
            employer_id: ID компании
            page: Номер страницы

        Returns:
            Список вакансий на странице
        """
        pass

    @abstractmethod
    def get_all_vacancies_for_employer(self, employer_id: int, max_pages: int) -> list[dict[str, Any]]:
        """Получает все вакансии компании.

        Args:
            employer_id: ID компании
            max_pages: Максимальное количество страниц

        Returns:
            Полный список вакансий
        """
        pass
