from .Mod import Mod
from Core import Bot

async def setup(bot: Bot):
    await bot.add_cog(Mod(bot))