import argparse
import asyncio

from queues import RabbitQueue
from senders.telegram import Telegram


async def main():
    parser = argparse.ArgumentParser(description='client data')
    parser.add_argument('id', type=int, help='client id')
    parser.add_argument('hash', type=str, help='client hash')
    parser.add_argument('phone', type=str, help='client phone')
    args = parser.parse_args()

    in_queue = RabbitQueue(port=5672, dispatcher=True)
    await in_queue.start()

    out_queue = RabbitQueue(port=5672)
    await out_queue.start()

    telegram = Telegram(args.phone, args.id, args.hash, in_queue, out_queue)
    await telegram.login()

    io_loop = asyncio.get_event_loop()
    io_loop.create_task(telegram.listen_telegram())
    listen = io_loop.create_task(telegram.listen_queue())

    await listen


if '__main__' == __name__:
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
