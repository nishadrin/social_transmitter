import sys

from telethon import events, errors

from .own_telethon.telegram_client import OwnTelegramClient


class Telegram(OwnTelegramClient):
    __slots__ = ['id', 'hash', 'phone', 'connect', 'name', 'in_queue',
                 'out_queue', 'in_queue_name', 'out_queue_name', 'in_data', ]

    def __init__(self, phone: str, id: int, hash: str, in_queue,
                 out_queue) -> None:
        self.id = id
        self.hash = hash
        self.phone = phone
        self.in_queue = in_queue
        self.out_queue = out_queue

        self.name = f'telegram.{self.phone}'
        self.in_data = {}
        self.in_queue_name = f'in.{self.name}'  # todo
        self.out_queue_name = f'out.{self.name}'  # todo

    async def send_reg_status(self, is_register=True):
        data = {
            'phone': self.phone,
            'is_register': is_register,
        }
        await self.in_queue.add(self.in_queue_name, data)

    async def login(self) -> None:
        try:
            self.connect = OwnTelegramClient(self.name, self.id, self.hash)

            if not self.connect._authorized or self.connect._authorized is None:
                await self.send_reg_status(is_register=False)
                await self.connect.start(phone=self.phone,
                                         code_callback=self.listen_queue)
            else:
                await self.send_reg_status()
        except (errors.PhoneCodeEmptyError,
                errors.PhoneCodeExpiredError,
                errors.PhoneCodeHashEmptyError,
                errors.PhoneCodeInvalidError) as e:
            print(e)
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

    async def listen_telegram(self) -> None:
        connect = self.connect

        @connect.on(events.NewMessage(incoming=True))
        async def input_handler(event):
            sender = await event.get_sender()
            user = sender.phone if sender.username is None else sender.username
            user = sender.id if user is None else user
            text = event.message.text if event.message.text else None
            data = {
                'user': user,
                'text': text,
            }
            await self.in_queue.add(self.in_queue_name, data)

    async def listen_queue(self):
        stop = False
        while not stop:
            _queue, data = await self.out_queue.listen(self.out_queue_name)
            if 'user' in data.keys() and 'text' in data.keys():
                await self.send_message(data['user'], data['text'])
            if 'phone' in data.keys():
                if data['phone'] is None:
                    await self.send_reg_status()
                elif 'code' in data.keys():
                    await self.send_reg_status()
                    stop = True
                    return data['code']

    async def send_message(self, user, text) -> None:
        await self.connect.send_message(user, text)
