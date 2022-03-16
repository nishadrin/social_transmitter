import asyncio
from typing import Dict


class Dispatcher:
    """
    Обрабатывает входящие данные из очереди и отправляет сообщения от менеджера.
    """

    __slots__ = ['in_queue', 'out_queue', '_handler', 'in_queue_name',
                 'out_queue_name', 'users', 'phone', 'is_register',
                 'is_request_phone', 'is_send_code', ]

    def __init__(self, in_queue, out_queue, name) -> None:
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.users = set()
        self.phone = None
        self.is_register = False
        self.is_request_phone = False
        self.is_send_code = False

        self.in_queue_name = f'in.{name}'  # todo
        self.out_queue_name = f'out.{name}'  # todo

    @staticmethod
    async def get_data(text) -> str:
        """
        Асинхронный запуск функции input для отправки данных в очередь.
        """
        return await asyncio.get_event_loop().run_in_executor(None, input, text)

    async def add_to_queue(self, name: str, data: Dict) -> None:
        """
        добавить в очередь данные
        """
        await self.out_queue.add(name, data)

    async def listen_queue(self):
        """
        Прослушивает очередь и выполняет логику, согласно запросу из очереди.
        """
        stop = False
        while not stop:
            _queue, message = await self.in_queue.listen(self.in_queue_name)

            if 'phone' in message.keys():
                self.phone = message["phone"]
                self.is_register = message["is_register"]
                if not self.is_register:
                    print(f'\n{message["phone"]} ожидает код подтверждения')

            if 'user' in message.keys():
                self.users.add(message["user"])
                print(f'\nКлиент {message["user"]}: {message["text"]}')

    async def send_handler(self):
        """
        Отправляет данные в очередь, согласно логики.
        """
        while True:
            if self.phone is None:
                if not self.is_request_phone:
                    await self.add_to_queue(self.out_queue_name, {
                        'phone': self.phone,
                    })
                    self.is_request_phone = True
                else:
                    await asyncio.sleep(0)
            elif not self.is_register and not self.is_send_code:
                text = await self.get_data('Введите код: ')
                await self.add_to_queue(self.out_queue_name, {
                    'phone': self.phone,
                    'code': text,
                })
                self.is_send_code = True
            else:
                print(f'\nВсе пользователи: {self.users}')
                user = await self.get_data('Введите данные пользователя: ')
                text = await self.get_data(f'Ответить клиенту {user}: ')
                await self.add_to_queue(self.out_queue_name, {
                    'user': user,
                    'text': text,
                })
