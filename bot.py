import asyncio
import discord
from discord.ext import commands
from config import TOKEN, GUILD_ID
from cogs.beta import BetaSignupView
from cogs.verify import VerifyView
from cogs.link import LinkView
from cogs.ticket import TicketView, TicketCloseView

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

    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"[Bot] Zasynkowano {len(synced)} komend na serwer {GUILD_ID}")
    except Exception as e:
        print(f"[Bot] Błąd sync: {e}")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="Assassin Arena ⚔ Beta",
        )
    )
    print(f"[Bot] Online jako {bot.user} ({bot.user.id})")


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
        await bot.start(TOKEN)


asyncio.run(main())
