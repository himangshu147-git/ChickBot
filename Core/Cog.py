from discord.ext import commands
import datetime


class Cog(commands.Cog):
    """A custom implementation of commands.Cog class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_time: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)

    def __str__(self):
        return "{0.__class__.__name__}".format(self)
