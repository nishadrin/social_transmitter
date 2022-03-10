import asyncio
import sys
from typing import Optional, Dict

from telethon import events, errors

from .own_telethon.telegram_client import OwnTelegramClient


class Telegram:
    __slots__ = ['id', 'hash', 'phone', 'dispatcher_queue', 'name', 'connect',
                 'telegram_queue', 'in_queue_name', 'out_queue_name']

    def __init__(self, phone: str, id: int, hash: str, dispatcher_queue,
                       telegram_queue) -> None:
        self.id = id
        self.hash = hash
        self.dispatcher_queue = dispatcher_queue
        self.telegram_queue = telegram_queue
        self.phone = phone
        self.name = f'telegram.{self.phone}'

        self.in_queue_name = f'in.{self.name}' # todo
        self.out_queue_name = f'out.{self.name}' # todo

    async def __call__(self, ):
        await self.login()
        await self.start_telegram()

    async def get_code(self) -> int:
        await self.add_to_queue({
            'phone': self.phone,
        })
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
            print(e)
            await self.add_to_queue({
                'id': self.id,
                'hash': self.hash,
                'phone': self.phone,
                'error': 'wrong code',
            })
            await self.stop()
        except KeyboardInterrupt:
            await self.stop()
            sys.exit()
        except Exception:
            await self.stop()
            raise Exception

    async def logout(self):
        await self.connect.log_out()

    async def stop(self) -> None:
        await self.connect.disconnect()

    async def start_telegram(self):
        loop = asyncio.get_event_loop()
        telegram = loop.create_task(self.listen_telegram())
        await telegram

    async def listen(self) -> None:
        try:
            loop = asyncio.get_event_loop()
            queue = loop.create_task(self.listen_queue())
            await queue
        except Exception:
            loop.stop()
            loop.close()
            raise Exception

    async def listen_telegram(self) -> None:
        connect = self.connect

        @connect.on(events.NewMessage(incoming=True))
        async def input_handler(event):
            await self.add_to_queue(await self.message_handler(event))

    async def listen_queue(self) -> Optional[int]:
        _queue, message = await self.telegram_queue.listen(self.out_queue_name)
        if 'code' in message.keys():
            return int(message['code'])
        if 'user' in message.keys() and 'text' in message.keys():
            await self.send_message(message['user'], message['text'])

    async def get_messages(self) -> None:  # todo get history of messages
        pass

    async def send_message(self, user, text) -> None:
        await self.connect.send_message(user, text)

    @staticmethod
    async def message_handler(event) -> Dict:
        sender = await event.get_sender()
        # todo attachments
        user = sender.phone if sender.username is None else sender.username

        return {
            'user': sender.id if user is None else user,
            'text': event.message.text if event.message.text else None,
            'attachment': event.message.file if event.message.file else None,
        }

    async def add_to_queue(self, text) -> None:
        await self.dispatcher_queue.add(self.in_queue_name, text)
