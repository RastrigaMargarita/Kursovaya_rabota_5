import math
import psycopg2
import config
import user_settings


class DBManager:
    """Класс для работы с базой данных"""

    def __init__(self, list_of_api):
        self.list_of_API = list_of_api
        self.check_db_existing()

    def check_db_existing(self) -> None:
        """Создает таблицы базы данных если их нет и заполяет таблицу работодателей по данным user_settings файла"""

        with psycopg2.connect(config.SQL_CONNECTION + " dbname=" + user_settings.DB_NAME) as connection:
            with connection.cursor() as cursor:
                cursor.execute('''CREATE TABLE IF NOT EXISTS employers
                                (
                                employer_id varchar(10) PRIMARY KEY,
                                employer_name varchar(100) NOT NULL,
                                api_id varchar(50) NOT NULL
                                );''')

                cursor.execute('''SELECT * FROM employers limit 1''')
                if cursor.rowcount == 0:
                    for employer in user_settings.LIST_OF_EMPLOYERS:
                        for item_of_API in self.list_of_API:
                            employer_id = item_of_API.get_id_employer(employer)
                            if employer_id is not None:
                                cursor.execute('INSERT INTO employers VALUES (%s,%s,%s)',
                                               (employer_id, employer, item_of_API.id))

                cursor.execute('''CREATE TABLE IF NOT EXISTS vacancies
                (
                    vacancy_id varchar(50) PRIMARY KEY,
                    title varchar(100),
                    ref varchar(100),
                    salary_min integer,
                    salary_max integer,
                    requirements text,
                    responsibility text,
                    employer_id varchar(10) REFERENCES employers(employer_id)
        
                )''')
                connection.commit()

    def download_vacancies(self):
        """Скачивает вакансии с ресурса и кладет в базу данных"""
        for API_item in self.list_of_API:

            with psycopg2.connect(config.SQL_CONNECTION + " dbname=" + user_settings.DB_NAME) as connection:
                with connection.cursor() as cursor:
                    cursor.execute('TRUNCATE vacancies')
                    cursor.execute('SELECT employer_id FROM employers WHERE api_id = %s', (API_item.id,))
                    list_of_employers = cursor.fetchall()

                    list_of_vacancies = API_item.get_vacancies_from_resourse(employer_ids=list_of_employers)
                    for vacancy in list_of_vacancies:
                        cursor.execute('''INSERT INTO vacancies VALUES (%s, %s, %s, %s, %s, %s, %s, %s);''',
                                       (vacancy[0], vacancy[1], vacancy[2], vacancy[3], vacancy[4], vacancy[5],
                                        vacancy[6], vacancy[7]))
                    connection.commit()

    @staticmethod
    def get_all_vacancies(where_block=""):
        """Возвращает все вакансии из базы"""
        with psycopg2.connect(config.SQL_CONNECTION + " dbname=" + user_settings.DB_NAME) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f'''SELECT vacancies.*, employers.employer_name FROM vacancies 
                                JOIN employers 
                                USING (employer_id)
                                {where_block}''')
                return "\n".join((" ".join(str(field) for field in row)) for row in cursor.fetchall())

    @staticmethod
    def get_companies_and_vacancies_count():
        with psycopg2.connect(config.SQL_CONNECTION + " dbname=" + user_settings.DB_NAME) as connection:
            with connection.cursor() as cursor:
                cursor.execute('''SELECT count(vacancies.vacancy_id) , employers.employer_name  FROM vacancies 
                                JOIN employers 
                                USING (employer_id) 
                                GROUP BY employers.employer_name''')

                return "\n".join(f"Компания: {row[1]}, вакансий: {row[0]} " for row in cursor.fetchall())

    @staticmethod
    def get_avg_salary():
        with psycopg2.connect(config.SQL_CONNECTION + " dbname=" + user_settings.DB_NAME) as connection:
            with connection.cursor() as cursor:
                cursor.execute('''SELECT AVG((salary_max + salary_min)/2) AS average FROM vacancies 
                                  WHERE salary_max > 0''')

                return math.floor(cursor.fetchall()[0][0])

    def get_statistic(self):
        """Формирует строку статистики и возвращает ее для вывода на экран"""
        companies_and_vacancies = self.get_companies_and_vacancies_count()
        return f"Всего вакансий: \n {companies_and_vacancies} \nсредняя зарплата: {self.get_avg_salary():_} руб."

    def get_vacancies_with_higher_salary(self):
        """Возвращает список вакансий с зарплатой выше средней."""
        return self.get_all_vacancies(where_block=f'WHERE (salary_max + salary_min)/2 >= {self.get_avg_salary()}')

    def get_vacancies_with_keyword(self, word):
        return self.get_all_vacancies(where_block=f'WHERE vacancies.title LIKE \'%{word}%\'')
