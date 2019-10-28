import datetime
import logging
import os
import sys
from collections.__init__ import Counter

import aiohttp
import coloredlogs
import discord
import psutil
import yaml
# import asyncpg
from rethinkdb import RethinkDB

from utils.config.config import get_icon, get_config

r = RethinkDB()
r.set_loop_type("asyncio")
logger = logging.getLogger()


def setup_logger():
    with open("config/logging.yml", "r") as log_config:
        config = yaml.safe_load(log_config)

    coloredlogs.install(
        level="INFO",
        logger=logger,
        fmt=config["formats"]["console"],
        datefmt=config["formats"]["datetime"],
        level_styles=config["levels"],
        field_styles=config["fields"]
    )

    file = logging.FileHandler(filename=f"logs/bot.log", encoding="utf-8", mode="w")
    file.setFormatter(logging.Formatter(config["formats"]["file"]))
    logger.addHandler(file)
    return logger


def setup_bot(bot):
    discord_log = logging.getLogger("discord")
    log = logging.getLogger("bot")
    discord_log.setLevel(logging.CRITICAL)
    bot.log = log
    log.info(f"\n{get_icon()}\nLoading....")
    bot.debug = any("debug" in arg.lower() for arg in sys.argv)
    starter_modules(bot)
    bot.conn = bot.loop.run_until_complete(r.connect("localhost", db="Naila", port=28015))
    # credentials = {
    #     "user": os.environ["POSTGRES_USER"],
    #     "password": os.environ["POSTGRES_PASS"],
    #     "database": "Naila",
    #     "host": "localhost"
    # }
    # bot.pool = bot.loop.run_until_complete(asyncpg.create_pool(**credentials))
    bot.config = get_config
    # bot.log.info(f"Postgres connected to database ({bot.pool._working_params.database})"
    #              f" under the ({bot.pool._working_params.user}) user")
    bot.uptime = datetime.datetime.utcnow()
    bot.version = {
        "bot": bot.config()["version"],
        "python": sys.version.split(" ")[0],
        "discord.py": discord.__version__
    }
    bot.counter = Counter()
    bot.commands_used = Counter()
    bot.process = psutil.Process()
    bot.session = aiohttp.ClientSession(loop=bot.loop)
    bot.color = bot.config()["colors"]["main"]
    bot.error_color = bot.config()["colors"]["error"]
    if bot.debug:
        discord_log.setLevel(logging.INFO)


def starter_modules(bot):
    paths = ["modules/Events", "modules/Cogs"]
    for path in paths:
        for file in os.listdir(path):
            try:
                if file.endswith(".py"):
                    file_name = file[:-3]
                    path = path.replace("/", ".")
                    bot.load_extension(f"{path}.{file_name}")
            except Exception as e:
                bot.log.error(f"Failed to load {file}: {e}")