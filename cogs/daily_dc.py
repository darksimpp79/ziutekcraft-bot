import json, time, logging
from pathlib import Path
import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID, RCON_HOST, RCON_PORT, RCON_PASSWORD
from branding import GREEN, GOLD, RED, PURPLE, THUMBNAIL_URL, footer
import link_store
from rcon_utils import rcon_command
import pending_rewards

log = logging.getLogger(__name__)

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
        resp = rcon_command(RCON_HOST, RCON_PORT, RCON_PASSWORD, f"dcreward {nick} {amount}")
        return True, resp.strip() or "OK"
    except Exception as e:
        return False, str(e)


def daily_claim(discord_id: int) -> dict:
    """
    Atomically claim the daily reward for a Discord user.
    Returns {"ok": True, "amount": int, "streak": int}
         or {"ok": False, "wait_seconds": int}
    """
    data  = _read()
    entry = data.get(str(discord_id), {"last_claim": 0, "streak": 0})
    now   = time.time()
    diff  = now - entry["last_claim"]

    if diff < COOLDOWN:
        return {"ok": False, "wait_seconds": int(COOLDOWN - diff)}

    entry["streak"] = (entry.get("streak", 0) + 1) if diff < COOLDOWN * 2 else 1
    entry["last_claim"] = now
    data[str(discord_id)] = entry
    _write(data)

    streak = entry["streak"]
    bonus  = min((streak - 1) * STREAK_STEP, MAX_BONUS)
    total  = BASE_TOKENS + bonus
    return {"ok": True, "amount": total, "streak": streak}


class DailyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="daily",
        description="Sprawdź kiedy możesz odebrać dzienny bonus (odbierz przez /daily w grze MC)",
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
        streak = entry.get("streak", 0)
        bonus  = min((streak - 1) * STREAK_STEP, MAX_BONUS) if streak > 0 else 0
        total  = BASE_TOKENS + bonus

        if diff < COOLDOWN:
            remaining = COOLDOWN - diff
            h = int(remaining // 3600)
            m = int((remaining % 3600) // 60)
            embed = discord.Embed(
                title="⏳  Dzienny bonus",
                description=(
                    f"Następna nagroda za **{h}h {m}m**.\n\n"
                    f"Seria: 🔥 **{streak}** dni | Nagroda: **{total}** znaczków\n\n"
                    f"Odbieraj przez **`/daily`** na serwerze Minecraft."
                ),
                color=PURPLE,
            )
        else:
            embed = discord.Embed(
                title="🎁  Dzienny bonus gotowy!",
                description=(
                    f"Możesz odebrać **{total} znaczków**!\n\n"
                    f"Wejdź na serwer Minecraft i wpisz **`/daily`**."
                ),
                color=GREEN,
            )
        embed.set_footer(text=footer("Daily Reward"))
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(DailyCog(bot))
