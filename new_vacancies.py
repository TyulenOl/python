import requests
import pandas as pd
from datetime import datetime
import json


def get_request(day=datetime.today().day):
    date = datetime(datetime.today().year, datetime.today().month, day).date()
    all_vacancies = pd.DataFrame()
    for hour in range(0, 23):
        for page in range(20):
            res = get_page(date, hour, page)
            if res.status_code != 200:
                continue
            date_json = json.loads(res.text)['items']
            df = pd.DataFrame([{'name': safe_get(vacancy, 'name'),
                                'salary_from': safe_get(vacancy, 'salary', 'from'),
                                'salary_to': safe_get(vacancy, 'salary', 'to'),
                                'salary_currency': safe_get(vacancy, 'salary', 'currency'),
                                'area_name': safe_get(vacancy, 'area', 'name'),
                                'published_at': safe_get(vacancy, 'published_at')}
                               for vacancy in date_json])
            all_vacancies = pd.concat([all_vacancies, df], ignore_index=True)
    return all_vacancies, date


def get_page(date, hour, page):
    params = {
        'page': page,
        'per_page': 100,
        'specialization': 1,
        'date_from': f'{date}T{hour:02}:00:00',
        'date_to': f'{date}T{hour + 1:02}:00:00'
    }
    res = requests.get('https://api.hh.ru/vacancies', params)
    return res


def safe_get(vacancy, *keys):
    for key in keys:
        try:
            vacancy = vacancy[key]
        except:
            return None
    return vacancy


def main():
    day = 20
    all_vacancies, date = get_request(day)
    all_vacancies.to_csv(f'vacancies_for_{date}.csv', index=False)


if __name__ == '__main__':
    main()
