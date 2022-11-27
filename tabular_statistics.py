import csv
import math
from openpyxl import Workbook
from openpyxl.styles import NamedStyle, Font, Border, Side
from openpyxl.worksheet.dimensions import ColumnDimension, DimensionHolder
from openpyxl.styles.numbers import FORMAT_PERCENTAGE_00
from openpyxl.utils import get_column_letter
from datetime import datetime

dic_naming = {'name': 'Название', 'description': 'Описание', 'key_skills': 'Навыки', 'experience_id': 'Опыт работы',
              'premium': 'Премиум-вакансия', 'employer_name': 'Компания', 'salary_from': 'Оклад',
              'area_name': 'Название региона', 'published_at': 'Дата публикации вакансии'}
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
    def __init__(self, file_name, vacancies_objects):
        self.file_name = file_name
        self.vacancies_objects = [Vacancy(row) for row in vacancies_objects if None not in row and '' not in row]
        self.statistic = []

    def calculateStatistics(self, data, profession_name):
        salary_by_years = {}
        salary_by_years_profession = {}
        sum_salary_by_city = {}
        salary_by_city = {}
        number_vac_by_years = {}
        number_profession_by_years = {}
        number_vac_by_city = {}
        percentage_vac_by_city = {}
        for vacancy in data.vacancies_objects:
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
            proportion_vacancy = number_vac_by_city.get(city) / len(data.vacancies_objects)
            if proportion_vacancy >= 0.01:
                percentage_vac_by_city[city] = round(proportion_vacancy, 4)
                salary_by_city[city] = math.floor(sum_salary_by_city[city] / number_vac_by_city.get(city))

        sorted_salary_by_city = dict(sorted(salary_by_city.items(), key=lambda x: -x[1])[:10])
        sorted_percentage_vac_by_city = dict(sorted(percentage_vac_by_city.items(), key=lambda x: -x[1])[:10])

        self.statistic = [salary_by_years, number_vac_by_years, salary_by_years_profession, number_profession_by_years,
                          sorted_salary_by_city, sorted_percentage_vac_by_city]

        return self.statistic

    def print_statistic(self):
        print(f'Динамика уровня зарплат по годам: {self.statistic[0]}')
        print(f'Динамика количества вакансий по годам: {self.statistic[1]}')
        print(f'Динамика уровня зарплат по годам для выбранной профессии: {self.statistic[2]}')
        print(f'Динамика количества вакансий по годам для выбранной профессии: {self.statistic[3]}')
        print(f'Уровень зарплат по городам (в порядке убывания): {self.statistic[4]}')
        print(f'Доля вакансий по городам (в порядке убывания): {self.statistic[5]}')


class Vacancy:
    def __init__(self, vacancy):
        if len(vacancy) == 6:
            self.name = vacancy[0].replace('\xa0', '\x20')
            self.salary = Salary([vacancy[1], vacancy[2], vacancy[3]])
            self.area_name = vacancy[4]
            self.published_at = datetime.strptime(vacancy[5], "%Y-%m-%dT%H:%M:%S%z")
        else:
            self.name = vacancy[0].replace('\xa0', '\x20')
            self.description = vacancy[1]
            self.key_skills = vacancy[2]
            self.experience_id = substitution_work_experience[vacancy[3]]
            self.premium = 'Да' if vacancy[4] == 'True' else 'Нет' if vacancy[4] == 'False' else vacancy[4]
            self.employer_name = vacancy[5]
            self.salary = Salary([vacancy[6], vacancy[7], vacancy[8], vacancy[9]])
            self.area_name = vacancy[10]
            self.published_at = datetime.strptime(vacancy[11], "%Y-%m-%dT%H:%M:%S%z")


class Salary:
    def __init__(self, salary):
        if len(salary) == 3:
            self.salary_from = int(float(salary[0]))
            self.salary_to = int(float(salary[1]))
            self.salary_currency = salary[2]
            self.average_salary = (self.salary_from + self.salary_to) / 2
        else:
            self.salary_from = int(float(salary[0]))
            self.salary_to = int(float(salary[1]))
            self.salary_gross = 'С вычетом налогов' if salary[2] == "False" else 'Без вычета налогов'
            self.salary_currency = salary[3]
            self.salary = f'{self.salary_from:_} - {self.salary_to:_} ({self.salary_currency} ({self.salary_gross}))'.replace(
                '_', ' ')

    def convert_to_rubles(self):
        return (((float(self.salary_from) + float(self.salary_to)) * float(currency_to_rub[self.salary_currency])) / 2)


