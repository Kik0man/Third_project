"""Главный модуль программы для анализа вакансий с hh.ru."""

import sys
from typing import NoReturn

from src.api import HeadHunterAPI
from src.config import EMPLOYERS
from src.db_creator import create_database  # новый импорт
from src.db_manager import DBManager


def main() -> None:
    """Главная функция программы."""
    print("🚀 Программа анализа вакансий с hh.ru")
    print("Автоматический сбор данных о нефтяных и IT компаниях\n")

    try:
        # Сначала создаем базу данных, если её нет
        print("Проверка наличия базы данных...")
        create_database()
        print()

        # Теперь подключаемся к созданной БД
        db_manager = DBManager()
        db_manager.create_tables()

        hh_api = HeadHunterAPI()

        # Загружаем данные
        print("\nНачинаем загрузку данных с hh.ru...")
        for employer in EMPLOYERS:
            emp_id = employer["id"]
            emp_name = employer["name"]

            print(f"\nОбработка компании: {emp_name}")

            # Получаем данные о компании
            emp_data = hh_api.get_employer_data(emp_id)
            db_manager.insert_employer(emp_data)

            # Получаем вакансии
            vacancies = hh_api.get_all_vacancies_for_employer(emp_id)
            for vacancy in vacancies:
                db_manager.insert_vacancy(vacancy, emp_id)

            print(f"  Загружено вакансий: {len(vacancies)}")

        print("\n✓ Данные успешно загружены!")

        # Запускаем интерактивный режим
        run_interactive_mode(db_manager)

    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        if "db_manager" in locals():
            db_manager.close()


def print_menu() -> None:
    """Выводит меню доступных действий."""
    print("\n" + "=" * 50)
    print("МЕНЮ АНАЛИЗА ВАКАНСИЙ")
    print("=" * 50)
    print("1. Список компаний и количество вакансий")
    print("2. Список всех вакансий")
    print("3. Средняя зарплата по всем вакансиям")
    print("4. Вакансии с зарплатой выше средней")
    print("5. Поиск вакансий по ключевому слову")
    print("0. Выход")
    print("-" * 50)


def run_interactive_mode(db_manager: DBManager) -> NoReturn:
    """Запускает интерактивный режим работы с пользователем."""
    while True:
        print_menu()

        try:
            choice = input("Выберите действие (0-5): ").strip()

            if choice == "1":
                print("\n📊 КОМПАНИИ И КОЛИЧЕСТВО ВАКАНСИЙ:")
                results = db_manager.get_companies_and_vacancies_count()
                if results:
                    for name, count in results:
                        print(f"  • {name}: {count} вакансий")
                else:
                    print("  Данные отсутствуют")

            elif choice == "2":
                print("\n📋 ВСЕ ВАКАНСИИ (первые 20):")
                results = db_manager.get_all_vacancies()
                if results:
                    for i, (company, vacancy, sal_from, sal_to, url) in enumerate(results[:20], 1):
                        salary = "не указана"
                        if sal_from and sal_to:
                            salary = f"{sal_from} - {sal_to}"
                        elif sal_from:
                            salary = f"от {sal_from}"
                        elif sal_to:
                            salary = f"до {sal_to}"
                        print(f"  {i}. {company} — {vacancy}")
                        print(f"     Зарплата: {salary}")
                        print(f"     Ссылка: {url}\n")
                else:
                    print("  Вакансии не найдены")

            elif choice == "3":
                print("\n💰 СРЕДНЯЯ ЗАРПЛАТА:")
                avg_salary = db_manager.get_avg_salary()
                if avg_salary > 0:
                    print(f"  Средняя зарплата по всем вакансиям: {avg_salary:,.0f} руб.")
                else:
                    print("  Данные о зарплатах отсутствуют")

            elif choice == "4":
                print("\n⭐ ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ:")
                results = db_manager.get_vacancies_with_higher_salary()
                if results:
                    for company, vacancy, sal_from, sal_to, url in results:
                        salary = "не указана"
                        if sal_from and sal_to:
                            salary = f"{sal_from} - {sal_to}"
                        elif sal_from:
                            salary = f"от {sal_from}"
                        elif sal_to:
                            salary = f"до {sal_to}"
                        print(f"  • {company} — {vacancy}")
                        print(f"    Зарплата: {salary}")
                        print(f"    Ссылка: {url}\n")
                else:
                    print("  Вакансии с зарплатой выше средней не найдены")

            elif choice == "5":
                print("\n🔍 ПОИСК ВАКАНСИЙ ПО КЛЮЧЕВОМУ СЛОВУ:")
                keyword = input("  Введите ключевое слово: ").strip()
                if keyword:
                    results = db_manager.get_vacancies_with_keyword(keyword)
                    print(f"\n  Найдено вакансий: {len(results)}")
                    if results:
                        for company, vacancy, sal_from, sal_to, url in results:
                            print(f"  • {company} — {vacancy}")
                            print(f"    Ссылка: {url}")
                    else:
                        print("  Ничего не найдено")
                else:
                    print("  Ключевое слово не может быть пустым")

            elif choice == "0":
                print("\n👋 Завершение работы программы...")
                break

            else:
                print("\n❌ Неверный ввод. Пожалуйста, выберите число от 0 до 5.")

        except KeyboardInterrupt:
            print("\n\n👋 Работа программы прервана пользователем")
            break
        except Exception as e:
            print(f"\n❌ Произошла ошибка: {e}")

    sys.exit(0)


if __name__ == "__main__":
    main()
