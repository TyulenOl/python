import csv
import math
import matplotlib.pyplot as plt
import numpy as np
import re
from datetime import datetime
import doctest

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
substitution_work_experience = {"noExperience": "Нет опыта", "between1And3": "От 1 года до 3 лет",
                                "between3And6": "От 3 до 6 лет", "moreThan6": "Более 6 лет"}
substitution_currency = {"AZN": "Манаты", "BYR": "Белорусские рубли", "EUR": "Евро", "GEL": "Грузинский лари",
                         "KGS": "Киргизский сом", "KZT": "Тенге", "RUR": "Рубли", "UAH": "Гривны", "USD": "Доллары",
                         "UZS": "Узбекский сум"}
reverse_naming = {'Навыки': 'key_skills', 'Оклад': 'salary', 'Дата публикации вакансии': 'published_at',
                  'Опыт работы': 'experience_id', 'Премиум-вакансия': 'premium',
                  'Идентификатор валюты оклада': 'salary_currency', 'Название': 'name',
                  'Название региона': 'area_name', 'Компания': 'employer_name', 'Описание': 'description'}


class DataSet:
    """Класс для хранения и обработки данных и статистики.

    Attributes:
        file_name (str): Имя исходного файла с данными
        vacancies_objects (list[Vacancy]): Лист вакансий со всеми заполненными значениями
        statistic (list[dict[int: int or str: int]]): Валюта оклада
    """

    def __init__(self, file_name, vacancies_objects):
        """Инициализирует объект DataSet.

        Args:
            file_name (str): Имя исходного файла с данными
            vacancies_objects (list): Лист вакансий для обработки

        >>> type(DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']])).__name__
        'DataSet'
        >>> DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]).file_name
        'unittest.csv'
        >>> len(DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]).vacancies_objects)
        1
        >>> DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]).vacancies_objects[0].name
        'IT аналитик'
        >>> DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]).vacancies_objects[0].area_name
        'Санкт-Петербург'
        >>> type(DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]).vacancies_objects[0].published_at).__name__
        'datetime'
        >>> DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]).vacancies_objects[0].published_at.strftime("%Y-%m-%dT%H:%M:%S%z")
        '2007-12-03T17:34:36+0300'
        >>> DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]).vacancies_objects[0].published_at.strftime("%Y.%m.%d")
        '2007.12.03'
        >>> type(DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]).vacancies_objects[0].salary).__name__
        'Salary'
        >>> DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]).vacancies_objects[0].salary.salary_from
        35000
        >>> DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]).vacancies_objects[0].salary.salary_to
        45000
        >>> DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]).vacancies_objects[0].salary.salary_currency
        'RUR'
        """

        self.file_name = file_name
        self.vacancies_objects = [Vacancy(row) for row in vacancies_objects if None not in row and '' not in row]
        self.statistic = []

    def calculate_statistics(self, profession_name):
        """Вычисляет статистику по вакансиям: динамика уровня зарплат по годам, динамика количества вакансий по
        годам, динамика уровня зарплат по годам для выбранной профессии, динамика количества вакансий по годам для
        выбранной профессии, уровень зарплат по городам (в порядке убывания) - только первые 10 значений,
        доля вакансий по городам (в порядке убывания) - только первые 10 значений.

        Args:
            profession_name(str): Название професии для сбора более конкретной статистики по данной професии

        Returns:
            list[dict[int: int or str: int]]: Собранная сатистика: динамика уровня зарплат по годам, динамика количества
             вакансий по годам, динамика уровня зарплат по годам для выбранной профессии, динамика количества вакансий
             по годам для выбранной профессии, уровень зарплат по городам (в порядке убывания) - только первые 10
             значений, доля вакансий по городам (в порядке убывания) - только первые 10 значений

        >>> DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]).calculate_statistics('аналитик')
        [{2007: 40000, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}, {2007: 1, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}, {2007: 40000, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}, {2007: 1, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}, {'Санкт-Петербург': 40000}, {'Санкт-Петербург': 1.0}]
        >>> DataSet('unittest.csv', [['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]).calculate_statistics('Инженер')
        [{2007: 40000, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}, {2007: 1, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}, {2007: 0, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}, {2007: 0, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}, {'Санкт-Петербург': 40000}, {'Санкт-Петербург': 1.0}]
        """

        salary_by_years = {}
        salary_by_years_profession = {}
        sum_salary_by_city = {}
        salary_by_city = {}
        number_vac_by_years = {}
        number_profession_by_years = {}
        number_vac_by_city = {}
        percentage_vac_by_city = {}
        for vacancy in self.vacancies_objects:
            year = vacancy.published_at.year
            city = vacancy.area_name
            number_vac_by_years[year] = number_vac_by_years.get(year, 0) + 1
            salary_by_years[year] = salary_by_years.get(year, 0) + vacancy.salary.convert_to_rubles()
            number_vac_by_city[city] = number_vac_by_city.get(city, 0) + 1
            sum_salary_by_city[city] = sum_salary_by_city.get(city, 0) + vacancy.salary.convert_to_rubles()
            salary_by_years_profession.setdefault(year, 0)
            number_profession_by_years.setdefault(year, 0)
            if profession_name in vacancy.name:
                salary_by_years_profession[year] = salary_by_years_profession.get(year,
                                                                                  0) + vacancy.salary.convert_to_rubles()
                number_profession_by_years[year] = number_profession_by_years.get(year, 0) + 1

        for year in number_vac_by_years.keys():
            salary_by_years[year] = math.floor(salary_by_years[year] / number_vac_by_years[year])

        for year in number_profession_by_years.keys():
            if number_profession_by_years[year] != 0:
                salary_by_years_profession[year] = math.floor(
                    salary_by_years_profession[year] / number_profession_by_years[year])

        for city in number_vac_by_city.keys():
            proportion_vacancy = number_vac_by_city.get(city) / len(self.vacancies_objects)
            if proportion_vacancy >= 0.01:
                percentage_vac_by_city[city] = round(proportion_vacancy, 4)
                salary_by_city[city] = math.floor(sum_salary_by_city[city] / number_vac_by_city.get(city))

        sorted_salary_by_city = dict(sorted(salary_by_city.items(), key=lambda x: -x[1])[:10])
        sorted_percentage_vac_by_city = dict(sorted(percentage_vac_by_city.items(), key=lambda x: -x[1])[:10])

        self.statistic = [salary_by_years, number_vac_by_years, salary_by_years_profession, number_profession_by_years,
                          sorted_salary_by_city, sorted_percentage_vac_by_city]

        return self.statistic

    def print_statistic(self):
        """Печатает статистику: динамика уровня зарплат по годам,динамика количества вакансий по годам,
        динамика уровня зарплат по годам для выбранной профессии, динамика количества вакансий по годам для выбранной
        профессии, уровень зарплат по городам (в порядке убывания) - только первые 10 значений, доля вакансий по
        городам (в порядке убывания) - только первые 10 значений.
        """

        print(f'Динамика уровня зарплат по годам: {self.statistic[0]}')
        print(f'Динамика количества вакансий по годам: {self.statistic[1]}')
        print(f'Динамика уровня зарплат по годам для выбранной профессии: {self.statistic[2]}')
        print(f'Динамика количества вакансий по годам для выбранной профессии: {self.statistic[3]}')
        print(f'Уровень зарплат по городам (в порядке убывания): {self.statistic[4]}')
        print(f'Доля вакансий по городам (в порядке убывания): {self.statistic[5]}')


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

        Args: vacancy (list): Лист данных о вакансии состоящий из: название профессии, оклад, название региона, дата
        публикации вакансии.

        >>> type(Vacancy(['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'])).__name__
        'Vacancy'
        >>> Vacancy(['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']).name
        'IT аналитик'
        >>> Vacancy(['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']).area_name
        'Санкт-Петербург'
        >>> type(Vacancy(['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']).published_at).__name__
        'datetime'
        >>> Vacancy(['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']).published_at.strftime("%Y-%m-%dT%H:%M:%S%z")
        '2007-12-03T17:34:36+0300'
        >>> type(Vacancy(['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']).salary).__name__
        'Salary'
        >>> Vacancy(['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']).salary.salary_from
        35000
        >>> Vacancy(['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']).salary.salary_to
        45000
        >>> Vacancy(['IT аналитик', '35000.0', '45000.0','RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']).salary.salary_currency
        'RUR'
        """

        self.name = vacancy[0].replace('\xa0', '\x20')
        self.salary = Salary([vacancy[1], vacancy[2], vacancy[3]])
        self.area_name = vacancy[4]
        self.published_at = datetime.strptime(vacancy[5], "%Y-%m-%dT%H:%M:%S%z")


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
            salary_from (str or int or float): Нижняя граница оклада
            salary_to (str or int or float): Нижняя граница оклада
            salary_currency (str): Нижняя граница оклада

        >>> type(Salary(['123000.0', '987000.0','RUR'])).__name__
        'Salary'
        >>> Salary(['123000.0', '987000.0','RUR']).salary_from
        123000
        >>> Salary(['123000', '987000.0','RUR']).salary_from
        123000
        >>> Salary(['123000.0', '987000.0','RUR']).salary_to
        987000
        >>> Salary(['123000.0', '987000','RUR']).salary_to
        987000
        >>> Salary(['123000.0', '987000.0','RUR']).salary_currency
        'RUR'
        >>> Salary(['123000.0', '987000.0','AZN']).salary_currency
        'AZN'
        """

        self.salary_from = int(float(salary[0]))
        self.salary_to = int(float(salary[1]))
        self.salary_currency = salary[2]

    def convert_to_rubles(self):
        """Вычисляет среднее значение зарплаты и конвертирует в рубли, при помощи словоря - currency_to_rub.

        Returns:
            float: Cреднее значение зарплаты в рублях

        >>> Salary(['123000.0', '987000.0','RUR']).convert_to_rubles()
        555000.0
        >>> Salary(['123000', '987000.0','RUR']).convert_to_rubles()
        555000.0
        >>> Salary(['123000.0', '987000','RUR']).convert_to_rubles()
        555000.0
        >>> Salary(['123000.0', '987000.0','AZN']).convert_to_rubles()
        19802400.0
        """

        return ((float(self.salary_from) + float(self.salary_to)) / 2) * float(currency_to_rub[self.salary_currency])


