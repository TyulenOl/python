import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import Pool
import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit
import re

currencies_df = pd.read_csv('dataframe_currencies.csv')


class Report:
    def __init__(self, statistic_year, statistic_city, graph_titles, graph_legends, sheet_headlines):
        self.statistic_year = statistic_year
        self.statistic_city = statistic_city
        self.years = statistic_year['year'].values
        self.salary_by_years = statistic_year['salary_by_years'].values
        self.number_vac_by_years = statistic_year['number_vac_by_years'].values
        self.salary_by_years_profession = statistic_year['salary_by_years_profession'].values
        self.number_profession_by_years = statistic_year['number_profession_by_years'].values
        self.salary_by_years_city = statistic_year['salary_by_years_city'].values
        self.number_city_by_years = statistic_year['number_city_by_years'].values
        self.percentage_by_city = statistic_city.sort_values(by="percentage_by_city", ascending=False)["percentage_by_city"].head(10).to_dict()
        self.salary_by_city = statistic_city.sort_values(by="salary_by_city", ascending=False)["salary_by_city"].head(10).to_dict()
        self.graph_titles = graph_titles
        self.graph_legends = graph_legends
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(nrows=2, ncols=2)
        self.sheet_headlines = sheet_headlines

    def generate_image(self):
        self.generate_vertical_graph(self.ax1, self.years, [self.salary_by_years, self.salary_by_years_profession, self.salary_by_years_city],
                                     self.graph_titles[0], self.graph_legends[0])
        self.generate_vertical_graph(self.ax2, self.years, [self.number_vac_by_years, self.number_profession_by_years, self.number_city_by_years],
                                     self.graph_titles[1], self.graph_legends[1])
        self.generate_horizontal_graph(self.ax3, list(self.salary_by_city.keys()), list(self.salary_by_city.values()), self.graph_titles[2])
        self.generate_pie_graph(self.ax4, list(self.percentage_by_city.keys()), list(self.percentage_by_city.values()), self.graph_titles[3])

        plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
        plt.savefig('graph.png')

    @staticmethod
    def generate_vertical_graph(ax, labels, data, title, legends):
        y_pos = np.arange(len(labels))
        width = 0.26

        ax.bar(y_pos - width, data[0], width, label=legends[0])
        ax.bar(y_pos, data[1], width, label=legends[1])
        ax.bar(y_pos + width, data[2], width, label=legends[2])

        ax.set_title(title)
        ax.set_xticks(y_pos, labels, rotation=90)
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.grid(axis='y')
        ax.legend(fontsize=8)

    @staticmethod
    def generate_horizontal_graph(ax, labels, data, title):
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
        data = list(map(lambda x: x * 100, data))
        data.insert(0, 100 - sum(data))
        labels.insert(0, 'Другие')
        ax.pie(data, labels=labels, textprops={'fontsize': 6})
        ax.set_title(title)

    def generate_pdf(self):
        year_table = self.statistic_year
        year_table.columns = self.sheet_headlines[0].values()
        salary_city_table = self.statistic_city.sort_values(by="salary_by_city", ascending=False)["salary_by_city"].head(10).to_frame().reset_index(level=0)
        salary_city_table.columns = list(self.sheet_headlines[1].values())[0:2]
        percentage_city_table = self.statistic_city.sort_values(by="percentage_by_city", ascending=False)["percentage_by_city"].head(10).to_frame().reset_index(level=0)
        percentage_city_table['percentage_by_city'] = percentage_city_table['percentage_by_city'].apply(lambda x: f'{round(x * 100, 2)}%')
        percentage_city_table.columns = list(self.sheet_headlines[1].values())[2:4]

        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("pdf_template_city.html")

        pdf_template = template.render({'year_table': year_table, 'salary_city_table': salary_city_table, 'percentage_city_table': percentage_city_table})

        config = pdfkit.configuration(wkhtmltopdf=r'D:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report_city.pdf', configuration=config, options={'enable-local-file-access': None})


def get_salary(series):
    date = parse_date(series['published_at'])
    date = f'{date[0]}-{date[1]:02}'
    if not pd.isna(series['salary_from']) and not pd.isna(series['salary_to']):
        salary = convert_to_rubles((int(float(series['salary_from'])) + int(float(series['salary_to']))) / 2, series['salary_currency'], date)
    elif not pd.isna(series['salary_from']):
        salary = convert_to_rubles(int(float(series['salary_from'])), series['salary_currency'], date)
    elif not pd.isna(series['salary_to']):
        salary = convert_to_rubles(int(float(series['salary_to'])), series['salary_currency'], date)
    else:
        salary = np.NaN
    return salary


