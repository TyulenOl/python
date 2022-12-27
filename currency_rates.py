import csv
import requests
import xml.etree.ElementTree as ET
import pandas as pd


def csv_reader(file_name):
    with open(file_name, encoding="utf-8-sig") as file:
        reader = list(csv.reader(file))
        try:
            list_naming = reader.pop(0)
        except Exception:
            list_naming = None
        file.close()
        return reader


def calculate_currency_frequency(data):
    currency_frequency = {}
    for vacancy in data:
        currency_frequency[vacancy[3]] = currency_frequency.get(vacancy[3], 0) + 1
    satisfying_currencies = [currency[0] for currency in currency_frequency.items() if currency[1] >= 5000 and currency[0] != '']
    print('Частотность с которой встречаются различные валюты:')
    for key, value in currency_frequency.items():
        print(f'{key}: {value}')
    return currency_frequency, satisfying_currencies


def collect_currency_rates(data, currencies):
    first_date = list(parse_date(data[0][5])[:2])
    last_date = list(parse_date(data[len(data) - 1][5])[:2])
    number_months = (int(last_date[0]) - int(first_date[0])) * 12 + int(last_date[1]) - int(first_date[1]) + 1
    currency_rates = {'date': []}
    currency_rates.update({currency: [] for currency in currencies if currency != 'RUR'})
    for i in range(number_months):
        date = [first_date[0] + ((first_date[1] + i - 1) // 12), ((first_date[1] + i - 1) % 12) + 1]
        currency_rates['date'].append(f"{date[0]}-{date[1]:02}")
        response = requests.get(f"http://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{date[1]:02}/{date[0]}&d=0")
        root = ET.fromstring(response.text)
        for child in root:
            valute = [i.text for i in child]
            if valute[1] in currencies:
                currency_rates[valute[1]].append(round(float(valute[4].replace(',', '.'))/int(valute[2]), 5))
        for key, value in currency_rates.items():
            if len(currency_rates['date']) != len(currency_rates[key]):
                currency_rates[key].append(None)
    return currency_rates


def parse_date(date):
    year, month, day, hour, minute, second, timezone = date.replace('T', '-').replace(':', '-').replace('+', '-').split('-')
    return int(year), int(month), int(day), int(hour), int(minute), int(second), int(timezone)


def main():
    name_file = 'vacancies_dif_currencies.csv'
    data = csv_reader(name_file)
    currency_frequency, currencies = calculate_currency_frequency(data)
    currency_rates = collect_currency_rates(data, currencies)
    dataframe = pd.DataFrame(currency_rates)
    dataframe.to_csv("currencies.csv", index=False)


if __name__ == '__main__':
    main()
