from __future__ import annotations

import asyncio
from typing import Optional, Union

import discord
from discord import app_commands
from discord.ext import commands
from typing_extensions import Annotated
from Core import Cog, Bot, Context
from Cogs.utility.Helpers.Emoji import emoji_name, EmojiURL
from Utils import Checks
import json

class LockView(discord.ui.View):
    def __init__(self, ctx: Context):
        super().__init__()
        self.ctx = ctx
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
       if interaction.user.id == self.ctx.author.id:
            return True
       else:
            await interaction.response.send_message("You cannot use this button.", ephemeral=True)
            return False
    

    @discord.ui.button(emoji="🔓", style=discord.ButtonStyle.grey)
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = False
        overwrites = {
                    self.ctx.guild.default_role: discord.PermissionOverwrite(send_messages = True, read_message_history = True),
                    self.ctx.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True),
                }
        await self.ctx.channel.edit(overwrites=overwrites)
        button.disabled = True
        self.lock.disabled = False
        await interaction.response.edit_message(embed=discord.Embed(description=f"Unlocked {self.ctx.channel.mention}", color=discord.Color.green()) ,view=self)


    @discord.ui.button(emoji="🔒", style=discord.ButtonStyle.grey, disabled=True)
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        overwrites = {
                self.ctx.guild.default_role: discord.PermissionOverwrite(send_messages = False, read_message_history = False),
                self.ctx.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True),
            }
        await self.ctx.channel.edit(overwrites=overwrites)
        button.disabled = True
        self.unlock.disabled = False
        await interaction.response.edit_message(embed=discord.Embed(description=f"Locked {self.ctx.channel.mention}", color=discord.Color.red()) ,view=self)


        
class Utility(Cog):
    """Utility commands"""
    def __init__(self, bot: Bot):
        self.bot = bot

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="🪛")

    @commands.hybrid_command(name="lock", description="Locks down a channel")
    @app_commands.describe(channel="The channel to lock down.")
    @Checks.has_permissions(manage_channels=True)
    async def lock(self, ctx: Context, channel:Optional[discord.TextChannel]=None):
        """
        Locks down a channel
        channel: The channel to lock down. 
        """
        if channel is None:
            channel = ctx.channel
        if channel.permissions_for(ctx.guild.default_role).send_messages == False:
            await ctx.embed(description=f"{channel} is already locked.")
            return
        if channel.permissions_for(ctx.guild.default_role).send_messages == True:
            overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(send_messages = False, read_message_history = False),
                    ctx.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True),
                }
        x = await ctx.embed(description=f"Locking down {channel.mention}.")
        await channel.edit(overwrites=overwrites)
        await asyncio.sleep(3)
        await x.edit(embed=discord.Embed(description=f"Locked down {channel.mention}.", color=self.bot.color), view=LockView(ctx))
            

    @commands.hybrid_command(name="unlock", description="Unlocks a channel")
    @app_commands.describe(channel="The channel to unlock.")
    @Checks.has_permissions(manage_channels=True)
    async def unlock(self, ctx: Context, channel:Optional[discord.TextChannel]):
        """
        Unlocks a channel
        channel: The channel to unlock. 
        """
        if channel is None:
            channel = ctx.channel
        if channel.permissions_for(ctx.guild.default_role).send_messages == True:
            await ctx.embed(description=f"{channel} is already unlocked.")
            return
        if channel.permissions_for(ctx.guild.default_role).send_messages == False:
            overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True),
                    ctx.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True),
                }
        x = await ctx.embed(description=f"Unlocking {channel.mention}.")
        await channel.edit(overwrites=overwrites)
        await asyncio.sleep(3)
        await x.edit(embed=discord.Embed(description=f"Unlocked {channel.mention}.", color=self.bot.color))


    @commands.hybrid_command(name="nuke", description="Nukes the channel")
    @Checks.has_permissions(manage_channels=True)
    async def nuke(self, ctx: Context, channel:Optional[discord.TextChannel]):
        """
        Nukes the channel
        """
        if channel is None:
            channel = ctx.channel
    
        result = await ctx.confirm(f"Are you sure you want to nuke {channel.mention}", delete_after=True)
        if result:
            x = await ctx.send("Nuking channel in 3 seconds...")
            for i in range(1, 4):
                await x.edit(content=f"Nuking channel in {3 - i} seconds...")
                await asyncio.sleep(1)
            await asyncio.sleep(1)
            chan = await channel.clone()
            await channel.delete()
            await chan.send(f"Hey {ctx.author.mention}, I just nuked {chan.mention}")

            await chan.send("https://tenor.com/view/chicken-bomb-gif-26332692")
        else:
            await ctx.send("Nuke aborted.")

    @commands.hybrid_command(name='emoji', description='Creates a new emoji in the server using imoji url or file')
    @commands.guild_only()
    @Checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    @app_commands.describe(
        name='The emoji name',
        file='The image file to use for uploading',
        url_or_emoji='The URL or emoji to use for uploading',
    )
    async def emoji(self, ctx: Context, name: Annotated[str, emoji_name], file: Optional[discord.Attachment], *, url_or_emoji: Optional[str]):
        if not ctx.me.guild_permissions.manage_emojis:
            return await ctx.send('Bot does not have permission to add emoji.')
        reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'
        if file is None and url_or_emoji is None:
            return await ctx.send('Missing emoji file or url to upload with')
        if file is not None and url_or_emoji is not None:
            return await ctx.send('Cannot mix both file and url arguments, choose only')
        is_animated = False
        request_url = ''
        if url_or_emoji is not None:
            upgraded = await EmojiURL.convert(ctx, url_or_emoji)
            is_animated = upgraded.animated
            request_url = upgraded.url
        elif file is not None:
            if not file.filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                return await ctx.send('Unsupported file type given, expected png, jpg, or gif')

            is_animated = file.filename.endswith('.gif')
            request_url = file.url

        emoji_count = sum(e.animated == is_animated for e in ctx.guild.emojis)
        if emoji_count >= ctx.guild.emoji_limit:
            return await ctx.send('There are no more emoji slots in this server.')

        async with self.bot.session.get(request_url) as resp:
            if resp.status >= 400:
                return await ctx.send('Could not fetch the image.')
            if int(resp.headers['Content-Length']) >= (256 * 1024):
                return await ctx.send('Image is too big.')

            data = await resp.read()
            coro = ctx.guild.create_custom_emoji(name=name, image=data, reason=reason)
            async with ctx.typing():
                try:
                    created = await asyncio.wait_for(coro, timeout=10.0)
                except asyncio.TimeoutError:
                    return await ctx.send('Sorry, the bot is rate limited or it took too long.')
                except discord.HTTPException as e:
                    return await ctx.send(f'Failed to create emoji somehow: {e}')
                else:
                    embed = discord.Embed(title="Created an emoji", description=f"emoji: {created}")
                    if url_or_emoji.__contains__("https://") and file is None:
                        embed.set_image(url=url_or_emoji)
                    else:
                        embed.set_image(url=file.url)
                    return await ctx.send(embed=embed)