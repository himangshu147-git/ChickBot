import platform
import sys

import discord
import psutil

from discord.ext import commands
import typing
import config
from Core import Bot, Cog, Context
from Utils import LinkButton, LinkType


class Meta(Cog):
	"""Commands that provide information about the bot itself"""
	def __init__(self, bot: Bot):
		self.bot = bot

	@property
	def display_emoji(self) -> discord.PartialEmoji:
		return discord.PartialEmoji(name="ℹ️")

	@commands.hybrid_command(name="ping", description="Shows the bot's latency")
	async def ping(self, ctx: Context):
		"""Shows the bot's latency"""
		embed = discord.Embed(title="Pong!", color=self.bot.color)
		embed.description = f"Latency: {round(self.bot.latency * 100)}ms"
		await ctx.send(embed=embed)

	@commands.hybrid_command(name="about", description="Shows information about the bot")
	async def about(self, ctx: Context):
		"""Shows information about the bot"""
		embed = discord.Embed(title=f"{self.bot.user} | a discord bot", color=self.bot.color)
		embed.set_thumbnail(url=self.bot.user.display_avatar.url)
		embed.description = f"I have features such as moderation, music,  and more.\nYou can get more inforamtion using {ctx.prefix}help"
		embed.set_footer(text=f"Made with discord.py v{discord.__version__}")
		links = [
			LinkType("Support", config.support),
			LinkType("Invite", self.bot.invite_url),
		]
		await ctx.send(embed=embed, view=LinkButton(links))

	@commands.hybrid_command(name="stats", description="Shows the bot's stats")
	async def stats(self, ctx: Context):
		"""Shows the bot's stats"""
		async with ctx.typing():
			data = await self.bot.db.execute(
				"""
				SELECT invoked
				FROM cmd_stat 
				WHERE author = ?
				""", 
				(ctx.author.id,)
				)
			command_ran = await data.fetchone()
			global_cmd_ran = await self.bot.db.execute(
				"""
				SELECT SUM(invoked)
				FROM cmd_stat
				"""
			)
			global_cmd_ran = await global_cmd_ran.fetchone()
			msg_seen = await self.bot.db.execute(
				"""
				SELECT seen
				FROM msg
				"""
			)
			msg_seen = await msg_seen.fetchall()

			embed = discord.Embed(title="Bot | Stats", color=self.bot.color)
			embed.set_thumbnail(url=self.bot.user.display_avatar.url)
			embed.add_field(name="Guilds", value=f"`{len(self.bot.guilds)}`")
			embed.add_field(name="Users", value=f"`{len(self.bot.users)}`")
			embed.add_field(name="Commands", value=f"`{len(self.bot.commands)}`")
			embed.add_field(name="Command usage", value=f"`{command_ran[0]}` times by you\n`{global_cmd_ran[0]}` globally")
			embed.add_field(name="Messages seen", value=f"`{int(msg_seen[0][0])}`")
			embed.add_field(name="Ping", value=f"`{round(self.bot.latency * 1000)}`ms")
			embed.add_field(name="RAM", value=f"`{round(psutil.virtual_memory().percent)}%` used")
			embed.add_field(name="CPU", value=f"`{round(psutil.cpu_percent(5) / psutil.cpu_count())}%` used")
			embed.add_field(name="Python", value=f"`v{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}`")
			embed.add_field(name="Discord.py", value=f"`v{discord.__version__}`")
			embed.add_field(name="OS", value=f"`{platform.system()} v{platform.release()}`")

			links = [
				LinkType("Support", config.support),
				LinkType("Invite", self.bot.invite_url),
			]
			await ctx.send(embed=embed, view=LinkButton(links))