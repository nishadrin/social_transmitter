import asyncio
import argparse

from senders.telegram import Telegram

from services.dispatcher import Dispatcher
from social_transmitter.transmitter.queues import RabbitQueue


async def main():
    parser = argparse.ArgumentParser(description='client data')
    parser.add_argument('id', type=int, help='client id')
    parser.add_argument('hash', type=str, help='client hash')
    parser.add_argument('phone', type=str, help='client phone')
    args = parser.parse_args()

    dispatcher_queue = RabbitQueue(port=25672, dispatcher=True)
    await dispatcher_queue()
    # надо бы разбить на 2 run.py
    telegram_queue = RabbitQueue(port=25672)
    await telegram_queue()

    dispatcher = Dispatcher(dispatcher_queue, telegram_queue)
    await dispatcher()

    telegram = Telegram(args.id, args.hash, args.phone,
                        dispatcher_queue, telegram_queue)
    await telegram()
    # await telegram.logout()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
