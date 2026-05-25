"""
Automatyczna progresja rang czasowych.

Po weryfikacji gracz dostaje 👋 Nowy.
Bot co 6h sprawdza wszystkich i awansuje/degraduje:

  👋 Nowy      → 0–6 dni na serwerze
  🎯 Gracz     → 7–89 dni
  🏆 Weteran   → 90+ dni (3 miesiące)

Komendy admina:
  /progression-sync          — ręczna synchronizacja wszystkich
  /progression-check @user   — sprawdź rangę konkretnego gracza
"""

import logging
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from config import GUILD_ID

log = logging.getLogger(__name__)

# ── Progi (dni, nazwa_roli) — od najwyższego do najniższego ──────────────────
TIME_TIERS: list[tuple[int, str]] = [
    (90, "🏆 Weteran"),
    (7,  "🎯 Gracz"),
    (0,  "👋 Nowy"),
]
ALL_TIER_NAMES = {name for _, name in TIME_TIERS}


def _target_tier(days: int) -> str:
    """Zwraca nazwę roli dla podanej liczby dni."""
    for threshold, name in TIME_TIERS:
        if days >= threshold:
            return name
    return TIME_TIERS[-1][1]


async def sync_member(member: discord.Member) -> str | None:
    """
    Zsynchronizuj rangę czasową jednego członka.
    Zwraca opis zmiany lub None jeśli nic się nie zmieniło.
    """
    if member.bot:
        return None
    if not member.joined_at:
        return None

    days = (discord.utils.utcnow() - member.joined_at).days
    target_name = _target_tier(days)

    current_tiers = [r for r in member.roles if r.name in ALL_TIER_NAMES]
    has_target    = any(r.name == target_name for r in current_tiers)
    wrong_tiers   = [r for r in current_tiers if r.name != target_name]

    if has_target and not wrong_tiers:
        return None  # już ok

    target_role = discord.utils.get(member.guild.roles, name=target_name)
    if not target_role:
        log.warning("Rola '%s' nie istnieje na serwerze!", target_name)
        return None

    try:
        if wrong_tiers:
            await member.remove_roles(*wrong_tiers, reason="Progression: tier update")
        if not has_target:
            await member.add_roles(target_role, reason=f"Progression: {days}d → {target_name}")
        return f"{member.display_name}: {', '.join(r.name for r in wrong_tiers) or '—'} → {target_name} ({days}d)"
    except discord.Forbidden:
        log.warning("Brak uprawnień do zmiany ról %s", member)
        return None


class ProgressionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.progression_task.start()

    def cog_unload(self):
        self.progression_task.cancel()

    # ── Pętla co 6 godzin ────────────────────────────────────────────────────

    @tasks.loop(hours=6)
    async def progression_task(self):
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return
        changed = 0
        for member in guild.members:
            result = await sync_member(member)
            if result:
                changed += 1
                log.info("[Progression] %s", result)
        if changed:
            log.info("[Progression] Zaktualizowano %d członków.", changed)

    @progression_task.before_loop
    async def _before(self):
        await self.bot.wait_until_ready()

    # ── Nowy członek: od razu daj 👋 Nowy ────────────────────────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id != GUILD_ID:
            return
        # Joined_at może być None przez ułamek sekundy — jest 0 dni, dostanie Nowy
        await sync_member(member)

    # ── /progression-sync — ręczna sync dla admina ───────────────────────────

    @app_commands.command(
        name="progression-sync",
        description="[ADMIN] Ręcznie zsynchronizuj rangi czasowe wszystkich członków",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def progression_sync(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild   = interaction.guild
        changes = []
        for member in guild.members:
            result = await sync_member(member)
            if result:
                changes.append(result)

        if not changes:
            await interaction.followup.send("✅ Wszystkie rangi są aktualne — nic do zmiany.", ephemeral=True)
            return

        header = f"✅ Zaktualizowano **{len(changes)}** członków:\n"
        body   = "\n".join(f"• {c}" for c in changes[:30])
        if len(changes) > 30:
            body += f"\n… i {len(changes) - 30} więcej (sprawdź logi)"
        await interaction.followup.send(header + "```\n" + body + "\n```", ephemeral=True)

    # ── /progression-check @user — sprawdź konkretnego gracza ───────────────

    @app_commands.command(
        name="progression-check",
        description="[ADMIN] Sprawdź i zsynchronizuj rangę czasową wybranego gracza",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(uzytkownik="Gracz do sprawdzenia")
    async def progression_check(
        self, interaction: discord.Interaction, uzytkownik: discord.Member
    ):
        if not uzytkownik.joined_at:
            await interaction.response.send_message("❌ Brak daty dołączenia.", ephemeral=True)
            return

        days        = (discord.utils.utcnow() - uzytkownik.joined_at).days
        target      = _target_tier(days)
        current     = [r.name for r in uzytkownik.roles if r.name in ALL_TIER_NAMES]
        result      = await sync_member(uzytkownik)

        embed = discord.Embed(title="⏱ Progresja rang", color=0x5865F2)
        embed.add_field(name="Gracz",       value=uzytkownik.mention, inline=True)
        embed.add_field(name="Dni na DC",   value=str(days),          inline=True)
        embed.add_field(name="Docelowa",    value=target,             inline=True)
        embed.add_field(name="Była",        value=", ".join(current) or "brak", inline=True)
        embed.add_field(name="Zmiana",      value=result or "Bez zmian", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ProgressionCog(bot))
