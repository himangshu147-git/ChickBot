
import wavelink
from Core import Bot, Cog, Context



class Music(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        try:
            wavelink.NodePool.get_node()
        except wavelink.NodeStatus.DISCONNECTED as e:
            await ctx.send(f"{e}")
            return False
        return True