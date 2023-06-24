from __future__ import annotations
import os, sys, asyncio
from typing import Literal
import discord
from discord.ext import commands
import traceback
from Core import Cog, Context, Bot

class Developer(Cog):
    """Developer commands"""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="🛠️")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def cog(self, ctx: Context, action: Literal["load", "unload", "reload"], *, cog: str) -> None:
        if action == "load":
            try:
                await self.bot.load_extension("Cogs."+cog)
                x = await ctx.send(f"Loading Cogs.{cog}...", delete_after=15)
                await asyncio.sleep(3)
                await x.edit(content=f"Loaded Cogs.{cog}.", delete_after=15)
            except Exception as e:
                await ctx.send(f"```py\n{e}\n```", delete_after=15)
                return
        if action == "unload":
            try:
                await self.bot.unload_extension("Cogs."+cog)
                x = await ctx.send(f"Unloading Cogs.{cog}...", delete_after=15)
                await asyncio.sleep(3)
                await x.edit(content=f"Unloaded Cogs.{cog}.", delete_after=15)
            except Exception as e:
                await ctx.send(f"```py\n{e}\n```", delete_after=15)
                return
        if action == "reload":
            try:
                await self.bot.unload_extension("Cogs."+cog)
                await self.bot.load_extension("Cogs."+cog)
                x = await ctx.send(f"🔄️ Reloading Cogs.{cog}...", delete_after=15)
                await asyncio.sleep(3)
                await x.edit(content=f"✅ Reloaded Cogs.{cog}.", delete_after=15)
            except Exception as e:
                await ctx.send(f"```py\n{e}\n```", delete_after=15)
                traceback.print_exc()
                return
            

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sync(
        self, ctx: Context, scope: Literal["global", "guild"]
    ) -> None:
        if scope == "global":
            await ctx.send(
                "Synchronizing. It may take more then 30 sec", delete_after=15
            )
            synced = await self.bot.tree.sync()
            await ctx.send(
                f"{len(synced)} Slash commands have been globally synchronized."
            )
            return
        elif scope == "guild":
            await ctx.send(
                "Synchronizing. It may take more then 30 sec", delete_after=15
            )
            self.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(
                f"{len(synced)} Slash commands have been synchronized in this guild.",
                delete_after=15,
            )
            return
        await ctx.send("The scope must be `global` or `guild`.", delete_after=15)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unsync(
        self, ctx: Context, scope: Literal["global", "guild"]
    ) -> None:
        if scope == "global":
            await ctx.send("Unsynchronizing...", delete_after=15)
            self.bot.tree.clear_commands(guild=None)
            unsynced = await self.bot.tree.sync()
            await ctx.send(
                f"{len(unsynced)} Slash commands have been globally unsynchronized.",
                delete_after=15,
            )
            return
        elif scope == "guild":
            await ctx.send("Unsynchronizing...", delete_after=15)
            self.bot.tree.clear_commands(guild=ctx.guild)
            unsynced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(
                f"{len(unsynced)} Slash commands have been unsynchronized in this guild.",
                delete_after=15,
            )
            return
        await ctx.send("The scope must be `global` or `guild`.", delete_after=15)