def parse_date(date):
    parsed_date = date.replace('T', '-').replace(':', '-').replace('+', '-').split('-')
    return int(parsed_date[0]), int(parsed_date[1])


def convert_to_rubles(salary, currency, date):
    try:
        if currency == "RUR":
            return salary
        else:
            return int(salary * currencies_df.loc[currencies_df['date'] == date, currency].values[0])
    except:
        return np.NaN


def get_data(file_name):
    df = pd.read_csv(file_name)
    if len(df) == 0:
        print('Нет данных')
    else:
        df['salary'] = df[['salary_from', 'salary_to', 'salary_currency', 'published_at']].apply(get_salary, axis=1)
        df = df.drop(['salary_from', 'salary_to', 'salary_currency'], axis=1)
        return df


def calculate_year_statistics(df_vacancies, profession_name, area_name):
    year = parse_date(df_vacancies.iloc[0]['published_at'])[0]
    statistic_year = pd.DataFrame(index=[year])
    suitable_vacancies = df_vacancies[df_vacancies['salary'].notna()]
    statistic_year['year'] = year
    statistic_year['salary_by_years'] = int(suitable_vacancies['salary'].mean())
    statistic_year['salary_by_years_profession'] = int(suitable_vacancies[suitable_vacancies['name'].str.contains(profession_name)]['salary'].mean())
    statistic_year['salary_by_years_city'] = int(suitable_vacancies.loc[suitable_vacancies['area_name'] == area_name, 'salary'].mean())
    statistic_year['number_vac_by_years'] = len(suitable_vacancies)
    statistic_year['number_profession_by_years'] = suitable_vacancies['name'].str.contains(profession_name).sum()
    statistic_year['number_city_by_years'] = len(suitable_vacancies[suitable_vacancies['area_name'] == area_name])
    return statistic_year


def calculate_city_statistics(df_vacancies):
    statistic_city = pd.DataFrame()
    suitable_vacancies = df_vacancies[df_vacancies['salary'].notna()]
    statistic_city['percentage_by_city'] = suitable_vacancies['area_name'].value_counts().apply(lambda x: x / len(suitable_vacancies)).round(4)
    statistic_city['salary_by_city'] = suitable_vacancies.groupby('area_name')['salary'].mean()
    statistic_city['salary_by_city'] = statistic_city.loc[statistic_city['percentage_by_city'] >= 0.01, 'salary_by_city'].round(0)
    return statistic_city


def main():
    # name_file = input('Введите название файла: ')
    name_file = 'years'
    # profession_name = input('Введите название профессии: ')
    profession_name = 'Инженер'
    # area_name = input('Введите название региона: ')
    area_name = 'Москва'
    files = [os.getcwd() + f'\\{name_file}\\' + file for file in os.listdir(os.getcwd() + f'\\{name_file}\\')]
    with Pool(8) as p:
        data_years = p.map(get_data, files)
        tuples_data_profession = [(data, profession_name, area_name) for data in data_years]
        statistic_year = p.starmap(calculate_year_statistics, tuples_data_profession)
    full_data = pd.concat(data_years, ignore_index=True)
    statistic_year = pd.concat(statistic_year, ignore_index=True)
    statistic_city = calculate_city_statistics(full_data)
    graph_titles = ['Уровень зарплат по годам', 'Количество вакансий по годам', 'Уровень зарплат по городам',
              'Доля вакансий по городам']
    graph_legends = [['средняя з/п', f'з/п {profession_name.lower()}', f'з/п в регионе\n{area_name.lower()}'],
               ['Количество вакансий', f'Количество ваканси\n{profession_name.lower()}', f'Количество ваканси в\nрегионе {area_name.lower()}']]
    sheet_headlines = [{'A': 'Год', 'B': 'Средняя зарплата', 'C': f'Средняя зарплата - {profession_name}',
                        'D': f'Средняя зарплата - {area_name}', 'E': 'Количество вакансий',
                        'F': f'Количество вакансий - {profession_name}', 'G': f'Количество вакансий - {area_name}'},
                       {'A': 'Город', 'B': 'Уровень зарплат', 'D': 'Город', 'E': 'Доля вакансий'}]
    report = Report(statistic_year, statistic_city, graph_titles, graph_legends, sheet_headlines)
    report.generate_image()
    report.generate_pdf()


if __name__ == '__main__':
    main()
