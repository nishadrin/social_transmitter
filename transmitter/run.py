import asyncio
import sys
import argparse

from social_transmitter.transmitter.senders.telegram import Telegram

from social_transmitter.transmitter.queues.redis import RedisQueue
from social_transmitter.transmitter.services.dispatcher import Dispatcher


async def get_code() -> str:
    print('Введите код: ')
    return await asyncio.get_event_loop().run_in_executor(
        None, sys.stdin.readline)


async def main():
    # id: int = 0
    # hash: str = ''
    # phone: str = ''
    parser = argparse.ArgumentParser(description='client data')
    parser.add_argument('id', type=int, help='client id')
    parser.add_argument('hash', type=str, help='client hash')
    parser.add_argument('phone', type=str, help='client phone')
    args = parser.parse_args()

    dispatcher_queue = RedisQueue(db=1)
    await dispatcher_queue()

    telegram_queue = RedisQueue(db=2)
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
