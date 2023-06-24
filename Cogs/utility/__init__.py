from .utility import Utility

async def setup(bot):
    await bot.add_cog(Utility(bot))