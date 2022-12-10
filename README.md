## Задание 2.3.2:
* ### Тесты doctest:
   ![doctest](https://user-images.githubusercontent.com/100992984/205491915-e05a7eb7-8e4a-4ef4-a5aa-f802bc6340fe.png)
* ### Тесты unittest:
   ![unittest](https://user-images.githubusercontent.com/100992984/205491930-df5f932a-2bb0-4707-920c-0c030254ee73.png)
* ### Содержимое файла unittest.csv:
   ![csv](https://user-images.githubusercontent.com/100992984/205491958-b7ce6905-27a4-4856-b125-0d4986410338.png)

## Задание 2.3.3:
* ### 30 самых долгих по времени выполнения функций:
   ![statistic](https://user-images.githubusercontent.com/100992984/205505639-ca791422-5983-482e-9b10-71650d50dafb.png)

* ### Результат первого измерения обособленной функции parse_date_strptime:
   ![date_strptime1](https://user-images.githubusercontent.com/100992984/205505411-54ccea97-4427-44a7-801c-720914bba638.png)
   
* ### 3 варианта форматирования даты и времени:
   ```python
       def parse_date_simple(date):
           date = date.replace('T', '-').replace(':', '-').replace('+', '-')
           year, month, day, hour, minute, second, timezone = date.split('-')
           return year, month, day, hour, minute, second, timezone
   
       def parse_date_regex(date):
           year, month, day, hour, minute, second, timezone = re.split("[-T:+]", date)
           return year, month, day, hour, minute, second, timezone
   
       def parse_date_strptime(date):
           result = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
           return result
   ```
   
* ### Результаты измерения 3-х функций форматирования даты и времени:
   ![date_simple](https://user-images.githubusercontent.com/100992984/205505539-599613eb-74fc-423b-bf0a-c73ca1eaca78.png)
   ![date_regex](https://user-images.githubusercontent.com/100992984/205505543-ad99f90b-6811-4e79-a242-d321b595c938.png)
   ![date_strptime2](https://user-images.githubusercontent.com/100992984/205505545-322b47b3-6b57-41a8-9566-42c7810efadf.png)  
   Наиболее быстрой функцией форматирования даты и времени является parse_date_simple
   
## Задание 3.2.1:
* ### Папка с разделенными на года csv файлами 
![Screenshot_11](https://user-images.githubusercontent.com/100992984/206690234-e8b6d315-48c5-4291-866e-731976f0f471.png)
