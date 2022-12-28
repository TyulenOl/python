from multiprocessing import Pool
import concurrent.futures as pool
import math
import os
import csv

import numpy as np
import pandas as pd


currencies_df = pd.read_csv('currencies.csv')


class DataSet:
    """Класс для хранения и обработки данных и статистики.

        Attributes:
            file_name (str): Имя исходного файла с данными
            vacancies_objects (list[Vacancy]): Лист вакансий со всеми заполненными значениями
            statistic_year (list)): Статистика по вакансиям
    """

    def __init__(self, file_name=None, vacancies_objects=None):
        """Инициализирует объект DataSet.

            Args:
                file_name (str): Имя исходного файла с данными
                vacancies_objects (list): Лист вакансий для обработки
        """
        self.file_name = file_name
        if vacancies_objects is not None:
            self.vacancies_objects = [Vacancy(row) for row in vacancies_objects if None not in row]
        self.statistic_year = []
        self.statistic_city = []

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
            if vacancy.salary.salary is not None and not pd.isnull(vacancy.salary.salary):
                number_vac_by_years = number_vac_by_years + 1
                salary_by_years = salary_by_years + vacancy.salary.salary
                if profession_name in vacancy.name:
                    salary_by_years_profession = salary_by_years_profession + vacancy.salary.salary
                    number_profession_by_years = number_profession_by_years + 1

        salary_by_years = math.floor(salary_by_years / number_vac_by_years)
        salary_by_years_profession = math.floor(salary_by_years_profession / number_profession_by_years)

        self.statistic_year = [year, salary_by_years, number_vac_by_years, salary_by_years_profession,
                               number_profession_by_years]

        return self.statistic_year

    def calculate_city_statistics(self, data):
        sum_salary_by_city = {}
        salary_by_city = {}
        number_vac_by_city = {}
        percentage_vac_by_city = {}
        for vacancy in data:
            if vacancy[1] is not None and not pd.isnull(vacancy[1]):
                city = vacancy[2]
                number_vac_by_city[city] = number_vac_by_city.get(city, 0) + 1
                sum_salary_by_city[city] = sum_salary_by_city.get(city, 0) + vacancy[1]

        for city in number_vac_by_city.keys():
            proportion_vacancy = number_vac_by_city.get(city) / len(data)
            if proportion_vacancy >= 0.01:
                percentage_vac_by_city[city] = round(proportion_vacancy, 4)
                salary_by_city[city] = math.floor(sum_salary_by_city[city] / number_vac_by_city.get(city))

        sorted_salary_by_city = dict(sorted(salary_by_city.items(), key=lambda x: -x[1])[:10])
        sorted_percentage_vac_by_city = dict(sorted(percentage_vac_by_city.items(), key=lambda x: -x[1])[:10])

        self.statistic_city = [sorted_salary_by_city, sorted_percentage_vac_by_city]

        return self.statistic_city


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
        self.area_name = vacancy[4]
        self.published_at = self.parse_date_simple(vacancy[5])
        self.salary = Salary([vacancy[1], vacancy[2], vacancy[3]], f"{self.published_at[0]}-{self.published_at[1]}")

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
    def __init__(self, salary, date):
        """Инициализирует объект Salary.

            Args:
                salary (list): Информация об окладе: нижняя граница оклада, верхняя граница оклада, валюта оклада
        """
        self.salary_currency = salary[2]
        self.date = date
        if salary[0] != '' and salary[1] != '':
            self.salary = self.convert_to_rubles((int(float(salary[0])) + int(float(salary[1]))) / 2)
        elif salary[0] != '':
            self.salary = self.convert_to_rubles(int(float(salary[0])))
        elif salary[1] != '':
            self.salary = self.convert_to_rubles(int(float(salary[1])))
        else:
            self.salary = None

    def convert_to_rubles(self, salary):
        """Вычисляет среднее значение зарплаты и конвертирует в рубли, при помощи словоря - currency_to_rub.

            Returns:
                float: Cреднее значение зарплаты в рублях
        """
        try:
            if self.salary_currency == "RUR":
                return salary
            else:
                index = currencies_df.index[currencies_df['date'] == self.date]
                return int(salary * currencies_df.loc[index, self.salary_currency].values[0])
        except:
            return None


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


def get_data(file_name):
    data_set, list_naming = csv_reader(file_name)
    if list_naming is None:
        print('Пустой файл')
    elif len(data_set.vacancies_objects) == 0:
        print('Нет данных')
    else:
        return data_set


def get_statistic(data_set, profession_name):
    """Получает данные из файла, вычисляет статистику и возвращяет её.

        Args:
            data_set (str): Набор данных для сбора статистики
            profession_name (str): Название профессии для сбора статистики по профессии
        Returns:
            list: Вычисленная статистика
    """
    return data_set.calculate_year_statistics(profession_name)


def print_statistic(statistic_year, statistic_city):
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
    print(f'Уровень зарплат по городам (в порядке убывания): {statistic_city[0]}')
    print(f'Доля вакансий по городам (в порядке убывания): {statistic_city[1]}')


def form_date(list):
    return f'{list[0]}-{list[1]}-{list[2]}T{list[3]}:{list[4]}:{list[5]}+{list[6]}'


def main():
    # name_file = input('Введите название файла: ')
    name_file = 'years'
    # profession_name = input('Введите название профессии: ')
    profession_name = 'Аналитик'
    files = [os.getcwd() + f'\\{name_file}\\' + file for file in os.listdir(os.getcwd() + f'\\{name_file}\\')]
    with Pool(8) as p:
        data_years = p.map(get_data, files)
        tuples_data_profession = [(data, profession_name) for data in data_years]
        statistic_year = p.starmap(get_statistic, tuples_data_profession)
    full_data = [[vacancy.name, vacancy.salary.salary, vacancy.area_name, form_date(vacancy.published_at)] for data in data_years for vacancy in data.vacancies_objects]
    data_df = pd.DataFrame(np.array(full_data[:100]))
    data_df.columns = ["name", "salary", "area_name", "published_at"]
    data_df.to_csv('first_hundred_vacancies.csv', index=False)
    statistic_city = DataSet().calculate_city_statistics(full_data)
    print_statistic(statistic_year, statistic_city)


if __name__ == '__main__':
    main()
