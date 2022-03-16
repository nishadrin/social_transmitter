Python 3.6.9+

Запуск 2-мя файлами:

`python3 dispetchet.py phone`

`python3 telegram.py id hash phone`

Данные:

- phone 79123456789
- id и hash можно получить по инструкции:
    1. авторизируемся в [telegram](https://my.telegram.org)
    2. переходим в [API development tools](https://my.telegram.org/apps)
    3. создаем новый app
    4. нажать на созданный app

RabbitMQ

Запуск:

`sudo docker run --rm -it --hostname my-rabbit -p 15672:15672 -p 5672:5672 rabbitmq:3-management`

Настройки:
- ip: 127.0.0.1
- port: 5672
- username: guest
- password: guest
