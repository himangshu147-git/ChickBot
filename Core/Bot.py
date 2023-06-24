import asyncio
import logging
import random
import re
from typing import Callable, Coroutine, List

import aiohttp
import aiosqlite
import discord
import wavelink
from discord.ext import commands, tasks
from discord.gateway import DiscordWebSocket
from discord.message import Message

import config as cf
from Core.Context import Context
from Utils import LinkButton, LinkType
from Utils.Webhook import error, startup
from .Help import PaginatedHelpCommand

l = logging.getLogger("discord.gateway")
l.propagate = False

logger = logging.getLogger("discord.client")
hdlr = logging.StreamHandler()
frmt = logging.Formatter(
    "[{asctime}] [{levelname:<10}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
hdlr.setFormatter(frmt)
logger.addFilter(hdlr)

on_startup: List[Callable[["Bot"], Coroutine]] = []

class Bot(commands.Bot):
    """`A custom implementation of commands.Bot class.`
       -----------------------------------------------
    """
    def __init__(
            self, 
            *args, 
            **kwargs
            ) -> None:
        super().__init__(
            *args, 
            **kwargs
            )
        self.wavelink = wavelink.NodePool()
        self.add_listener(self.on_mention, "on_message")
        
    @property
    def config(self) -> cf:
        return __import__("config")

    @property
    def logger(self):
        return logger
    
    @property
    def color(self):
        return self.config.color
    
    @property
    def invite_url(self) -> str:
        return discord.utils.oauth_url(
            self.user.id,
            permissions=discord.Permissions(10430261488759),
            scopes=("bot", "applications.commands"),
            disable_guild_select=False,
        )
    
   
    @on_startup.append
    async def session(self) -> None:
        self.session = aiohttp.ClientSession()
    
    @on_startup.append
    async def init_db(self) -> None:
        self.db = await aiosqlite.connect("db/database.db")
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS cmd_stat (
                author INTEGER PRIMARY KEY,
                invoked INTEGER DEFAULT 0
            )
            """

        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS msg (
                seen INTEGER DEFAULT 0
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS music(
                guild_id INTEGER PRIMARY KEY,
                text_channel_id INTEGER DEFAULT 0,
                voice_channel_id INTEGER DEFAULT 0,
                msg_id INTEGER DEFAULT 0
            )
            """
        )


        await self.db.commit()

    async def setup_hook(self):
        for coro in on_startup:
            self.loop.create_task(coro(self))
            self.logger.info(f"Starting {coro.__name__}")
        await __import__("asyncio").sleep(8)
        synced = await self.tree.sync()
        self.logger.info(f"Successfully synced {len(synced)} command.")
        await startup(msg=f"Successfully synced {len(synced)} command.", session=self.session)

    async def on_ready(self) -> None:
        """Setup the bot when it is ready."""
        self.logger.info(f"Logged in as {self.user}")
        await startup(msg=f"Logged in as {self.user}", session=self.session)
        await self.change_presence(status=discord.Status.offline)
        # self.status_task.start()

    async def get_context(self, message: Message, *, cls=Context) -> Context:
        return await super().get_context(message, cls=cls)

    # @tasks.loop(minutes=0.3)
    # async def status_task(self) -> None:
    #     """
    #     Setup the game status task of the bot.
    #     """
    #     guilds=len(self.guilds)
    #     user=len(self.users)
    #     statuses= ["_guilds_ guilds", "_users_ users", "_help", "_h", "@Chick"]
    #     statuses=[status.replace("_guilds_", str(guilds)).replace("_users_", str(user)) for status in statuses]
    #     await self.change_presence(activity=discord.Game(random.choice(statuses)))
    #     await asyncio.sleep(1)
        
    
    # async def get_context(self, origin: Union[discord.Interaction, discord.Message], /, *, cls=Context) -> Context:
    #     return await super().get_context(origin, cls=cls)

    async def process_commands(self, message: discord.Message):
        if message.content and message.guild is not None:
            ctx = await self.get_context(message)
            if ctx.command is None:
                return
            await self.invoke(ctx)
    
    async def on_command(self, ctx: Context):
        if ctx.interaction:
            return
        c = await self.db.execute(
            """
            SELECT invoked 
            FROM cmd_stat 
            WHERE author = ?
            """, 
            (ctx.author.id,)
            )
        r = await c.fetchone()
        if r is None:
            await self.db.execute(
                """
                INSERT INTO cmd_stat (author, invoked)
                VALUES (?, 1)
                """,
                (ctx.author.id,)
                )
        else:
            await self.db.execute(
                """
                UPDATE cmd_stat
                SET invoked = ?
                WHERE author = ?
                """,
                (r[0]+1, ctx.author.id)
                )
        await self.db.commit()
        await ctx.message.add_reaction("✅")
        
        def check(payload: discord.RawReactionActionEvent):
            if payload.message_id == ctx.message.id and payload.user_id == ctx.author.id:
                return True
            
            if payload.message_id == ctx.message.id and payload.emoji.name == "✅":
                return True
        x = await self.wait_for("raw_reaction_add", check=check)
        if x:
            await ctx.message.delete()

    async def on_message(self, message: Message):
        if message.author.bot:
            return
        await self.db.execute(
                """
                UPDATE msg
                SET seen = seen + 1
                """
            )
        await self.db.commit()
        await self.process_commands(message)

    
    async def on_mention(self, message: Message):
        if re.fullmatch(rf"<@!?{self.user.id}>", message.content):
            embed = (
                discord.Embed(
                    title="Chick | a discord bot for your server",
                    description=(
                        f"Hi {message.author.mention}!\n"
                        f"My prefix is `_`\n"
                        f"Use `_help` to get started.\n"
                        f"I provide some nice features such as modaration, music, utility, fun and more"
                    ),
                    color=self.color,
                )
                .set_thumbnail(url=self.user.display_avatar.url)
                .set_footer(
                    text="Made with 💖 and discord.py", icon_url=self.user.display_avatar.url
                )
            )
            links = [
                LinkType("Invite", self.invite_url),
                LinkType("Support", self.config.support),
            ]
            await message.channel.send(embed=embed, view=LinkButton(links))
            return


    @on_startup.append
    async def load_cogs(self):
        for cog in self.config.extensions:
            try:
                await super().load_extension("Cogs."+cog)
                self.logger.info(f"Loaded Cogs.{cog}")
                await startup(msg=f"Loaded Cogs.{cog}", session=self.session)
            except Exception as e:
                self.logger.error(f"Error while loading Cogs.{cog}", exc_info=e)
                await error(msg=f"Error while loading Cogs.\n{cog}", session=self.session)
        await super().load_extension("jishaku")
        self.logger.info("Loaded Cogs.jishaku")
        await startup(msg="Loaded Cogs.jishaku", session=self.session)

    @on_startup.append
    async def load_events(self):
        for event in self.config.events:
            try:
                await super().load_extension("Events."+event)
                self.logger.info(f"Loaded Events.{event}")
                await startup(msg=f"Loaded Events.{event}", session=self.session)
            except Exception as e:
                self.logger.error(f"Error while loading Events.{event}", exc_info=e)
                await error(msg=f"Error while loading Events.\n{event}", session=self.session)
                pass

    @on_startup.append
    async def wavelink_connect(self):
        node: wavelink.Node = wavelink.Node(uri=f'{self.config.host}:{self.config.port}', password=self.config.auth, id='Music Node')
        await self.wavelink.connect(client=self, nodes=[node])
        self.logger.info(f"Connected to wavelink node {node.id}")
        await startup(msg=f"Connected to wavelink node {node.id}", session=self.session)