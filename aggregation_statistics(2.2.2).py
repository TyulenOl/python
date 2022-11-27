import graph_statistics
import tabular_statistics


def main():
    type_statistics = input("Введите данные для печати: ")

    if type_statistics not in ['Вакансии', 'Статистика']:
        print('Некорректный ввод')
        return

    if type_statistics == 'Вакансии':
        tabular_statistics.get_tabular_statistics()

    elif type_statistics == 'Статистика':
        graph_statistics.get_graph_statistics()


if __name__ == '__main__':
    main()

# Изменение файла в ветке main
