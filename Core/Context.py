from contextlib import suppress
from typing import Any, Generic, List, Optional, TypeVar, Union, Callable
import asyncio
import discord
from discord.ext import commands
from Utils import ConfirmationView

T = TypeVar("T")

class Context(commands.Context[commands.Bot], Generic[T]):
    bot: commands.Bot
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
    async def send(
        self,
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[discord.Message]:
        perms: discord.Permissions = self.channel.permissions_for(self.me)
        if not (perms.send_messages and perms.embed_links):
            with suppress(discord.Forbidden):
                await self.author.send(
                    (
                        "Bot don't have either Embed Links or Send Messages permission in that channel. "
                        "Please give sufficient permissions to the bot."
                    )
                )
                return None

        embeds: Union[discord.Embed, List[discord.Embed]] = kwargs.get(
            "embed"
        ) or kwargs.get("embeds")

        def __set_embed_defaults(embed: discord.Embed, /):
            if not embed.color:
                embed.color = 0xfc6f03
            if not embed.timestamp:
                embed.timestamp = discord.utils.utcnow()
            if not embed.footer:
                embed.set_footer(
                    text=f"Requested by {self.author}",
                    icon_url=self.author.display_avatar.url,
                )

        if isinstance(embeds, (list, tuple)):
            for embed in embeds:
                if isinstance(embed, discord.Embed):
                    __set_embed_defaults(embed)
        else:
            if isinstance(embeds, discord.Embed):
                __set_embed_defaults(embeds)

        return await super().send(str(content)[:1990] if content else None, **kwargs)
    
    async def embed(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        footer_text: Optional[str] = None,
        footer_icon: Optional[str] = None,
        timestamp: bool = True,
        color: Optional[Union[int, discord.Color]] = None,
        **kwargs: Any,
    ) -> Optional[discord.Message]:
        embed = discord.Embed(title=title, description=description, color=color or self.bot.color)
        if footer_text and footer_icon is not None:
            embed.set_footer(text=footer_text, icon_url=footer_icon)
        if timestamp:
            embed.timestamp = discord.utils.utcnow()

        return await self.send(embed=embed, **kwargs)
    
    
    async def error(self, message: str, delete_after: bool = None, **kwargs: Any) -> Optional[discord.Message]:
        with suppress(discord.HTTPException):
            msg: Optional[discord.Message] = await self.reply(
                embed=discord.Embed(description=message, color=discord.Color.red()),
                delete_after=delete_after,
                **kwargs,
            )
            try:
                await self.bot.wait_for("message_delete", check=lambda m: m.id == self.message.id, timeout=30)
            except asyncio.TimeoutError:
                pass
            else:
                if msg is not None:
                    await msg.delete(delay=0)
            finally:
                return msg

        return None

    async def wait_and_purge(
        self,
        channel: Union[discord.TextChannel, discord.Thread],
        *,
        limit: int = 100,
        wait_for: Union[int, float] = 10,
        check: Callable = lambda m: True,
    ):
        await asyncio.sleep(wait_for)

        with suppress(discord.HTTPException):
            await channel.purge(limit=limit, check=check)
            
            
    async def confirm(
        self,
        message: str,
        *,
        timeout: float = 60.0,
        delete_after: bool = True,
        author_id: Optional[int] = None,
    ) -> Optional[bool]:
        author_id = author_id or self.author.id
        view = ConfirmationView(
            timeout=timeout,
            delete_after=delete_after,
            author_id=author_id,
        )
        view.message = await self.send(message, view=view, ephemeral=delete_after)
        await view.wait()
        return view.value
    
    def tick(self, opt: Optional[bool], label: Optional[str] = None) -> str:
        lookup = {
            True: '<:greenTick:330090705336664065>',
            False: '<:redTick:330090723011592193>',
            None: '<:greyTick:563231201280917524>',
        }
        emoji = lookup.get(opt, '<:redTick:330090723011592193>')
        if label is not None:
            return f'{emoji}: {label}'
        return emoji
        

class GuildContext(Context):
    author: discord.Member
    guild: discord.Guild
    channel: Union[discord.VoiceChannel, discord.TextChannel, discord.Thread]
    me: discord.Member
    prefix: str