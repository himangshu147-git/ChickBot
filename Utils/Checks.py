from __future__ import annotations
from typing import TYPE_CHECKING, Callable, TypeVar
from discord import app_commands

from discord.ext import commands

if TYPE_CHECKING:
    from Core import GuildContext, Context, Bot
    from discord.ext.commands._types import Check

T = TypeVar('T')


async def check_permissions(ctx: GuildContext, perms: dict[str, bool], *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True
    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_permissions(*, check=all, **perms: bool):
    async def pred(ctx: GuildContext):
        return await check_permissions(ctx, perms, check=check)

    return commands.check(pred)


async def check_guild_permissions(ctx: GuildContext, perms: dict[str, bool], *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if ctx.guild is None:
        return False

    resolved = ctx.author.guild_permissions
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_guild_permissions(*, check=all, **perms: bool):
    async def pred(ctx: GuildContext):
        return await check_guild_permissions(ctx, perms, check=check)

    return commands.check(pred)

def hybrid_permissions_check(**perms: bool) -> Callable[[T], T]:
    async def pred(ctx: GuildContext):
        return await check_guild_permissions(ctx, perms)

    def decorator(func: T) -> T:
        commands.check(pred)(func)
        app_commands.default_permissions(**perms)(func)
        return func

    return decorator


def is_manager():
    return hybrid_permissions_check(manage_guild=True)


def is_mod():
    return hybrid_permissions_check(ban_members=True, manage_messages=True)


def is_admin():
    return hybrid_permissions_check(administrator=True)


def is_in_guilds(*guild_ids: int):
    def predicate(ctx: GuildContext) -> bool:
        guild = ctx.guild
        if guild is None:
            return False
        return guild.id in guild_ids

    return commands.check(predicate)

def music_vc(vc_chan: int):
    async def predicate(ctx: Context) -> bool:
        if ctx.author.voice is None:
            await ctx.send("You must be in a voice channel to use this command.")
            return False
        if ctx.voice_client is None:
            await ctx.send("I am not connected to a voice channel.")
            return False
        if ctx.author.voice.channel != ctx.voice_client.channel:
            await ctx.send("You must be in the same voice channel as me to use this command.")
            return False
        if ctx.author.voice is not None and ctx.author.voice.channel.id != vc_chan:
            await ctx.send(f"You must be in the <#{vc_chan}> to use this command.")
            return False
        return True
    return commands.check(predicate)