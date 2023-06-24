from __future__ import annotations
from Core import Bot
from .dev import Developer

async def setup(bot: Bot) -> None:
    await bot.add_cog(Developer(bot))
