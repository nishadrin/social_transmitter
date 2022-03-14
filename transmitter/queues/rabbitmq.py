__all__ = ['RabbitQueue', ]

import json
from typing import Dict, Tuple

from aio_pika import ExchangeType, connect_robust, Message


class RabbitQueue:
    __slots__ = ['url', 'connect', 'channel', 'dispatcher', ]

    def __init__(self, url='127.0.0.1', port=None, username='guest',
                 password='guest', dispatcher=False):
        self.url = f'amqp://{username}:{password}@{url}'
        if port is not None:
            self.url += f':{port}'
        self.url += '/'
        self.dispatcher = dispatcher

    async def start(self) -> None:
        try:
            self.connect = await connect_robust(self.url)
            self.channel = await self.connect.channel()
        except Exception:
            await self.close()
            raise Exception

    async def close(self) -> None:
        await self.connect.close()

    async def listen(self, name, auto_delete=True) -> Tuple[str, Dict]:
        queue = await self.channel.declare_queue(name,
                                                 auto_delete=auto_delete,
                                                 durable=True, )

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    if queue.name in message.body.decode():
                        break

                    # print(f'\nВ {queue.name} добавили {json.loads(message.body.decode())}')
                    return queue.name, json.loads(message.body.decode())

    async def add(self, name, data) -> None:
        exchange = await self.channel.declare_exchange(name,
                                                       ExchangeType.TOPIC,
                                                       durable=True, )
        queue = await self.channel.declare_queue(name,
                                                 auto_delete=True,
                                                 durable=True, )
        await queue.bind(exchange, queue.name)
        # print(f'\nДобавлено {data} в очередь {queue.name}')
        await exchange.publish(
            Message(json.dumps(data).encode(), content_type='text/plain'),
            routing_key=queue.name,
        )
