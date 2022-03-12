import asyncio
import sys
from typing import Dict


class Dispatcher:
    __slots__ = ['dispatcher_queue', 'telegram_queue', '_handler',
                 'in_queue_name', 'out_queue_name', 'users', 'phone',
                 'is_register', ]

    def __init__(self, dispatcher_queue, telegram_queue, name) -> None:
        self.dispatcher_queue = dispatcher_queue
        self.telegram_queue = telegram_queue
        self.users = []
        self.phone = None
        self.is_register = False

        self.in_queue_name = f'in.{name}' # todo
        self.out_queue_name = f'out.{name}' # todo

    async def __call__(self):
        await self.listen()

    @staticmethod
    async def get_data(text):
        return await asyncio.get_event_loop().run_in_executor(None, input, text)

    async def listen(self):
        try:
            loop = asyncio.get_event_loop()
            listen_queue = loop.create_task(self.listen_queue())
            send_handler = loop.create_task(self.send_handler())
            # await listen_queue
        except Exception:
            loop.close()
            raise Exception


    async def send_handler(self):
        if not self.is_register:
            await self.send_code(message['phone'])
        else:
            print(self.users)
            user = self.get_data('Введите данные пользователя: ')
            await self.send_input_message()

    async def send_code(self, phone):
        text = await self.get_data('Введите код: ')
        await self.add_to_queue(self.out_queue_name, {
            'phone': phone,
            'code': text,
        })

    async def send_input_message(self):
        attachment = None
        text = await self.get_data(f'Ответить клиенту {self.user}: ')
        await self.add_to_queue(self.out_queue_name, {
            'user': self.user,
            'text': text,
            'attachment': attachment,
        })

    async def listen_queue(self):
        _queue, message = await self.dispatcher_queue.listen(
            self.in_queue_name)

        if 'phone' in message.keys():
            print(f'{message["phone"]} ожидает код подтверждения')
        if 'user' in message.keys():
            self.is_register = True
            self.users.append(message["user"])
            print(f'Клиент {message["user"]}: {message["text"]}')

    async def add_to_queue(self, name, text) -> None:
        await self.telegram_queue.add(name, text)
