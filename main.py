import asyncio
import atexit
import os
from os.path import join, dirname

import discord
from discord.utils import oauth_url
from discord.ext.commands import AutoShardedBot as DiscordBot
from dotenv import load_dotenv

from utils.database.GuildSettings import Prefixes
from utils.config.setup_bot import setup_bot, setup_logger
from utils.ctx import CustomContext

load_dotenv(join(dirname(__file__), 'env/.env'))

perms = discord.Permissions(int(os.getenv("PERMS")))
description = "**Support server**: https://discord.gg/fox\n" \
              f"**Bot invite**:" \
              f" [Recommended perms]({oauth_url(os.getenv('CLIENT_ID'), permissions=perms)}) |" \
              f" [No perms]({oauth_url(os.getenv('CLIENT_ID'))})"


class Bot(DiscordBot):
    def __init__(self):
        atexit.register(lambda: asyncio.ensure_future(self.logout()))
        super().__init__(command_prefix=Prefixes.get, description=description, case_insensitive=True)
        setup_bot(self)
        try:
            self.loop.run_until_complete(self.start(os.getenv("TOKEN")))
        except (discord.errors.LoginFailure, discord.errors.HTTPException) as e:
            self.log.error(f"Shit: {repr(e)}", exc_info=False)
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.pool.close())
            self.loop.run_until_complete(self.logout())

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or CustomContext)

    if __name__ != "__main__":
        setup_logger()


if __name__ == "__main__":
    setup_logger()
    Bot()
