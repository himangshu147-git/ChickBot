from typing import Optional
import discord
import wavelink
from discord.ext import commands
from discord.interactions import Interaction
from Core import Context, Bot

class MusicView(discord.ui.View):
    message: Optional[discord.Message]
    def __init__(
        self, vc: discord.VoiceChannel, 
        *, 
        timeout: Optional[float] = None, 
        ctx: Context
    ):
        super().__init__(timeout=timeout)
        self.vc = vc
        self.ctx = ctx
        self.bot: Bot = self.ctx.bot
        self.player: wavelink.Player = self.ctx.voice_client

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id not in self.bot.get_channel(self.vc).voice_states.keys():
            await self.ctx.send(
                "You must be in the bot's voice channel to use this command.",
                ephemeral=True,
            )
            return False
        return True