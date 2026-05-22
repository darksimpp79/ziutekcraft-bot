import json, time
from pathlib import Path
import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID, RCON_HOST, RCON_PORT, RCON_PASSWORD
from branding import GREEN, GOLD, RED, PURPLE, THUMBNAIL_URL, footer
import link_store

DATA_DIR   = Path(__file__).parent.parent / "data"
DAILY_FILE = DATA_DIR / "daily_rewards.json"

COOLDOWN    = 86400  # 24h in seconds
BASE_TOKENS = 10
STREAK_STEP = 2      # +2 tokens per streak day
MAX_BONUS   = 20     # cap at +20 (= 10-day streak)


def _read() -> dict:
    if DAILY_FILE.exists():
        try:
            return json.loads(DAILY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _write(data: dict):
    DATA_DIR.mkdir(exist_ok=True)
    DAILY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _rcon_grant(nick: str, amount: int) -> tuple[bool, str]:
    """Call RCON /dcreward <nick> <amount> to grant tokens in-game."""
    if not RCON_PASSWORD:
        return False, "RCON nie skonfigurowane (brak hasła w .env)"
    try:
        from mcrcon import MCRcon
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            resp = mcr.command(f"dcreward {nick} {amount}")
        return True, resp.strip() or "OK"
    except Exception as e:
        return False, str(e)


class DailyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="daily",
        description="Odbierz dzienny bonus znaczków (potrzebne połączone konto MC)",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def daily(self, interaction: discord.Interaction):
        discord_id = interaction.user.id
        link       = link_store.get_link_by_discord(discord_id)

        if not link:
            embed = discord.Embed(
                title="🔗  Najpierw połącz konto MC",
                description=(
                    "Aby odbierać codzienne nagrody musisz połączyć konto Minecraft z Discordem.\n\n"
                    "Użyj **/polacz-konto** i postępuj zgodnie z instrukcją."
                ),
                color=RED,
            )
            embed.set_footer(text=footer())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        data  = _read()
        entry = data.get(str(discord_id), {"last_claim": 0, "streak": 0})
        now   = time.time()
        diff  = now - entry["last_claim"]

        if diff < COOLDOWN:
            remaining = COOLDOWN - diff
            h = int(remaining // 3600)
            m = int((remaining % 3600) // 60)
            await interaction.response.send_message(
                f"⏳ Następna nagroda za **{h}h {m}m**. Wróć jutro!",
                ephemeral=True,
            )
            return

        # Streak: continues if claimed within 48h, resets otherwise
        entry["streak"] = (entry.get("streak", 0) + 1) if diff < COOLDOWN * 2 else 1
        entry["last_claim"] = now
        data[str(discord_id)] = entry
        _write(data)

        streak = entry["streak"]
        bonus  = min((streak - 1) * STREAK_STEP, MAX_BONUS)
        total  = BASE_TOKENS + bonus
        nick   = link["mc_nick"]

        await interaction.response.defer(ephemeral=True)
        ok, msg = _rcon_grant(nick, total)

        if ok:
            embed = discord.Embed(
                title="🎁  Dzienna nagroda odebrana!",
                color=GREEN,
            )
            embed.add_field(name="Znaczki",     value=f"`+{total}` 🪙",        inline=True)
            embed.add_field(name="Seria",       value=f"🔥 **{streak}** dni",  inline=True)
            if bonus > 0:
                embed.add_field(name="Bonus serii", value=f"`+{bonus}` za serię", inline=False)
            embed.add_field(name="Nick MC",     value=f"`{nick}`",             inline=True)
            if streak < 10:
                needed  = (10 - streak) * STREAK_STEP
                embed.add_field(
                    name="Do max. bonusu",
                    value=f"Jeszcze **{10 - streak}** dni (+{needed} tokenów)",
                    inline=True,
                )
        else:
            embed = discord.Embed(
                title="⚠️  Serwer offline — nagroda zapisana",
                description=(
                    f"**{total} znaczków** zostanie przyznanych gdy serwer wróci.\n"
                    f"Napisz do admina jeśli nagroda nie dotrze.\n```{msg}```"
                ),
                color=GOLD,
            )

        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer("Daily Reward"))
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(DailyCog(bot))
