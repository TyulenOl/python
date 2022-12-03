import graph_statistics
import tabular_statistics


def main():
    type_statistics = input("Введите данные для печати: ")

    if type_statistics not in ['Вакансии', 'Статистика']:
        print('Некорректный ввод')
        return

    name_file = input('Введите название файла: ')
    profession_name = input('Введите название профессии: ')

    if type_statistics == 'Вакансии':
        sheet1_headlines = {'A': 'Год', 'B': 'Средняя зарплата', 'C': f'Средняя зарплата - {profession_name}',
                            'D': 'Количество вакансий', 'E': f'Количество вакансий - {profession_name}'}
        sheet2_headlines = {'A': 'Город', 'B': 'Уровень зарплат', 'D': 'Город', 'E': 'Доля вакансий'}
        sheet_titles = ['Статистика по годам', 'Статистика по городам']
        tabular_statistics.get_tabular_statistics(name_file, profession_name, sheet_titles, [sheet1_headlines, sheet2_headlines])

    elif type_statistics == 'Статистика':
        titles = ['Уровень зарплат по годам', 'Количество вакансий по годам', 'Уровень зарплат по городам',
                  'Доля вакансий по городам']
        graph_statistics.get_graph_statistics(name_file, profession_name, titles)


if __name__ == '__main__':
    main()