class Report:
    """Класс для формирования отчета в табличном виде.

    Attributes:
        titles (list[str]): Названия графиков
        legends (list[list[str]]): Подписи(легенды) для графиков
        fig (Figure): Контейнер самого верхнего уровня, та область на которой все нарисовано
        ax1 (AxesSubplot): Первый график
        ax2 (AxesSubplot): Второй график
        ax3 (AxesSubplot): Третий график
        ax4 (AxesSubplot): Четвертый график
    """

    def __init__(self, titles, legends):
        """Инициализирует графики.

        Args:
            titles (list[str]): Названия графиков
            legends (list[list[str]]): Подписи(легенды) для графиков
        """

        self.titles = titles
        self.legends = legends
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(nrows=2, ncols=2)

    def generate_image(self, statistic):
        """Создает в каталоге изображение со всеми необходимыми графиками на основе статистики.

        Args:
            statistic (list[dict[int: int or str: int]]): Статистика, на основе которой строятся графики
        """

        years_labels = list(statistic[1].keys())
        cities_labels = list(statistic[5].keys())
        salary_by_years = list(statistic[0].values())
        number_vac_by_years = list(statistic[1].values())
        salary_by_years_profession = list(statistic[2].values())
        number_profession_by_years = list(statistic[3].values())
        salary_by_city = list(statistic[4].values())
        percentage_vac_by_city = list(statistic[5].values())

        self.generate_vertical_graph(self.ax1, years_labels, [salary_by_years, salary_by_years_profession],
                                     self.titles[0], self.legends[0])
        self.generate_vertical_graph(self.ax2, years_labels, [number_vac_by_years, number_profession_by_years],
                                     self.titles[1], self.legends[1])
        self.generate_horizontal_graph(self.ax3, cities_labels, salary_by_city, self.titles[2])
        self.generate_pie_graph(self.ax4, cities_labels, percentage_vac_by_city, self.titles[3])

        plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
        plt.savefig('graph.png')

    @staticmethod
    def generate_vertical_graph(ax, labels, data, title, legends):
        """Генерирует графики с вертикально направленными столбиками данных.

        Args:
            ax (AxesSubplot): Область на которой отражаются графики
            labels (list[int]): Подписи оси Ox
            data (list[list[int]]): Данные на основе которых строится график
            title (str): Название для графика
            legends (list[str]): Подписи(легенды) к графику
        """
        y_pos = np.arange(len(labels))
        width = 0.35

        ax.bar(y_pos - width / 2, data[0], width, label=legends[0])
        ax.bar(y_pos + width / 2, data[1], width, label=legends[1])

        ax.set_title(title)
        ax.set_xticks(y_pos, labels, rotation=90)
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.grid(axis='y')
        ax.legend(fontsize=8)

    @staticmethod
    def generate_horizontal_graph(ax, labels, data, title):
        """Генерирует графики с горизонтально направленными столбиками данных.

        Args:
            ax (AxesSubplot): Область на которой отражаются графики
            labels (list[int]): Подписи оси Oy
            data (list[list[int]]): Данные на основе которых строится график
            title (str): Название для графика
        """
        new_labels = [re.sub('-', '-\n', label, count=1) if '-' in label else re.sub(' ', '\n', label, count=1) for
                      label in labels]
        y_pos = np.arange(len(new_labels))
        ax.barh(y_pos, data, align='center')
        ax.set_yticks(y_pos, labels=new_labels)
        ax.tick_params(axis='y', which='major', labelsize=6)
        ax.tick_params(axis='x', which='major', labelsize=8)
        ax.invert_yaxis()
        ax.grid(axis='x')
        ax.set_title(title)

    @staticmethod
    def generate_pie_graph(ax, labels, data, title):
        """Генерирует круговые диаграммы.

        Args:
            ax (AxesSubplot): Область на которой отражаются графики
            labels (list[int]): Подписи для долей
            data (list[list[int]]): Данные на основе которых строится график
            title (str): Название для графика
        """

        data = list(map(lambda x: x * 100, data))
        data.insert(0, 100 - sum(data))
        labels.insert(0, 'Другие')
        ax.pie(data, labels=labels, textprops={'fontsize': 6})
        ax.set_title(title)


