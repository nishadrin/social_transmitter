import argparse
import asyncio

from services.dispatcher import Dispatcher
from queues.rabbitmq import RabbitQueue


async def main():
    parser = argparse.ArgumentParser(description='client data')
    parser.add_argument('phone', type=str, help='client phone')
    parser.add_argument('platform', default='telegram', type=str,
                        help='client platform')
    args = parser.parse_args()

    dispatcher_queue = RabbitQueue(port=5672, dispatcher=True)
    telegram_queue = RabbitQueue(port=5672)

    name = f'{args.platform}.{args.phone}'

    dispatcher = Dispatcher(dispatcher_queue, telegram_queue, name)

    while True:
        await dispatcher_queue()
        await telegram_queue()
        await dispatcher()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
