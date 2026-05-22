import discord
from discord import app_commands
from discord.ext import commands, tasks
from config import GUILD_ID, MC_IP, MC_PORT, STATUS_CHAN_ID
from branding import GREEN, RED, PURPLE, THUMBNAIL_URL, footer


def get_server_status() -> discord.Embed:
    try:
        from mcstatus import JavaServer
        server = JavaServer.lookup(f"{MC_IP}:{MC_PORT}", timeout=3)
        s = server.status()

        players_online = s.players.online
        players_max    = s.players.max
        version        = s.version.name
        motd           = (s.motd.to_plain_text() if hasattr(s.motd, "to_plain_text") else str(s.motd)).strip()

        bar_filled = round((players_online / max(players_max, 1)) * 10)
        bar = "🟩" * bar_filled + "⬛" * (10 - bar_filled)

        names = ""
        if s.players.sample:
            names = "\n".join(f"• `{p.name}`" for p in s.players.sample[:10])

        embed = discord.Embed(
            title="🟢  Serwer ONLINE",
            color=GREEN,
        )
        embed.add_field(name="IP",      value=f"`{MC_IP}`",  inline=True)
        embed.add_field(name="Port",    value=f"`{MC_PORT}`", inline=True)
        embed.add_field(name="Wersja",  value=version,        inline=True)
        embed.add_field(
            name=f"Gracze — {players_online}/{players_max}",
            value=f"{bar}\n{names if names else '*Brak graczy online*'}",
            inline=False,
        )
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer("Aktualizacja co 5 min"))
        return embed

    except Exception as e:
        embed = discord.Embed(
            title="🔴  Serwer OFFLINE",
            description=f"Nie można połączyć się z `{MC_IP}:{MC_PORT}`\n```{e}```",
            color=RED,
        )
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer("Aktualizacja co 5 min"))
        return embed


class StatusCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._status_msg: discord.Message | None = None
        self.auto_update.start()

    def cog_unload(self):
        self.auto_update.cancel()

    @app_commands.command(name="status", description="Sprawdź status serwera Minecraft")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(embed=get_server_status())

    @tasks.loop(minutes=5)
    async def auto_update(self):
        chan = (
            self.bot.get_channel(STATUS_CHAN_ID)
            if STATUS_CHAN_ID
            else discord.utils.get(self.bot.get_all_channels(), name="🟢-status-serwera")
        )
        if not isinstance(chan, discord.TextChannel):
            return

        embed = get_server_status()

        if self._status_msg is None:
            async for msg in chan.history(limit=10):
                if msg.author == self.bot.user and msg.embeds:
                    self._status_msg = msg
                    break

        if self._status_msg:
            try:
                await self._status_msg.edit(embed=embed)
                return
            except discord.NotFound:
                self._status_msg = None

        self._status_msg = await chan.send(embed=embed)

    @auto_update.before_loop
    async def before_update(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(StatusCog(bot))
