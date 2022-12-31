import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import Pool
import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit

currencies_df = pd.read_csv('dataframe_currencies.csv')


class Report:
    def __init__(self, statistic, graph_titles, graph_legends, sheet_headlines):
        self.statistic = statistic
        self.years = statistic['year'].values
        self.salary_by_years = statistic['salary_by_years'].values
        self.number_vac_by_years = statistic['number_vac_by_years'].values
        self.salary_by_years_profession = statistic['salary_by_years_profession'].values
        self.number_profession_by_years = statistic['number_profession_by_years'].values
        self.graph_titles = graph_titles
        self.graph_legends = graph_legends
        self.fig, (self.ax1, self.ax2) = plt.subplots(nrows=2, ncols=1)
        self.sheet_headlines = sheet_headlines

    def generate_image(self):
        self.generate_vertical_graph(self.ax1, self.years, [self.salary_by_years, self.salary_by_years_profession],
                                     self.graph_titles[0], self.graph_legends[0])
        self.generate_vertical_graph(self.ax2, self.years, [self.number_vac_by_years, self.number_profession_by_years],
                                     self.graph_titles[1], self.graph_legends[1])

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

    def generate_pdf(self):
        year_table = self.statistic
        year_table.columns = self.sheet_headlines[0].values()

        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("pdf_template.html")

        pdf_template = template.render({'year_table': year_table})

        config = pdfkit.configuration(wkhtmltopdf=r'D:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options={'enable-local-file-access': None})


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


def calculate_year_statistics(df_vacancies, profession_name):
    year = parse_date(df_vacancies.iloc[0]['published_at'])[0]
    statistic_year = pd.DataFrame(index=[year])
    suitable_vacancies = df_vacancies[df_vacancies['salary'].notna()]
    statistic_year['year'] = year
    statistic_year['salary_by_years'] = int(suitable_vacancies['salary'].mean())
    statistic_year['salary_by_years_profession'] = int(suitable_vacancies[suitable_vacancies['name'].str.contains(profession_name)]['salary'].mean())
    statistic_year['number_vac_by_years'] = len(suitable_vacancies)
    statistic_year['number_profession_by_years'] = suitable_vacancies['name'].str.contains(profession_name).sum()
    return statistic_year


def main():
    name_file = input('Введите название файла: ')
    # name_file = 'years'
    profession_name = input('Введите название профессии: ')
    # profession_name = 'Инженер'
    files = [os.getcwd() + f'\\{name_file}\\' + file for file in os.listdir(os.getcwd() + f'\\{name_file}\\')]
    with Pool(8) as p:
        data_years = p.map(get_data, files)
        tuples_data_profession = [(data, profession_name) for data in data_years]
        statistic_year = p.starmap(calculate_year_statistics, tuples_data_profession)
    statistic_year = pd.concat(statistic_year, ignore_index=True)
    graph_titles = ['Уровень зарплат по годам', 'Количество вакансий по годам', 'Уровень зарплат по городам',
              'Доля вакансий по городам']
    graph_legends = [['средняя з/п', f'з/п {profession_name.lower()}'],
               ['Количество вакансий', f'Количество ваканси\n{profession_name.lower()}']]
    sheet_headlines = [{'A': 'Год', 'B': 'Средняя зарплата', 'C': f'Средняя зарплата - {profession_name}',
                        'D': 'Количество вакансий', 'E': f'Количество вакансий - {profession_name}'}]
    report = Report(statistic_year, graph_titles, graph_legends, sheet_headlines)
    report.generate_image()
    report.generate_pdf()


if __name__ == '__main__':
    main()
