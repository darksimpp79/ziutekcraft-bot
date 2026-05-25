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

    # ── /staz — gracz sprawdza swój czas na serwerze ─────────────────────────

    @app_commands.command(
        name="staz",
        description="Sprawdź ile czasu spędziłeś na serwerze i do kiedy awansujesz",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(uzytkownik="Opcjonalnie — sprawdź innego gracza")
    async def staz(
        self,
        interaction: discord.Interaction,
        uzytkownik: discord.Member | None = None,
    ):
        target = uzytkownik or interaction.user
        if not isinstance(target, discord.Member):
            await interaction.response.send_message("❌ Nie znaleziono gracza.", ephemeral=True)
            return
        if not target.joined_at:
            await interaction.response.send_message("❌ Brak daty dołączenia.", ephemeral=True)
            return

        now      = discord.utils.utcnow()
        delta    = now - target.joined_at
        total_h  = int(delta.total_seconds() // 3600)
        days     = delta.days
        hours    = int((delta.total_seconds() % 86400) // 3600)
        minutes  = int((delta.total_seconds() % 3600) // 60)

        # Aktualna ranga
        current_tier = _target_tier(days)
        tier_roles = [r.name for r in target.roles if r.name in ALL_TIER_NAMES]
        current_display = tier_roles[0] if tier_roles else current_tier

        # Następna ranga i ile brakuje
        next_info = ""
        for threshold, name in TIME_TIERS:
            if threshold > days:
                days_left = threshold - days
                next_info = f"Do **{name}** brakuje **{days_left}d** ({threshold - days} dni)"
                break

        # Pasek postępu do następnej rangi
        progress_bar = ""
        for i, (threshold, name) in enumerate(reversed(TIME_TIERS)):
            if days >= threshold:
                tiers_rev = list(reversed(TIME_TIERS))
                idx = tiers_rev.index((threshold, name))
                if idx + 1 < len(tiers_rev):
                    next_thresh = tiers_rev[idx + 1][0]
                    filled = min(10, int((days - threshold) / (next_thresh - threshold) * 10))
                    bar    = "█" * filled + "░" * (10 - filled)
                    pct    = min(100, int((days - threshold) / (next_thresh - threshold) * 100))
                    progress_bar = f"`{bar}` {pct}%"
                else:
                    progress_bar = "`██████████` MAX 🏆"
                break

        color_map = {
            "👋 Nowy":    0x555555,
            "🎯 Gracz":   0x808080,
            "🏆 Weteran": 0x95A5A6,
        }
        embed = discord.Embed(
            title=f"⏱ Staż na serwerze — {target.display_name}",
            color=color_map.get(current_tier, 0x5865F2),
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        embed.add_field(
            name="📅 Na serwerze od",
            value=f"<t:{int(target.joined_at.timestamp())}:D>\n"
                  f"*(<t:{int(target.joined_at.timestamp())}:R>)*",
            inline=True,
        )
        embed.add_field(
            name="⏳ Łączny czas",
            value=f"**{days}** dni **{hours}**h **{minutes}**m\n"
                  f"(*{total_h:,} godzin łącznie*)",
            inline=True,
        )
        embed.add_field(
            name="🏅 Aktualna ranga",
            value=current_display,
            inline=True,
        )
        if next_info:
            embed.add_field(name="⬆️ Następny awans", value=next_info, inline=False)
            if progress_bar:
                embed.add_field(name="Postęp", value=progress_bar, inline=False)
        else:
            embed.add_field(name="⬆️ Następny awans", value="Osiągnąłeś najwyższą rangę! 🏆", inline=False)

        embed.set_footer(text="Rangi: 👋 Nowy (0-6d) → 🎯 Gracz (7-89d) → 🏆 Weteran (90+d)")
        await interaction.response.send_message(embed=embed)

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
