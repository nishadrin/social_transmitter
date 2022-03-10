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

    dispatcher_queue = RabbitQueue(port=5672, dispatcher=True)
    telegram_queue = RabbitQueue(port=5672)


    telegram = Telegram(args.phone, args.id, args.hash, dispatcher_queue,
                        telegram_queue)
    await telegram()
    await dispatcher_queue()
    await telegram_queue()
    while True:

        await telegram.listen()

    await telegram.send_message(153314285, 'hello')
    # await telegram.logout()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
