import asyncio
import logging
import logging.handlers
from pathlib import Path
import discord
from discord.ext import commands
from config import TOKEN, GUILD_ID

# ── Logging setup ─────────────────────────────────────────────────────────────
_LOG_DIR = Path(__file__).parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

_fmt = logging.Formatter("%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
                          datefmt="%Y-%m-%d %H:%M:%S")

_fh = logging.handlers.RotatingFileHandler(
    _LOG_DIR / "bot.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
_fh.setFormatter(_fmt)

_sh = logging.StreamHandler()
_sh.setFormatter(_fmt)

logging.basicConfig(level=logging.INFO, handlers=[_fh, _sh])
# Quieten noisy discord.py internals
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("discord.http").setLevel(logging.WARNING)

log = logging.getLogger("bot")
from cogs.beta import BetaSignupView
from cogs.verify import VerifyView
from cogs.link import LinkView
from cogs.ticket import TicketView, TicketCloseView
from cogs.bugs import BugPanelView, BugFixView
from cogs.suggestions import SuggestionPanelView, SuggestionStatusView

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    # Persistent views — przeżywają restart bota
    bot.add_view(BetaSignupView(bot))
    bot.add_view(VerifyView())
    bot.add_view(LinkView())
    bot.add_view(TicketView())
    bot.add_view(TicketCloseView())
    bot.add_view(BugPanelView())
    bot.add_view(BugFixView())
    bot.add_view(SuggestionPanelView())
    bot.add_view(SuggestionStatusView())

    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        log.info("Zasynkowano %d komend na serwer %s", len(synced), GUILD_ID)
    except Exception as e:
        log.error("Błąd sync komend: %s", e)

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="Assassin Arena ⚔ Beta",
        )
    )
    log.info("Online jako %s (%s)", bot.user, bot.user.id)


async def main():
    async with bot:
        await bot.load_extension("cogs.verify")
        await bot.load_extension("cogs.welcome")
        await bot.load_extension("cogs.beta")
        await bot.load_extension("cogs.status")
        await bot.load_extension("cogs.setup")
        await bot.load_extension("cogs.link")
        await bot.load_extension("cogs.invites")
        await bot.load_extension("cogs.daily_dc")
        await bot.load_extension("cogs.creator")
        await bot.load_extension("cogs.ranks")
        await bot.load_extension("cogs.info")
        await bot.load_extension("cogs.ticket")
        await bot.load_extension("cogs.bugs")
        await bot.load_extension("cogs.suggestions")
        await bot.load_extension("cogs.voice")
        await bot.start(TOKEN)


asyncio.run(main())
