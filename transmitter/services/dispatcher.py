import asyncio
import sys
from typing import Dict


class DispatcherHandler:
    __slots__ = ['message', 'data']

    def __call__(self, text, message=None) -> Dict:
        self.message = message

        return self.get_dict(text)

    def get_dict(self, text: str, file: bytes=None) -> Dict:
        if self.message is None:
            self.data = {
                'user': 153314285,
                'text': 'некому посылать',
                'attachment': None,
            }
        else:
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
        print('get_data')
        return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)

    async def listen(self):
        try:
            loop = asyncio.get_event_loop()
            listen_queue = loop.create_task(self.listen_queue())
            # await listen_queue
        except Exception:
            loop.close()
            raise Exception

    async def listen_queue(self):
        _queue, message = await self.dispatcher_queue.listen(
            self.in_queue_name)

        if 'phone' in message.keys():
            print('Введите код: ')
        else:
            print(f'Клиент {message["user"]}: {message["text"]}')
            print(f'Введите сообщение для {message["user"]}: ')

        text = await self.get_data()
        text = text[:-1]  # delete '\n' in the end of line
        await self.add_to_queue(self.out_queue_name,
                                self._handler(text, message))

    async def add_to_queue(self, name, text) -> None:
        await self.telegram_queue.add(name, text)
