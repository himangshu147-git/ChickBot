import os
import discord
from discord.ext.commands import when_mentioned_or

from Core import Bot
from Core.Help import PaginatedHelpCommand

bot = Bot(
            command_prefix=when_mentioned_or("_",),
            intents=discord.Intents.all(),
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                users=True,
                roles=False,
                replied_user=True
                ),
            help_command=PaginatedHelpCommand()
)

if __name__ == "__main__":
    bot.run(bot.config.token)
    if KeyboardInterrupt:
        bot.logger.info("Shutting Down...")
        os._exit(0)