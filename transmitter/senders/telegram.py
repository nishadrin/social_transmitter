import asyncio
from typing import Optional

from telethon import events, errors

from social_transmitter.transmitter.senders.own_telethon.telegram_client import \
    OwnTelegramClient
from social_transmitter.transmitter.services.system import JsonWrapper


class Telegram(JsonWrapper):
    __slots__ = ['id', 'hash', 'phone', 'dispatcher_queue', 'name', 'connect',
                 'telegram_queue']

    def __init__(self, id: int, hash: str, phone: str,
                 dispatcher_queue, telegram_queue) -> None:
        self.id = id
        self.hash = hash
        self.phone = phone
        self.dispatcher_queue = dispatcher_queue
        self.telegram_queue = telegram_queue
        self.name = f'telegram{self.phone}'

    async def __call__(self):
        await self.login()
        await self.listen()

    async def get_code(self) -> str:
        await self.add_to_queue(self.json_dumps({
            'phone': self.phone,
        }))
        return await self.listen_queue()

    async def login(self) -> None:
        try:
            self.connect = OwnTelegramClient(self.name, self.id, self.hash)
            await self.connect.start(phone=self.phone,
                                     code_callback=self.get_code)
        except (errors.PhoneCodeEmptyError,
                errors.PhoneCodeExpiredError,
                errors.PhoneCodeHashEmptyError,
                errors.PhoneCodeInvalidError) as e:
            print(e.text)
            await self.add_to_queue(self.json_dumps({
                'id': self.id,
                'hash': self.hash,
                'phone': self.phone,
                'error': 'wrong code',
            }))
            await self.stop()
            sys.exit()
        except KeyboardInterrupt:
            await self.stop()
        except Exception:
            await self.stop()
            raise Exception

    async def logout(self):
        await self.connect.log_out()

    async def stop(self) -> None:
        await self.connect.disconnect()

    async def listen(self) -> None:
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.listen_telegram())
            loop.create_task(self.listen_queue())
        except Exception:
            loop.close()
            raise Exception

    async def listen_telegram(self) -> None:
        connect = self.connect

        @connect.on(events.NewMessage(incoming=True))
        async def input_handler(event):
            await self.add_to_queue(self.message_handler(event))

    async def listen_queue(self) -> Optional[int]:
        while True:
            _queue, message = await self.telegram_queue.listen(self.name)
            _queue, message = _queue.decode(), self.json_loads(message.decode())
            if 'code' in message.keys():
                return int(message['code'])
            if 'user_id' in message.keys() and 'text' in message.keys():
                await self.send_message(int(message['user_id']),
                                        message['text'])

    async def get_messages(self) -> None:  # todo get history of messages
        pass

    async def send_message(self, member, text) -> None:
        await self.connect.send_message(member, text)

    def message_handler(self, event) -> str:
        # todo attachments
        return self.json_dumps({
            'user_id': event.message.peer_id.user_id,
            'text': event.message.text if event.message.text else None,
            'attachment': event.message.file if event.message.file else None,
        })

    async def add_to_queue(self, text) -> None:
        await self.dispatcher_queue.add(self.name, text)
