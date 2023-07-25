from db_manager import DBManager
from source_api import HeadHunterAPI


def main():
    """Функция иницилизирует все что нужно для работы и стартует взаимодействие с пользователем"""

    # Платформы будем расширять со временем, по-этому будем складывать их в список.
    platforms = {HeadHunterAPI()}
    # создаем менеджер для работы с базой данной и передаем в него платформы
    dbmanager = DBManager(platforms)
    # запускаем взаимодействие с пользователем
    user_interaction(dbmanager)


def user_interaction(dbmanager):
    """Функция для взаимодействия с пользователем"""
    user_choise = ""
    while user_choise != '5':
        user_choise = input("""Введите действие: 
        0 - Обновить данные с сайта,
        1 - Посмотреть статистику, 
        2 - Посмотреть все вакансии, 
        3 - Отобрать вакансии по ключевому слову, 
        4 - Отобрать только хорошие вакансии, 
        5 - прекратить работу
""")
        if user_choise == '0':

            dbmanager.download_vacancies()
            print("Загрузка завершена")

        elif user_choise == '1':
            print(dbmanager.get_statistic())

        elif user_choise == '2':
            print(dbmanager.get_all_vacancies())

        elif user_choise == '3':
            word = input("Введите слово для поиска: ")
            print(dbmanager.get_vacancies_with_keyword(word))

        elif user_choise == '4':
            print(dbmanager.get_vacancies_with_higher_salary())

        elif user_choise == '5':
            print("Пока, приходи еще.")


if __name__ == "__main__":
    main()
