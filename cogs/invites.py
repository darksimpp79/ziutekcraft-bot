import json
import time
from pathlib import Path
import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID
from branding import GOLD, PURPLE, RED, THUMBNAIL_URL, footer

DATA_DIR = Path(__file__).parent.parent / "data"
INV_FILE  = DATA_DIR / "invites.json"

# (count_threshold, role_name, display_label)
MILESTONES = [
    (5,  "📨 Rekruter",       "5 zaproszeń"),
    (15, "🏅 Ambasador",      "15 zaproszeń"),
    (30, "💎 Legenda Ziutka", "30 zaproszeń"),
]

MIN_ACCOUNT_AGE_DAYS = 7    # konto młodsze → invite nie liczy się
RATE_LIMIT_COUNT     = 5    # tyle zaproszeń w oknie…
RATE_LIMIT_WINDOW    = 3600 # …(sekundy) → flaga dla staffa
STAFF_LOG_CHAN        = "🔧-bot-komendy"


def _read() -> dict:
    if INV_FILE.exists():
        try:
            return json.loads(INV_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _write(data: dict):
    DATA_DIR.mkdir(exist_ok=True)
    INV_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class InviteCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot    = bot
        self._cache: dict[str, dict] = {}  # code -> {uses, inviter_id}

    @commands.Cog.listener()
    async def on_ready(self):
        await self._refresh_cache()

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        if invite.guild and invite.guild.id == GUILD_ID:
            self._cache[invite.code] = {
                "uses":       invite.uses or 0,
                "inviter_id": invite.inviter.id if invite.inviter else None,
            }

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        self._cache.pop(invite.code, None)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id != GUILD_ID:
            return

        before = {c: v["uses"] for c, v in self._cache.items()}
        await self._refresh_cache()

        used_code = None
        for code, entry in self._cache.items():
            if entry["uses"] > before.get(code, 0):
                used_code = code
                break

        if used_code is None:
            return

        inviter_id = self._cache[used_code]["inviter_id"]
        if not inviter_id:
            return

        guild   = member.guild
        inviter = guild.get_member(inviter_id)

        # ── Weryfikacja wieku konta ───────────────────────────────────────────
        account_age_days = (discord.utils.utcnow() - member.created_at).days
        if account_age_days < MIN_ACCOUNT_AGE_DAYS:
            # Invite nie liczy się — powiadom zapraszającego
            if inviter:
                try:
                    await inviter.send(
                        f"⚠️ Zaprosiłeś **{member.mention}** ({member}), ale ich konto ma tylko "
                        f"**{account_age_days} dni** — minimum to **{MIN_ACCOUNT_AGE_DAYS} dni**.\n"
                        f"To zaproszenie **nie zostało zaliczone**. Jeśli to prawdziwa osoba, "
                        f"wróci i policzy się normalnie gdy konto będzie starsze."
                    )
                except discord.Forbidden:
                    pass
            return

        # ── Zapis zaproszenia ─────────────────────────────────────────────────
        data  = _read()
        entry = data.setdefault(str(inviter_id), {"count": 0, "milestones": [], "recent_ts": []})

        now = int(time.time())
        # Wyczyść stare timestamps spoza okna
        entry["recent_ts"] = [ts for ts in entry.get("recent_ts", []) if now - ts < RATE_LIMIT_WINDOW]
        entry["recent_ts"].append(now)
        entry["count"] += 1
        _write(data)

        count         = entry["count"]
        recent_count  = len(entry["recent_ts"])

        # ── Rate-limit flag dla staffa ────────────────────────────────────────
        if recent_count >= RATE_LIMIT_COUNT:
            log_chan = discord.utils.get(guild.text_channels, name=STAFF_LOG_CHAN)
            if log_chan:
                embed = discord.Embed(
                    title="⚠️ Podejrzana aktywność — zaproszenia",
                    color=RED,
                )
                inviter_mention = inviter.mention if inviter else f"<@{inviter_id}>"
                embed.add_field(
                    name="Zapraszający",
                    value=f"{inviter_mention} (`{inviter or inviter_id}`)",
                    inline=True,
                )
                embed.add_field(
                    name="Zaproszeń w ostatniej godzinie",
                    value=f"**{recent_count}** (łącznie: {count})",
                    inline=True,
                )
                embed.add_field(
                    name="Nowy member",
                    value=f"{member.mention} (`{member}`)\nKonto: {account_age_days} dni",
                    inline=False,
                )
                embed.add_field(
                    name="Co zrobić",
                    value=(
                        "Sprawdź ręcznie czy to znajomi czy multikonta.\n"
                        "`/invite-anuluj @user <liczba>` — aby odjąć fałszywe zaproszenia."
                    ),
                    inline=False,
                )
                embed.set_footer(text=footer("Invite Guard"))
                await log_chan.send(embed=embed)

        if not inviter:
            return

        # ── Milestony ─────────────────────────────────────────────────────────
        for threshold, role_name, label in MILESTONES:
            if count == threshold:
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    try:
                        await inviter.add_roles(role, reason=f"Invite milestone {threshold}")
                    except discord.Forbidden:
                        pass

                embed = discord.Embed(
                    title="🏅  Milestone odblokowany!",
                    description=(
                        f"Zaprosiłeś **{count}** osób na **{guild.name}**!\n\n"
                        f"Odblokowałeś rolę **{role_name}**. Dziękujemy za rozwijanie społeczności! ⚔"
                    ),
                    color=GOLD,
                )
                if THUMBNAIL_URL:
                    embed.set_thumbnail(url=THUMBNAIL_URL)
                embed.set_footer(text=footer("System Zaproszeń"))
                try:
                    await inviter.send(embed=embed)
                except discord.Forbidden:
                    pass
                break

    # ── /zaproszenia ──────────────────────────────────────────────────────────

    @app_commands.command(
        name="zaproszenia",
        description="Sprawdź ile osób zaprosiłeś na serwer i postęp do następnego milestone",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def zaproszenia(self, interaction: discord.Interaction):
        data  = _read()
        entry = data.get(str(interaction.user.id), {"count": 0})
        count = entry["count"]

        next_ms = next(((t, r) for t, r, _ in MILESTONES if count < t), None)

        embed = discord.Embed(title="📨  Twoje zaproszenia", color=PURPLE)
        embed.add_field(name="Zaproszono", value=f"**{count}** osób", inline=True)
        if next_ms:
            left = next_ms[0] - count
            embed.add_field(
                name="Następny milestone",
                value=f"`{next_ms[1]}` za **{left}** więcej",
                inline=True,
            )
        else:
            embed.add_field(name="Status", value="🏆 Wszystkie milestony odblokowane!", inline=True)

        embed.add_field(
            name="Milestony",
            value="\n".join(
                f"{'✅' if count >= t else '⬜'} `{t}` → **{r}**"
                for t, r, _ in MILESTONES
            ),
            inline=False,
        )
        embed.set_footer(text=footer("System Zaproszeń"))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── /invite-anuluj (admin) ────────────────────────────────────────────────

    @app_commands.command(
        name="invite-anuluj",
        description="[ADMIN] Odejmij fałszywe zaproszenia od gracza",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def invite_anuluj(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        ilosc: int,
    ):
        data  = _read()
        entry = data.get(str(member.id))
        if not entry:
            await interaction.response.send_message(
                f"Brak danych dla {member.mention}.", ephemeral=True
            )
            return

        before = entry["count"]
        entry["count"] = max(0, before - ilosc)
        _write(data)

        await interaction.response.send_message(
            f"✅ Odjęto **{ilosc}** zaproszeń od {member.mention}. "
            f"Było: `{before}`, teraz: `{entry['count']}`.",
            ephemeral=True,
        )

    async def _refresh_cache(self):
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return
        try:
            invites = await guild.fetch_invites()
            self._cache = {
                inv.code: {
                    "uses":       inv.uses or 0,
                    "inviter_id": inv.inviter.id if inv.inviter else None,
                }
                for inv in invites
            }
        except discord.Forbidden:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(InviteCog(bot))
