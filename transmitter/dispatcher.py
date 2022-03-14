import argparse
import asyncio

from services.dispatcher import Dispatcher
from queues.rabbitmq import RabbitQueue


async def main():
    parser = argparse.ArgumentParser(description='client data')
    parser.add_argument('phone', type=str, help='client phone')
    parser.add_argument('--platform', default='telegram', type=str,
                        help='client platform')
    args = parser.parse_args()

    in_queue = RabbitQueue(port=5672, dispatcher=True)
    await in_queue.start()

    out_queue = RabbitQueue(port=5672)
    await out_queue.start()

    name = f'{args.platform}.{args.phone}'
    dispatcher = Dispatcher(in_queue, out_queue, name)

    io_loop = asyncio.get_event_loop()
    in_listen = io_loop.create_task(dispatcher.listen_queue())
    out_data = io_loop.create_task(dispatcher.send_handler())
    await asyncio.gather(out_data, in_listen)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
