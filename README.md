# rainforest


RESTful API service

# Run application

1. With docker: `docker-compose up` (docker should be installed)

Application will be available at http://127.0.0.1:8000


# Request example

`GET /api/store/products/`

##### Список продуктов.

http://localhost:8000/api/store/products/  

`POST /api/store/products/`

##### Добавить продукт.

http://localhost:8000/api/store/products/  

Пример JSON для запроса:
  
 
```
{
            "title": "macbook",
            "cost": "1200",
            "price": "2000",
            "quantity": "33"
        }
```

`PATCH /api/store/products/?id={PK PRODUCT}'`

##### Редактирование продукта.

http://localhost:8000/api/store/products/?id=2

Пример JSON для запроса:
  
 
```
{
            "quantity": "50"
        }
```

`POST /api/store/order/`

##### Создание заказа.

http://localhost:8000/api/store/order/  

Пример JSON для запроса:
  
 
```
{
            "products": [{"product": 1, "quantity": 4}]
        }
```

`PATCH /api/store/products/?id={PK PRODUCT}`

##### Редактирование статуса заказа.

http://localhost:8000/api/store/order/?id=3

Пример JSON для запроса:
  
 
```
{
            "status": "4"
        }
```


`POST /api/store/report/`

##### Получение отчета с выбранным периодом на почту.

http://localhost:8000/api/store/report/  

Пример JSON для запроса:
  
 
```
{
    "date_start": "2020-10-10",
    "date_end": "2020-11-11",
    "email": "test123@yandex.ru"
}
        
```

### ТЗ

![image](https://user-images.githubusercontent.com/74962029/138147791-39d64249-7db7-4fd9-bafa-d9818eac05b4.png)
![image](https://user-images.githubusercontent.com/74962029/138147834-74d5ad3a-b8d2-46e1-a17d-e6d1b1e9afa8.png)

