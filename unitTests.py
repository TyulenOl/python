from unittest import TestCase
from tabular_statistics import DataSet, Vacancy, Salary, csv_reader


class DataSetTests(TestCase):
    def test_dataset_type(self):
        file_name = 'unittest.csv'
        data = [['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'],
                ['PHP-программист', '40000.0', '50000.0', 'RUR', 'Москва', '2007-12-03T22:39:07+0300'],
                ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']]
        self.assertEqual(type(DataSet(file_name, data)).__name__, 'DataSet')

    def test_dataset_file_name(self):
        file_name = 'unittest.csv'
        data = [['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'],
                ['PHP-программист', '40000.0', '50000.0', 'RUR', 'Москва', '2007-12-03T22:39:07+0300'],
                ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']]
        self.assertEqual(DataSet(file_name, data).file_name, 'unittest.csv')

    def test_dataset_vacancies_objects_length(self):
        file_name = 'unittest.csv'
        data = [['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'],
                ['PHP-программист', '40000.0', '50000.0', 'RUR', 'Москва', '2007-12-03T22:39:07+0300'],
                ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']]
        self.assertEqual(len(DataSet(file_name, data).vacancies_objects), 3)

    def test_dataset_vacancies_objects_name(self):
        file_name = 'unittest.csv'
        data = [['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'],
                ['PHP-программист', '40000.0', '50000.0', 'RUR', 'Москва', '2007-12-03T22:39:07+0300'],
                ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']]
        self.assertEqual(DataSet(file_name, data).vacancies_objects[0].name, 'IT аналитик')
        self.assertEqual(DataSet(file_name, data).vacancies_objects[2].name, 'Web-программист')

    def test_dataset_vacancies_objects_area_name(self):
        file_name = 'unittest.csv'
        data = [['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'],
                ['PHP-программист', '40000.0', '50000.0', 'RUR', 'Москва', '2007-12-03T22:39:07+0300'],
                ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']]
        self.assertEqual(DataSet(file_name, data).vacancies_objects[0].area_name, 'Санкт-Петербург')
        self.assertEqual(DataSet(file_name, data).vacancies_objects[2].area_name, 'Москва')

    def test_dataset_vacancies_objects_published_at_type(self):
        file_name = 'unittest.csv'
        data = [['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'],
                ['PHP-программист', '40000.0', '50000.0', 'RUR', 'Москва', '2007-12-03T22:39:07+0300'],
                ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']]
        self.assertEqual(type(DataSet(file_name, data).vacancies_objects[0].published_at).__name__, 'datetime')

    def test_dataset_vacancies_objects_published_at(self):
        file_name = 'unittest.csv'
        data = [['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'],
                ['PHP-программист', '40000.0', '50000.0', 'RUR', 'Москва', '2007-12-03T22:39:07+0300'],
                ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']]
        self.assertEqual(DataSet(file_name, data).vacancies_objects[0].published_at.strftime("%Y-%m-%dT%H:%M:%S%z"), '2007-12-03T17:34:36+0300')
        self.assertEqual(DataSet(file_name, data).vacancies_objects[2].published_at.strftime("%Y-%m-%dT%H:%M:%S%z"), '2007-12-03T19:10:20+0300')
        self.assertEqual(DataSet(file_name, data).vacancies_objects[0].published_at.strftime("%Y.%m.%d"), '2007.12.03')

    def test_dataset_vacancies_objects_salary_type(self):
        file_name = 'unittest.csv'
        data = [['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'],
                ['PHP-программист', '40000.0', '50000.0', 'RUR', 'Москва', '2007-12-03T22:39:07+0300'],
                ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']]
        self.assertEqual(type(DataSet(file_name, data).vacancies_objects[0].salary).__name__, 'Salary')

    def test_dataset_vacancies_objects_salary(self):
        file_name = 'unittest.csv'
        data = [['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'],
                ['PHP-программист', '40000.0', '50000.0', 'RUR', 'Москва', '2007-12-03T22:39:07+0300'],
                ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']]
        self.assertEqual(DataSet(file_name, data).vacancies_objects[2].salary.salary_from, 30000)
        self.assertEqual(DataSet(file_name, data).vacancies_objects[2].salary.salary_to, 40000)
        self.assertEqual(DataSet(file_name, data).vacancies_objects[2].salary.salary_currency, 'RUR')

    def test_dataset_calculate_statistics(self):
        file_name = 'unittest.csv'
        data = [['IT аналитик', '32000.0', '56000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300'],
                ['PHP-программист', '41000.0', '67000.0', 'RUR', 'Москва', '2007-12-03T22:39:07+0300'],
                ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2008-12-03T19:10:20+0300']]
        expected = [{2007: 49000, 2008: 35000, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}, {2007: 2, 2008: 1, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}, {2007: 54000, 2008: 35000, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}, {2007: 1, 2008: 1, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}, {'Москва': 44500, 'Санкт-Петербург': 44000}, {'Москва': 0.6667, 'Санкт-Петербург': 0.3333}]
        self.assertEqual(DataSet(file_name, data).calculate_statistics('программист'), expected)


class VacancyTests(TestCase):
    def test_vacancy_type(self):
        data = ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']
        self.assertEqual(type(Vacancy(data)).__name__, 'Vacancy')

    def test_vacancy_name(self):
        data = ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']
        self.assertEqual(Vacancy(data).name, 'Web-программист')

    def test_vacancy_area_name(self):
        data = ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']
        self.assertEqual(Vacancy(data).area_name, 'Москва')

    def test_vacancy_published_at_type(self):
        data = ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']
        self.assertEqual(type(Vacancy(data).published_at).__name__, 'datetime')

    def test_vacancy_published_at(self):
        data = ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']
        self.assertEqual(Vacancy(data).published_at.strftime("%Y-%m-%dT%H:%M:%S%z"), '2007-12-03T19:10:20+0300')
        self.assertEqual(Vacancy(data).published_at.strftime("%d.%m.%Y"), '03.12.2007')

    def test_vacancy_salary_type(self):
        data = ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']
        self.assertEqual(type(Vacancy(data).salary).__name__, 'Salary')

    def test_vacancy_salary(self):
        data = ['Web-программист', '30000.0', '40000.0', 'RUR', 'Москва', '2007-12-03T19:10:20+0300']
        self.assertEqual(Vacancy(data).salary.salary_from, 30000)
        self.assertEqual(Vacancy(data).salary.salary_to, 40000)
        self.assertEqual(Vacancy(data).salary.salary_currency, 'RUR')


class SalaryTests(TestCase):
    def test_salary_type(self):
        self.assertEqual(type(Salary(['32000.0', '46000.0', 'RUR'])).__name__, 'Salary')

    def test_salary_from(self):
        self.assertEqual(Salary(['32000', '46000.0', 'RUR']).salary_from, 32000)
        self.assertEqual(Salary(['32000.0', '46000.0', 'RUR']).salary_from, 32000)

    def test_salary_to(self):
        self.assertEqual(Salary(['32000.0', '46000.0', 'RUR']).salary_to, 46000)
        self.assertEqual(Salary(['32000.0', '46000', 'RUR']).salary_to, 46000)

    def test_salary_currency(self):
        self.assertEqual(Salary(['32000.0', '46000.0', 'RUR']).salary_currency, 'RUR')
        self.assertEqual(Salary(['32000.0', '46000.0', 'KGS']).salary_currency, 'KGS')

    def test_salary_convert_to_rubles(self):
        self.assertEqual(Salary(['32000.0', '46000.0', 'RUR']).convert_to_rubles(), 39000.0)
        self.assertEqual(Salary(['32000.0', '46000.0', 'KGS']).convert_to_rubles(), 29640.0)


class CsvReaderTests(TestCase):
    def test_csv_reader_length_result(self):
        self.assertEqual(len(csv_reader('unittest.csv')), 2)

    def test_csv_reader_type(self):
        self.assertEqual(type(csv_reader('unittest.csv')).__name__, 'tuple')

    def test_csv_reader_result_elements_type(self):
        self.assertEqual(type(csv_reader('unittest.csv')[0]).__name__, 'DataSet')
        self.assertEqual(type(csv_reader('unittest.csv')[1]).__name__, 'list')

    def test_csv_reader_dataset_file_name(self):
        self.assertEqual(csv_reader('unittest.csv')[0].file_name, 'unittest.csv')

    def test_csv_reader_dataset_vacancies_objects_length(self):
        self.assertEqual(len(csv_reader('unittest.csv')[0].vacancies_objects), 3)