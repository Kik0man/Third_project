"""Пакет с модулями для сбора и анализа вакансий с hh.ru."""

from src.abc_api import BaseJobAPI
from src.abc_storage import BaseStorage
from src.api import HeadHunterAPI
from src.db_manager import DBManager

__all__ = [
    "BaseJobAPI",
    "BaseStorage",
    "HeadHunterAPI",
    "DBManager",
]
