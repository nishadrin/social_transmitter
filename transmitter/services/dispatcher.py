import asyncio
import sys
from typing import Dict

from social_transmitter.transmitter.services.system import JsonWrapper


class DispatcherHandler:
    __slots__ = ['message', 'data']

    def __call__(self, message, text) -> Dict:
        self.message = message

        return self.get_data(text)

    def get_data(self, text: str, file: bytes=None) -> Dict:
        if 'phone' in self.message.keys():
            data = {
                'phone': self.message['phone'],
                'code': text,
            }
        if 'user_id' in self.message.keys() and 'text' in self.message.keys():
            print(f'Клиент с id {self.message["user_id"]}: \
{self.message["text"]}')
            data = {
                'user_id': self.message["user_id"],
                'text': text,
                'attachment': None,
            }
        self.data = data

        return self.data


class Dispatcher(JsonWrapper):
    __slots__ = ['dispatcher_queue', 'telegram_queue', ]

    def __init__(self, dispatcher_queue, telegram_queue) -> None:
        self.dispatcher_queue = dispatcher_queue
        self.telegram_queue = telegram_queue
        self._handler = DispatcherHandler

    async def __call__(self):
        await self.listen()

    async def get_data(self):
        return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)

    async def listen(self):
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.listen_queues())
        except Exception:
            loop.close()
            raise Exception

    async def listen_queues(self):
        while True:
            keys = await self.dispatcher_queue.connect.keys()
            for key in keys:
                _queue, message = await self.dispatcher_queue.listen(key)
                _queue, message = _queue.decode(), self.json_loads(message.decode())

                if 'phone' in message.keys():
                    print('Введите код: ')
                else:
                    print(f'Введите сообщение для {key}: ')

                text = await self.get_data()

                text = text[:-1] # delete '\n' in the end of line

                handler = DispatcherHandler()
                data = handler(message, text)

                await self.add_to_queue(key, self.json_dumps(data))

    async def add_to_queue(self, name, text) -> None:
        await self.telegram_queue.add(name, text)
