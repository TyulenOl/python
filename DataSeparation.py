import csv
import os


def csv_reader(file_name):
    """Открывает и читает необходимый файл, а также возвращяет полученный результат.

    Args:
       file_name (str): Название файла для чтения

    Returns:
        list(list), list: Полученные данные из прочитанного файла; строчка с названиями столбцов
    """

    with open(file_name, encoding="utf-8-sig") as file:
        reader = list(csv.reader(file))
        try:
            list_naming = reader.pop(0)
        except Exception:
            list_naming = None
        file.close()
        return reader, list_naming


def separate_data(data):
    """Разделяет входные данные по годам

    Args:
        data (list(list)): Набор данных, которые необходимо разделить по годам
    Returns:
        dict(list(list)): Данные разделенные по годам
    """
    split_data = {}
    for row in data:
        year = int(row[5][:4])
        if year not in split_data.keys():
            split_data[year] = list()
        split_data[year].append(row)
    return split_data


def create_directory():
    """Создает директорию для хранения разделенных по годам файлов"""
    path = os.getcwd() + '\years'
    try:
        os.mkdir(path)
    except OSError:
        print(f'Создать директорию {path} не удалось')
    else:
        print(f'Успешно создана директория {path}')


def create_files(data, list_naming):
    """Создает csv файлы, где каждый файл хранит данные о вакансиях за один определенный год

    Args:
        data: Данные для записи в файлы
        list_naming: Заголовки для столбцов
    """
    path = os.getcwd() + "\years\\"
    for year in data.items():
        with open(f'{path}{year[0]}_year.csv', 'w', newline='', encoding="utf-8") as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(list_naming)
            filewriter.writerows(year[1])


def main():
    data, list_naming = csv_reader('vacancies_by_year.csv')
    split_data = separate_data(data)
    create_directory()
    create_files(split_data, list_naming)


if __name__ == "__main__":
    main()