class InputConnect:
    def __init__(self, input_data):
        self.filter_parameter = input_data[0]
        self.sort_parameter = input_data[1]
        self.reverse_sort_order = True if input_data[2] == 'Да' else False if input_data[2] == 'Нет' or input_data[
            2] == '' else None
        self.table_from_to = input_data[3]
        self.desired_column_names = input_data[4]

    def data_processing(self):
        if self.filter_parameter != '' and ': ' not in self.filter_parameter:
            print('Формат ввода некорректен')
            return True
        if self.filter_parameter != '':
            try:
                reverse_naming[self.filter_parameter.split(': ')[0]]
            except Exception:
                print('Параметр поиска некорректен')
                return True

        if self.sort_parameter != '':
            try:
                reverse_naming[self.sort_parameter]
            except Exception:
                print('Параметр сортировки некорректен')
                return True
        if self.reverse_sort_order is None:
            print('Порядок сортировки задан некорректно')
            return True
        return False


class Report:
    def __init__(self, sheet_titles, headlines):
        self.sheet_titles = sheet_titles
        self.wb = Workbook()
        self.wb.remove(self.wb['Sheet'])
        for title in sheet_titles:
            self.wb.create_sheet(title)

        for sheet in range(len(headlines)):
            ws = self.wb[self.wb.sheetnames[sheet]]
            ws.append(headlines[sheet])

    def setting_workbook(self):
        for ws in self.wb:
            for column_cells in ws.columns:
                new_column_length = max(len(str(cell.value)) for cell in column_cells)
                new_column_letter = (get_column_letter(column_cells[0].column))
                if new_column_length > 0:
                    ws.column_dimensions[new_column_letter].width = new_column_length * 1.20

            side = Side(style='thin', color="000000")
            for cell in ws._cells.values():
                if cell.row == 1:
                    cell.font = Font(bold=True, size=11)
                if cell.value is not None:
                    cell.border = Border(top=side, bottom=side, left=side, right=side)

        for cell in self.wb[self.wb.sheetnames[1]]['E']:
            cell.number_format = FORMAT_PERCENTAGE_00

    def generate_excel(self, statistic):
        salary_by_years = statistic[0]
        number_vac_by_years = statistic[1]
        salary_by_years_profession = statistic[2]
        number_profession_by_years = statistic[3]
        salary_by_city = statistic[4]
        percentage_vac_by_city = statistic[5]
        ws = self.wb[self.wb.sheetnames[0]]
        row = 2
        for year in number_vac_by_years.keys():
            ws[row][0].value = year
            ws[row][1].value = salary_by_years[year]
            ws[row][2].value = salary_by_years_profession[year]
            ws[row][3].value = number_vac_by_years[year]
            ws[row][4].value = number_profession_by_years[year]
            row += 1

        ws = self.wb[self.wb.sheetnames[1]]
        row = 2
        for city in salary_by_city.keys():
            ws[row][0].value = city
            ws[row][1].value = salary_by_city[city]
            row += 1

        row = 2
        for city in percentage_vac_by_city.keys():
            ws[row][3].value = city
            ws[row][4].value = percentage_vac_by_city[city]
            row += 1

        self.setting_workbook()
        self.wb.save('report.xlsx')
        self.wb.close()


def csv_reader(file_name):
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
    input_data = []
    input_data.append(f"Название: {input('Введите название профессии: ')}")
    list(map(lambda x: input_data.append(x), ['', '', '', [], ['']]))
    input_connect = InputConnect(input_data)
    if input_connect.data_processing():
        return
    data_set, list_naming = csv_reader(name_file)
    if list_naming is None:
        print('Пустой файл')
    elif len(data_set.vacancies_objects) == 0:
        print('Нет данных')
    else:
        profession_name = input_connect.filter_parameter.split(': ')[1]
        statistic = data_set.calculateStatistics(data_set, profession_name)
        sheet1_headlines = {'A': 'Год', 'B': 'Средняя зарплата', 'C': f'Средняя зарплата - {profession_name}',
                            'D': 'Количество вакансий', 'E': f'Количество вакансий - {profession_name}'}
        sheet2_headlines = {'A': 'Город', 'B': 'Уровень зарплат', 'D': 'Город', 'E': 'Доля вакансий'}
        report = Report(['Статистика по годам', 'Статистика по городам'], [sheet1_headlines, sheet2_headlines])
        report.generate_excel(statistic)


def get_tabular_statistics():
    main()


if __name__ == '__main__':
    main()
