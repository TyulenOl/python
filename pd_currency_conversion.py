from multiprocessing import Pool
import os
import numpy as np
import pandas as pd


currencies_df = pd.read_csv('dataframe_currencies.csv')


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
    suitable_vacancies = df_vacancies[df_vacancies['salary'].notna()]
    salary_by_years = int(suitable_vacancies['salary'].mean())
    salary_by_years_profession = int(suitable_vacancies[suitable_vacancies['name'].str.contains(profession_name)]['salary'].mean())
    number_vac_by_years = len(suitable_vacancies)
    number_profession_by_years = suitable_vacancies['name'].str.contains(profession_name).sum()
    statistic_year = [year, salary_by_years, number_vac_by_years, salary_by_years_profession, number_profession_by_years]
    return statistic_year


def calculate_city_statistics(df_vacancies):
    statistic_city = pd.DataFrame()
    suitable_vacancies = df_vacancies[df_vacancies['salary'].notna()]
    statistic_city['percentage'] = suitable_vacancies['area_name'].value_counts().apply(lambda x: x / len(suitable_vacancies)).round(4)
    statistic_city['salary'] = suitable_vacancies.groupby('area_name')['salary'].mean()
    statistic_city['salary'] = statistic_city.loc[statistic_city['percentage'] >= 0.01, 'salary'].round(0)
    return statistic_city


def print_statistic(statistic_year, statistic_city):
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
    print(f'Уровень зарплат по городам (в порядке убывания): {statistic_city.sort_values(by="salary", ascending=False)["salary"].head(10).to_dict()}')
    print(f'Доля вакансий по городам (в порядке убывания): {statistic_city.sort_values(by="percentage", ascending=False)["percentage"].head(10).to_dict()}')


def main():
    # name_file = input('Введите название файла: ')
    name_file = 'years'
    # profession_name = input('Введите название профессии: ')
    profession_name = 'Аналитик'
    files = [os.getcwd() + f'\\{name_file}\\' + file for file in os.listdir(os.getcwd() + f'\\{name_file}\\')]
    with Pool(8) as p:
        data_years = p.map(get_data, files)
        tuples_data_profession = [(data, profession_name) for data in data_years]
        statistic_year = p.starmap(calculate_year_statistics, tuples_data_profession)
    full_data = pd.concat(data_years, ignore_index=True)
    data_df = full_data.head(100)
    data_df.to_csv('pd_first_hundred_vacancies.csv', index=False)
    statistic_city = calculate_city_statistics(full_data)
    print_statistic(statistic_year, statistic_city)


if __name__ == '__main__':
    main()
