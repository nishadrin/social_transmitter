import sys

from telethon import events, errors

from .own_telethon.telegram_client import OwnTelegramClient


class Telegram(OwnTelegramClient):
    """
    Телеграм клиент, который слушает телеграм, и передает сообщения в очередь,
    а из очереди сообщений передает обратно в телеграм.
    Формат взаимодействия при авторизации:
    {
        'phone': Optional[str], в случае None - запрос статуса
        'code': str,
    }
    Формат передачи сообщений:
    {
        'user': str, - может содержать: username или user id
        'text': str,
    }
    """

    __slots__ = ['id', 'hash', 'phone', 'connect', 'name', 'in_queue',
                 'out_queue', 'in_queue_name', 'out_queue_name', 'in_data', ]

    def __init__(self, phone: str, id: int, hash: str, in_queue,
                 out_queue) -> None:
        self.id = id
        self.hash = hash
        self.phone = phone
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.is_register = False

        self.name = f'telegram.{self.phone}'
        self.in_data = {}
        self.in_queue_name = f'in.{self.name}'  # todo
        self.out_queue_name = f'out.{self.name}'  # todo

    async def send_reg_status(self) -> None:
        """
        Передает статус авотризации клиента в очередь.
        """
        data = {
            'phone': self.phone,
            'is_register': self.is_register,
        }
        await self.in_queue.add(self.in_queue_name, data)

    async def login(self) -> None:
        """
        Запуск и авторизизация клиента телеграм, отправка статуса авторизации
        в очередь.

        Авторизация происходит с помощью запроса кода через функцию, которая
        передается в code_callback.

        Перехватываем ошибки авторизации, в случае, если код не верный.
        """
        try:
            self.client = OwnTelegramClient(self.name, self.id, self.hash)
            await self.client.start(phone=self.phone,
                                     code_callback=self.listen_queue)
            if self.client.session.auth_key.key is not None:
                self.is_register = True
            await self.send_reg_status()
        except (errors.PhoneCodeEmptyError,
                errors.PhoneCodeExpiredError,
                errors.PhoneCodeHashEmptyError,
                errors.PhoneCodeInvalidError) as e:
            self.is_register = False
            print(e)
            await self.stop()
        except KeyboardInterrupt:
            await self.stop()
            sys.exit()
        except Exception:
            await self.stop()
            raise Exception

    async def logout(self):
        """
        Разлогиниться.
        """
        await self.client.log_out()

    async def stop(self) -> None:
        await self.client.disconnect()

    async def listen_telegram(self) -> None:
        """
        Прослушивание всех входящих сообщений из телеграма.
        """
        connect = self.client

        @connect.on(events.NewMessage(incoming=True))
        async def input_handler(event):
            sender = await event.get_sender()
            user = sender.phone if sender.username is None else sender.username
            user = sender.id if user is None else user
            text = event.message.text if event.message.text else None
            data = {
                'user': user,
                'text': text,
            }
            await self.in_queue.add(self.in_queue_name, data)

    async def listen_queue(self):
        """
        Слушаем очередь от диспетчера, и выполняем логику авторизации или
        отправляем сообщение.
        """
        stop = False
        while not stop:
            _queue, data = await self.out_queue.listen(self.out_queue_name)
            if 'user' in data.keys() and 'text' in data.keys():
                await self.send_message(data['user'], data['text'])
            if 'phone' in data.keys():
                if data['phone'] is None:
                    await self.send_reg_status()
                elif 'code' in data.keys():
                    stop = True
                    self.is_register = True
                    await self.send_reg_status()
                    return data['code']

    async def send_message(self, user: str, text: str) -> None:
        """
        Отправка сообщений.
        """
        await self.client.send_message(user, text)
