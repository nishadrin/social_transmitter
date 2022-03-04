import asyncio
import json
import sys
from typing import Dict

from telethon import events, errors

from transmitter.senders.own_telethon.telegram_client import OwnTelegramClient


class Telegram:
    def __init__(self, id: int, hash: str, phone: str, queue) -> None:
        self.id = id
        self.hash = hash
        self.phone = phone
        self.queue = queue
        self.name = f'telegram{self.phone}'

    @staticmethod
    async def get_code() -> str:
        print('Введите код: ')
        return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)

    async def login(self, get_code) -> None:
        try:
            self.connect = OwnTelegramClient(self.name, self.id, self.hash)
            await self.connect.start(phone=self.phone, code_callback=get_code)
        except (errors.PhoneCodeEmptyError,
                errors.PhoneCodeExpiredError,
                errors.PhoneCodeHashEmptyError,
                errors.PhoneCodeInvalidError) as e:
            await self.add_to_queue(self.json_dumps({
                'id': self.id,
                'hash': self.hash,
                'phone': self.phone,
                'error': 'wrong code',
            }))
            await self.stop()
            await sys.exit()
        except KeyboardInterrupt:
            await self.stop()
        except Exception:
            await self.stop()
            raise Exception

    async def logout(self):
        await self.connect.log_out()

    async def stop(self) -> None:
        await self.connect.disconnect()

    async def listen(self, queue) -> None:
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.listen_telegram())
            loop.create_task(self.listen_queue(queue))
        except Exception:
            loop.close()
            raise Exception

    async def listen_telegram(self) -> None:
        connect = self.connect

        @connect.on(events.NewMessage(incoming=True))
        async def input_handler(event):
            await self.add_to_queue(self.message_handler(event))

    async def listen_queue(self, queue) -> None:
        while True:
            _queue, message = await queue.listen(self.name)
            _queue, message = _queue.decode(), self.json_loads(message.decode())
            # todo wrong code
            await self.send_message(int(message['user_id']), message['text'])

    async def get_messages(self) -> None: # todo get history of messages
        pass

    async def send_message(self, member, text) -> None:
        await self.connect.send_message(member, text)

    @staticmethod
    def json_loads(data: Dict) -> str:
        print()
        print(f'input data: {json.loads(data)}')
        return json.loads(data)

    @staticmethod
    def json_dumps(data: Dict) -> str:
        print()
        print(f'output data: {data}')
        return json.dumps(data)

    def message_handler(self, event) -> str:
        # todo attachments
        return self.json_dumps({
            'user_id': event.message.peer_id.user_id,
            'text': event.message.text if event.message.text else None,
            'attachment': event.message.file if event.message.file else None,
        })

    async def add_to_queue(self, text) -> None:
        await self.queue.add(self.name, text)
