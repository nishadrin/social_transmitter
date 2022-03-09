import asyncio
import sys
from typing import Dict


class DispatcherHandler:
    __slots__ = ['message', 'data']

    def __call__(self, message, text) -> Dict:
        self.message = message

        return self.get_data(text)

    def get_data(self, text: str, file: bytes=None) -> Dict:
        if 'phone' in self.message.keys():
            self.data = {
                'phone': self.message['phone'],
                'code': text,
            }
        if 'user' in self.message.keys() and 'text' in self.message.keys():
            self.data = {
                'user': self.message["user"],
                'text': text,
                'attachment': None,
            }

        return self.data


class Dispatcher:
    __slots__ = ['dispatcher_queue', 'telegram_queue', '_handler',
                 'in_queue_name', 'out_queue_name', ]

    def __init__(self, dispatcher_queue, telegram_queue, name) -> None:
        self.dispatcher_queue = dispatcher_queue
        self.telegram_queue = telegram_queue
        self._handler = DispatcherHandler()

        self.in_queue_name = f'in.{name}' # todo
        self.out_queue_name = f'out.{name}' # todo

    async def __call__(self):
        await self.listen()

    @staticmethod
    async def get_data():
        return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)

    async def listen(self):
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.listen_queue())
        except Exception:
            loop.close()
            raise Exception

    async def listen_queue(self):
        while True:
            _queue, message = await self.dispatcher_queue.listen(
                self.in_queue_name)

            if 'phone' in message.keys():
                print('Введите код: ')
            else:
                print(f'Клиент {message["user"]}: {message["text"]}')
                print(f'Введите сообщение для {message["user"]}: ')

            text = await self.get_data()
            text = text[:-1] # delete '\n' in the end of line

            self._handler(message, text)
            await self.add_to_queue(self.out_queue_name,
                                    self._handler.data)

    async def add_to_queue(self, name, text) -> None:
        await self.telegram_queue.add(name, text)
