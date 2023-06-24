from discord import Webhook
import aiohttp

async def startup(msg: str, session: aiohttp.ClientSession):
    webhook = Webhook.partial(
        id=1119866573591695421, 
        token="O_o4MFRNX4JXQemIQCPgDCxJh-ShPB3yiCWi2wcnn3X4mATadGkDPDSDsvFMCkoLxpMI",
        session=session
        )
    await webhook.send(content=f"```css\n{msg}\n```")

async def error(msg: str, session: aiohttp.ClientSession):
    webhook = Webhook.partial(
        id=1119866573591695421, 
        token="O_o4MFRNX4JXQemIQCPgDCxJh-ShPB3yiCWi2wcnn3X4mATadGkDPDSDsvFMCkoLxpMI",
        session=session
        )
    await webhook.send(content=f"```css\n{msg}\n```")