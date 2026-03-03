"""Модуль для взаимодействия с API HeadHunter."""

import time
from typing import Any

import requests


class HeadHunterAPI:
    """Класс для получения данных с публичного API hh.ru."""

    BASE_URL: str = "https://api.hh.ru"

    @staticmethod
    def get_employer_data(employer_id: Any) -> Any:
        """Получает данные о компании по её идентификатору.

        Args:
            employer_id: ID компании на hh.ru

        Returns:
            dict с данными компании или None, если компания не найдена
        """
        url = f"{HeadHunterAPI.BASE_URL}/employers/{employer_id}"

        try:
            response = requests.get(url)

            if response.status_code == 404:
                print(f"  ⚠️ Компания с ID {employer_id} не найдена на hh.ru")
                return None

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"  ❌ Ошибка при получении данных компании {employer_id}: {e}")
            return None

    @staticmethod
    def get_vacancies_from_employer(employer_id: int, page: int = 0) -> Any:
        """Получает список вакансий для конкретной компании с указанной страницы.

        Args:
            employer_id: ID компании на hh.ru
            page: Номер страницы (начиная с 0)

        Returns:
            Список вакансий с текущей страницы
        """
        url = f"{HeadHunterAPI.BASE_URL}/vacancies"
        params = {"employer_id": employer_id, "page": page, "per_page": 20, "area": 113}  # Максимум 100  # Россия

        try:
            response = requests.get(url, params=params)

            if response.status_code == 404:
                return []

            response.raise_for_status()
            data = response.json()
            return data.get("items", [])

        except requests.RequestException as e:
            print(f"  ❌ Ошибка при получении вакансий компании {employer_id}: {e}")
            return []

    def get_all_vacancies_for_employer(self, employer_id: Any, max_pages: int = 5) -> Any:
        """Получает ВСЕ вакансии компании с учетом пагинации.

        Args:
            employer_id: ID компании на hh.ru
            max_pages: Максимальное количество страниц для загрузки

        Returns:
            Полный список всех вакансий компании
        """
        all_vacancies = []

        for page in range(max_pages):
            # Используем существующий метод для получения страницы
            vacancies = self.get_vacancies_from_employer(employer_id, page)

            if not vacancies:  # Если вакансий больше нет
                break

            all_vacancies.extend(vacancies)
            print(f"    Загружена страница {page + 1}: {len(vacancies)} вакансий")

            # Задержка чтобы не нагружать API
            time.sleep(0.3)

            # Если получили меньше, чем per_page, значит это последняя страница
            if len(vacancies) < 20:
                break

        return all_vacancies

    def search_employers(self, query: Any) -> Any:
        """Поиск компаний по названию.

        Args:
            query: Название компании для поиска

        Returns:
            Список найденных компаний
        """
        url = f"{HeadHunterAPI.BASE_URL}/employers"
        params = {"text": query, "area": 113, "per_page": 10}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except requests.RequestException as e:
            print(f"Ошибка при поиске компаний: {e}")
            return []
