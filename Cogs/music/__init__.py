from .music import Music 
from Core import Bot   

async def setup(bot: Bot):
    await bot.add_cog(Music(bot))