def csv_reader(file_name):
    """Открывает и читает необходимый файл, а также возвращяет полученный результат.

    Args:
       file_name (str): Название файла для чтения

    Returns:
        DataSet, list: Полученные данные из прочитанного файла, строчка с названиями столбцов

    >>> len(csv_reader('unittest.csv'))
    2
    >>> type(csv_reader('unittest.csv')[0]).__name__
    'DataSet'
    >>> type(csv_reader('unittest.csv')[1]).__name__
    'list'
    >>> csv_reader('unittest.csv')[1]
    ['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']
    >>> csv_reader('unittest.csv')[0].file_name
    'unittest.csv'
    >>> len(csv_reader('unittest.csv')[0].vacancies_objects)
    1
    >>> type(csv_reader('unittest.csv')[0].vacancies_objects[0]).__name__
    'Vacancy'
    >>> csv_reader('unittest.csv')[0].vacancies_objects[0].name
    'IT аналитик'
    >>> csv_reader('unittest.csv')[0].vacancies_objects[0].area_name
    'Караганда'
    >>> type(csv_reader('unittest.csv')[0].vacancies_objects[0].published_at).__name__
    'datetime'
    >>> csv_reader('unittest.csv')[0].vacancies_objects[0].published_at.strftime("%Y-%m-%dT%H:%M:%S%z")
    '2015-07-13T17:34:36+0300'
    >>> type(csv_reader('unittest.csv')[0].vacancies_objects[0].salary).__name__
    'Salary'
    >>> csv_reader('unittest.csv')[0].vacancies_objects[0].salary.salary_from
    1230
    >>> csv_reader('unittest.csv')[0].vacancies_objects[0].salary.salary_to
    9870
    >>> csv_reader('unittest.csv')[0].vacancies_objects[0].salary.salary_currency
    'KGS'
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


def main():
    name_file = input('Введите название файла: ')
    profession_name = input('Введите название профессии: ')
    data_set, list_naming = csv_reader(name_file)
    if list_naming is None:
        print('Пустой файл')
    elif len(data_set.vacancies_objects) == 0:
        print('Нет данных')
    else:
        statistic = data_set.calculate_statistics(data_set, profession_name)
        titles = ['Уровень зарплат по годам', 'Количество вакансий по годам', 'Уровень зарплат по городам',
                  'Доля вакансий по городам']
        legends = [['средняя з/п', f'з/п {profession_name.lower()}'],
                   ['Количество вакансий', f'Количество ваканси\n{profession_name.lower()}']]
        report = Report(titles, legends)
        report.generate_image(statistic)


def get_graph_statistics(name_file, profession_name, titles):
    """Метод запускающий программу.

    Args:
       name_file (str): Название файла
       profession_name (str): Название профессии
       titles (list[str]): Названия графиков
    """
    data_set, list_naming = csv_reader(name_file)
    if list_naming is None:
        print('Пустой файл')
    elif len(data_set.vacancies_objects) == 0:
        print('Нет данных')
    else:
        statistic = data_set.calculate_statistics(profession_name)
        legends = [['средняя з/п', f'з/п {profession_name.lower()}'],
                   ['Количество вакансий', f'Количество ваканси\n{profession_name.lower()}']]
        report = Report(titles, legends)
        report.generate_image(statistic)


if __name__ == '__main__':
    main()
