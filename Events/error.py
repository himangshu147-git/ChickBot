from discord.ext import commands
from Core import Bot, Cog, Context

class Error(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(
        self, ctx: Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            await ctx.send(f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.", delete_after=5)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.error(f"**You are missing a required argument.**\n`{error}`")
        elif isinstance(error, commands.BadArgument):
            await ctx.error(f"**One or more arguments are invalid.**\n`{error}`")
        elif isinstance(error, commands.CheckFailure):
            await ctx.error(f"**Command failed.**\n`{error}`")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.error(f"**Command not found.**\n`{error}`")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.error(f"**Command is disabled.**\n`{error}`")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.error(f"**Command cannot be used in DMs.**\n`{error}`")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.error(f"**An error occurred while executing the command.**\n`{error}`")
        elif isinstance(error, commands.TooManyArguments):
            await ctx.error(f"**Too many arguments.**\n`{error}`")
        elif isinstance(error, commands.UserInputError):
            await ctx.error(f"**An error occurred while executing the command.**\n`{error}`")   
        elif isinstance(error, commands.NotOwner):
            await ctx.error(f"**You are not the owner of this bot.**\n`{error}`")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.error(f"**You are missing permissions to run this command.**\n`{error}`")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.error(f"**I am missing permissions to run this command.**\n`{error}`")
        elif isinstance(error, commands.MissingRole):
            await ctx.error(f"**You are missing a role to run this command.**\n`{error}`")
        elif isinstance(error, commands.BotMissingRole):
            await ctx.error(f"**I am missing a role to run this command.**\n`{error}`")
        elif isinstance(error, commands.MissingAnyRole):
            await ctx.error(f"**You are missing a role to run this command.**\n`{error}`")
        elif isinstance(error, commands.BotMissingAnyRole):
            await ctx.error(f"**I am missing a role to run this command.**\n`{error}`")
        elif isinstance(error, commands.NSFWChannelRequired):
            await ctx.error(f"**This command can only be used in a NSFW channel.**\n`{error}`")
        elif isinstance(error, commands.ExtensionError):
            await ctx.error(f"**An error occurred while executing the command.**\n`{error}`")
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            await ctx.error(f"**An error occurred while executing the command.**\n`{error}`")
        elif isinstance(error, commands.ExtensionNotLoaded):    
            await ctx.error(f"**An error occurred while executing the command.**\n`{error}`")
        elif isinstance(error, commands.ExtensionNotFound):
            await ctx.error(f"**An error occurred while executing the command.**\n`{error}`")
        elif isinstance(error, commands.ExtensionFailed):
            await ctx.error(f"**An error occurred while executing the command.**\n`{error}`")
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            await ctx.error(f"**An error occurred while executing the command.**\n`{error}`")

        else:
            print(f"An error occurred: {type(error).__name__} - {error}")
            await ctx.error(f"**An error occurred while executing the command.**\n`{error}`")
    

async def setup(bot: Bot) -> None:
    await bot.add_cog(Error(bot))