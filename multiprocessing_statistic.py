from multiprocessing import Pool
import math
import os
import csv


currency_to_rub = {"AZN": 35.68,
                   "BYR": 23.91,
                   "EUR": 59.90,
                   "GEL": 21.74,
                   "KGS": 0.76,
                   "KZT": 0.13,
                   "RUR": 1,
                   "UAH": 1.64,
                   "USD": 60.66,
                   "UZS": 0.0055}


class DataSet:
    """Класс для хранения и обработки данных и статистики.

        Attributes:
            file_name (str): Имя исходного файла с данными
            vacancies_objects (list[Vacancy]): Лист вакансий со всеми заполненными значениями
            statistic_year (list)): Статистика по вакансиям
    """

    def __init__(self, file_name, vacancies_objects):
        """Инициализирует объект DataSet.

            Args:
                file_name (str): Имя исходного файла с данными
                vacancies_objects (list): Лист вакансий для обработки
        """
        self.file_name = file_name
        self.vacancies_objects = [Vacancy(row) for row in vacancies_objects if None not in row and '' not in row]
        self.statistic_year = []

    def calculate_year_statistics(self, profession_name):
        """Вычисляет статистику по вакансиям: динамика уровня зарплат по годам, динамика количества вакансий по
        годам, динамика уровня зарплат по годам для выбранной профессии, динамика количества вакансий по годам для
        выбранной профессии.

            Args:
                profession_name(str): Название професии для сбора более конкретной статистики по данной професии

            Returns:
                list: Собранная сатистика: динамика уровня зарплат по годам, динамика количества
                 вакансий по годам, динамика уровня зарплат по годам для выбранной профессии, динамика количества вакансий
                 по годам для выбранной профессии.
        """
        salary_by_years = 0
        salary_by_years_profession = 0
        number_vac_by_years = 0
        number_profession_by_years = 0
        year = self.vacancies_objects[0].published_at[0]
        for vacancy in self.vacancies_objects:
            number_vac_by_years = number_vac_by_years + 1
            salary_by_years = salary_by_years + vacancy.salary.convert_to_rubles()
            if profession_name in vacancy.name:
                salary_by_years_profession = salary_by_years_profession + vacancy.salary.convert_to_rubles()
                number_profession_by_years = number_profession_by_years + 1

        salary_by_years = math.floor(salary_by_years / number_vac_by_years)
        salary_by_years_profession = math.floor(salary_by_years_profession / number_profession_by_years)

        self.statistic_year = [year, salary_by_years, number_vac_by_years, salary_by_years_profession,
                          number_profession_by_years]

        return self.statistic_year


class Vacancy:
    """Класс для представления вакансии.

        Attributes:
            name (str): Название профессии
            salary (Salary): Оклад
            area_name (): Название региона
            published_at (): Дата публикации вакансии
    """

    def __init__(self, vacancy):
        """Устанавливает все необходимые атрибуты для объекта Vacancy.

            Args:
                vacancy (list): Лист данных о вакансии состоящий из: название профессии, оклад, название региона, дата
            публикации вакансии.
        """
        self.name = vacancy[0].replace('\xa0', '\x20')
        self.salary = Salary([vacancy[1], vacancy[2], vacancy[3]])
        self.area_name = vacancy[4]
        self.published_at = self.parse_date_simple(vacancy[5])

    @staticmethod
    def parse_date_simple(date):
        """Преобразует дату из одной строки в лист по значениям: год, месяц, день, часы, минуты, секунды, часовой пояс

            Args:
                date (str): Дата (в формате "%Y-%m-%dT%H:%M:%S%z") для разбиения на значения
            Returns:
                list: Лист со значениями даты: год, месяц, день, часы, минуты, секунды, часовой пояс
        """
        date = date.replace('T', '-').replace(':', '-').replace('+', '-')
        year, month, day, hour, minute, second, timezone = date.split('-')
        return year, month, day, hour, minute, second, timezone


class Salary:
    """Класс для представления оклада.

        Attributes:
            salary_from (int): Нижняя граница оклада
            salary_to (int): Верхняя граница оклада
            salary_currency (str): Валюта оклада
    """

    def __init__(self, salary):
        """Инициализирует объект Salary.

            Args:
                salary (list): Информация об окладе: нижняя граница оклада, верхняя граница оклада, валюта оклада
        """
        self.salary_from = int(float(salary[0]))
        self.salary_to = int(float(salary[1]))
        self.salary_currency = salary[2]

    def convert_to_rubles(self):
        """Вычисляет среднее значение зарплаты и конвертирует в рубли, при помощи словоря - currency_to_rub.

            Returns:
                float: Cреднее значение зарплаты в рублях
        """
        return ((float(self.salary_from) + float(self.salary_to)) / 2) * float(currency_to_rub[self.salary_currency])


def csv_reader(file_name):
    """Открывает и читает необходимый файл, а также возвращяет полученный результат.

        Args:
           file_name (str): Название файла для чтения

        Returns:
            DataSet, list: Полученные данные из прочитанного файла, строчка с названиями столбцов
    """
    with open(file_name, encoding="utf-8-sig") as file:
        reader = list(csv.reader(file))
        try:
            list_naming = reader.pop(0)
        except Exception:
            list_naming = None
        data_set = DataSet(file_name, reader)
        file.close()
        return data_set, list_naming


def get_statistic(file_name, profession_name):
    """Получает данные из файла, вычисляет статистику и возвращяет её.

        Args:
            file_name (str): Название файла с данными для сбора статистики
            profession_name (str): Название профессии для сбора статистики по профессии
        Returns:
            list: Вычисленная статистика
    """
    data_set, list_naming = csv_reader(file_name)
    if list_naming is None:
        print('Пустой файл')
    elif len(data_set.vacancies_objects) == 0:
        print('Нет данных')
    else:
        return data_set.calculate_year_statistics(profession_name)


def print_statistic(statistic_year):
    """Печатает статистику: динамика уровня зарплат по годам, динамика количества вакансий по годам,
        динамика уровня зарплат по годам для выбранной профессии, динамика количества вакансий по годам для выбранной
        профессии.
    """
    salary_by_years = {}
    number_vac_by_years = {}
    salary_by_years_profession = {}
    number_profession_by_years = {}
    for stat in statistic_year:
        year = stat[0]
        salary_by_years[year] = stat[1]
        number_vac_by_years[year] = stat[2]
        salary_by_years_profession[year] = stat[3]
        number_profession_by_years[year] = stat[4]

    print(f'Динамика уровня зарплат по годам: {salary_by_years}')
    print(f'Динамика количества вакансий по годам: {number_vac_by_years}')
    print(f'Динамика уровня зарплат по годам для выбранной профессии: {salary_by_years_profession}')
    print(f'Динамика количества вакансий по годам для выбранной профессии: {number_profession_by_years}')


def main():
    name_file = input('Введите название файла: ')
    profession_name = input('Введите название профессии: ')
    tuples_files_profession = [(os.getcwd() + f'\\{name_file}\\' + file, profession_name) for file in os.listdir(os.getcwd() + f'\\{name_file}\\')]
    with Pool(16) as p:
        statistic_year = p.starmap(get_statistic, tuples_files_profession)
    print_statistic(statistic_year)


if __name__ == '__main__':
    main()
