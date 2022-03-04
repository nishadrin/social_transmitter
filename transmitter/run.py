import asyncio
import sys
import argparse

from transmitter.queues.redis import RedisQueue
from transmitter.senders.telegram import Telegram


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

    queue = RedisQueue(db=1)
    await queue()
    queue_to_listen = RedisQueue(db=2)
    await queue_to_listen()

    telegram = Telegram(args.id, args.hash, args.phone, queue)
    await telegram.login(get_code)
    await telegram.listen(queue)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
