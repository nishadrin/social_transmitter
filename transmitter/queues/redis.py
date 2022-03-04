import aioredis


class RedisQueue:
    __slots__ = [
        'url',
        'connect',
    ]

    def __init__(self, host: str = 'localhost', port: str = '6379',
                 username: str = None, password: str = None,
                 db: int = None) -> None:
        self.url = f'redis://'
        if all((username, password)):
            self.url += f'{username}:{password}@'
        self.url += host
        if port:
            self.url += f':{port}'
        if db:
            self.url += f'/{db}'

    async def __call__(self) -> None:
        await self.start()

    async def start(self) -> None:
        try:
            self.connect = await aioredis.from_url(self.url)
        except Exception:
            await self.close()
            raise Exception

    async def close(self) -> None:
        await self.connect.close()

    async def listen(self, name) -> str:
        while True:
            return await self.consume(name)

    async def add(self, name, data) -> None:
        await self.produce(name, data)

    async def produce(self, name, data) -> None:
        await self.connect.lpush(name, data)

    async def consume(self, name) -> str:
        return await self.connect.brpop(name)
