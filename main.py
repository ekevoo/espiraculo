#!/usr/bin/env python3
import asyncio
import sys
from dataclasses import dataclass, field
from typing import Optional, List

import discord
import yamldataclassconfig.config


async def main():
    config = Config()
    config.load("config.yaml")
    async with Client(config) as client:
        asyncio.create_task(read_input(client))
        await asyncio.sleep(10)
        print("10 seconds passed, exiting")


class Client(discord.Client):
    last_channel: Optional[discord.TextChannel] = None

    def __init__(self, config: "Config"):
        self.__config = config
        super().__init__()

    async def __aenter__(self):
        await self.login(self.__config.discord_token)
        asyncio.create_task(self.connect())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()

    async def on_ready(self):
        print(f"Logged on as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        self.last_channel = message.channel
        print(f"Message from {message.author}: {message.content}")


async def read_input(client: Client):
    loop = asyncio.get_running_loop()
    msg = await loop.run_in_executor(None, sys.stdin.readline)
    while msg != "/quit":
        if client.last_channel:
            await client.last_channel.send(f"I've been told that {msg}")
        msg = await loop.run_in_executor(None, sys.stdin.readline)


@dataclass
class Config(yamldataclassconfig.config.YamlDataClassConfig):
    discord_token: str = ""
    owners: List[str] = field(default_factory=list)


if __name__ == "__main__":
    asyncio.run(main())
