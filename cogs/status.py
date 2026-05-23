import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
from config import GUILD_ID, MC_IP, MC_PORT, STATUS_CHAN_ID, VELOCITY_PORT, SURVIVAL_PORT
from branding import GREEN, RED, THUMBNAIL_URL, footer
import link_store


def _query_server(ip: str, port: int) -> tuple[int, int] | None:
    """Returns (online, max) or None if server is unreachable."""
    try:
        from mcstatus import JavaServer
        s = JavaServer.lookup(f"{ip}:{port}", timeout=3).status()
        return s.players.online, s.players.max
    except Exception:
        return None


def get_server_status() -> discord.Embed:
    result = _query_server(MC_IP, MC_PORT)
    if result:
        online, max_players = result
        bar_filled = round((online / max(max_players, 1)) * 10)
        bar = "🟩" * bar_filled + "⬛" * (10 - bar_filled)
        try:
            from mcstatus import JavaServer
            s = JavaServer.lookup(f"{MC_IP}:{MC_PORT}", timeout=3).status()
            version = s.version.name
            names   = "\n".join(f"• `{p.name}`" for p in (s.players.sample or [])[:10])
        except Exception:
            version = "—"
            names   = ""
        embed = discord.Embed(title="🟢  Serwer ONLINE", color=GREEN)
        embed.add_field(name="IP",     value=f"`{MC_IP}`",    inline=True)
        embed.add_field(name="Port",   value=f"`{MC_PORT}`",  inline=True)
        embed.add_field(name="Wersja", value=version,         inline=True)
        embed.add_field(
            name=f"Gracze — {online}/{max_players}",
            value=f"{bar}\n{names if names else '*Brak graczy online*'}",
            inline=False,
        )
    else:
        embed = discord.Embed(
            title="🔴  Serwer OFFLINE",
            description=f"Nie można połączyć się z `{MC_IP}:{MC_PORT}`",
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
        self.stats_voice_update.start()

    def cog_unload(self):
        self.auto_update.cancel()
        self.stats_voice_update.cancel()

    @app_commands.command(name="status", description="Sprawdź status serwera Minecraft")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(embed=get_server_status())

    # ── Detailed status embed (Assassin Arena channel) ────────────────────────

    @tasks.loop(minutes=5)
    async def auto_update(self):
        chan = (
            self.bot.get_channel(STATUS_CHAN_ID)
            if STATUS_CHAN_ID
            else discord.utils.get(self.bot.get_all_channels(), name="🟢・status-serwera")
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

    # ── Stats voice channels (sidebar scoreboard) ─────────────────────────────

    @tasks.loop(minutes=10)
    async def stats_voice_update(self):
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return

        cat = discord.utils.get(guild.categories, name="📊 STATYSTYKI")
        if not cat:
            return

        def find_vc(prefix: str) -> discord.VoiceChannel | None:
            for ch in cat.voice_channels:
                if ch.name.startswith(prefix):
                    return ch
            return None

        async def set_name(vc: discord.VoiceChannel | None, name: str):
            if vc and vc.name != name:
                try:
                    await vc.edit(name=name, reason="Stats update")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"[Status] stats channel rename error: {e}")

        # Query all three servers (may be offline — returns None gracefully)
        velocity = _query_server(MC_IP, VELOCITY_PORT)
        assassin = _query_server(MC_IP, MC_PORT)
        survival = _query_server(MC_IP, SURVIVAL_PORT)

        linked_count = len(link_store.get_all_links())

        await set_name(
            find_vc("🌐 Sieć"),
            f"🌐 Sieć: {velocity[0]} graczy" if velocity else "🌐 Sieć: offline",
        )
        await set_name(
            find_vc("⚔ Assassin"),
            f"⚔ Assassin: {assassin[0]}/{assassin[1]}" if assassin else "⚔ Assassin: offline",
        )
        await set_name(
            find_vc("🌲 Survival"),
            f"🌲 Survival: {survival[0]}/{survival[1]}" if survival else "🌲 Survival: wkrótce",
        )
        await set_name(
            find_vc("👥 Discord"),
            f"👥 Discord: {guild.member_count}",
        )
        await set_name(
            find_vc("🔗 Połączonych"),
            f"🔗 Połączonych: {linked_count}",
        )

    @stats_voice_update.before_loop
    async def before_stats(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(StatusCog(bot))
