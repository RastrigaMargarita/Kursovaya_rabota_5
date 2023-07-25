from abc import ABC, abstractmethod
import requests

import user_settings


class API_connect(ABC):
    """Абстрактный класс для всех будущих контактов с сайтами"""

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass

    @abstractmethod
    def get_id_employer(self):
        pass


class HeadHunterAPI:
    """Класс для загрузки вакансий с hh.ru"""

    def __init__(self):
        """Определяем основные настройки подключения"""

        self.__id = "hh"
        self.__url = user_settings.HH_API_URL
        self.__headers = user_settings.HH_API_Header
        self.__url_employer = user_settings.HH_API_Employer

    @property
    def id(self):
        return self.__id

    def get_id_employer(self, employer_name):
        """Получаем с сайта id компании-работодателя по наименованию
        :param employer_name: string"""

        param = {'text': employer_name}
        response = requests.get(self.__url_employer, headers=self.__headers, params=param)
        if response.status_code != 200:
            raise Exception(f"Не могу получить данные работодателя {employer_name}")
        else:

            for employer_item in response.json()["items"]:
                if employer_item['name'] == employer_name:
                    return employer_item['id']

        return None

    def get_vacancies_from_resourse(self, keyword="", employer_ids=""):
        """Функция загружает вакансии с сайта HeadHunter по ключевому слову и списку работодателей
        :param keyword: string
        :param employer_ids: string"""
        list_of_vacancies = []
        for employer_id in employer_ids:
            param = {'text': keyword, 'employer_id': employer_id[0]}
            response_employers = requests.get(self.__url, headers=self.__headers, params=param)

            if response_employers.status_code != 200:
                raise Exception(f"Не могу получить информацию о вакансиях работодателя {employer_id}")
            else:

                for vacancy_item in response_employers.json()["items"]:
                    list_of_vacancies.append([vacancy_item['id'],
                                              vacancy_item['name'],
                                              vacancy_item['url'],
                                              (vacancy_item['salary']['from'] if vacancy_item[
                                                                                     'salary'] is not None else None),
                                              (vacancy_item['salary']['to'] if vacancy_item[
                                                                                   'salary'] is not None else None),
                                              vacancy_item['snippet']['requirement'],
                                              vacancy_item['snippet']['responsibility'],
                                              vacancy_item['employer']['id']])

        return list_of_vacancies
