import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID

# ─────────────────────────────────────────────────────────────────────────────
# Struktura serwera ZiutekCraft
# Uprawnienia:
#   @everyone     = BRAK (gate wejściowa)
#   Zweryfikowany = kanały ogólne + społeczność
#   Beta Tester   = dodatkowe kanały beta
#   Połączony     = kanały nagród (#daily, #zaproszenia, #polacz-konto-mc)
#   Mod/Admin     = wszystko łącznie ze staffem
# ─────────────────────────────────────────────────────────────────────────────

ROLES = [
    {"name": "👑 Admin",         "color": 0xCC0000, "hoist": True},
    {"name": "🛡️ Mod",           "color": 0x0055CC, "hoist": True},
    {"name": "⚔ Beta Tester",   "color": 0xAA2200, "hoist": True},
    {"name": "✔ Zweryfikowany", "color": 0x226600, "hoist": False},
    {"name": "🔗 Połączony",     "color": 0x00AA88, "hoist": False},
    {"name": "📨 Rekruter",      "color": 0xFFAA00, "hoist": False},
    {"name": "🏅 Ambasador",     "color": 0xFFCC00, "hoist": False},
    {"name": "💎 Legenda Ziutka", "color": 0x00CCFF, "hoist": True},
    # LP ranks
    {"name": "🔧 Helper",    "color": 0x0099FF, "hoist": True},
    {"name": "🌟 Premium+",  "color": 0xFF5500, "hoist": True},
    {"name": "⭐ Premium",   "color": 0xFFAA00, "hoist": False},
    # Kill ranks
    {"name": "⚜ Generał",   "color": 0xFF2222, "hoist": True},
    {"name": "🦅 Pułkownik", "color": 0xFF6600, "hoist": False},
    {"name": "🎖 Major",     "color": 0xFFAA00, "hoist": False},
    {"name": "🗡 Kapitan",   "color": 0xFFDD00, "hoist": False},
    {"name": "🔱 Porucznik", "color": 0x00CCFF, "hoist": False},
    {"name": "⚡ Sierżant",  "color": 0x00AA88, "hoist": False},
    {"name": "🔰 Kapral",    "color": 0x226600, "hoist": False},
    {"name": "🪖 Rekrut",    "color": 0x555555, "hoist": False},
]

STRUCTURE = [
    # ── Weryfikacja — widoczna dla wszystkich ─────────────────────────────────
    {
        "category": "✅ WERYFIKACJA",
        "channels": [
            {
                "name": "✅-weryfikacja",
                "topic": "Kliknij przycisk i rozwiąż działanie aby uzyskać dostęp do serwera.",
                "everyone_read": True,
            },
        ],
    },
    # ── Statystyki — read-only, bot auto-aktualizuje ──────────────────────────
    {
        "category": "📊 STATYSTYKI",
        "channels": [
            {"name": "🟢-status-serwera",  "topic": "Status serwera MC — auto-aktualizacja co 5 min.", "read_only": True},
            {"name": "💀-top-killer",       "topic": "Aktualny lider rankingu killów — auto.", "read_only": True},
            {"name": "🏅-sezon",            "topic": "Numer aktywnego sezonu i jego koniec.", "read_only": True},
        ],
    },
    # ── Start ─────────────────────────────────────────────────────────────────
    {
        "category": "🚀 START",
        "channels": [
            {"name": "👋-powitalnia",    "topic": "Powitanie nowych graczy — embed z botami.", "read_only": True},
            {"name": "📖-jak-zaczac",    "topic": "Przewodnik dla nowych: klasy, rundy, tokeny.", "read_only": True},
            {"name": "🔑-dolacz-do-bety","topic": "Kliknij przycisk, wpisz nick MC — trafisz na whitelist!"},
        ],
    },
    # ── Informacje ────────────────────────────────────────────────────────────
    {
        "category": "📋 INFORMACJE",
        "channels": [
            {"name": "📢-ogloszenia",  "topic": "Oficjalne ogłoszenia serwera.", "read_only": True},
            {"name": "🔔-changelog",   "topic": "Historia zmian pluginu — nowe wersje, poprawki, balans.", "read_only": True},
            {"name": "📜-regulamin",   "topic": "Zasady serwera — przeczytaj przed grą.", "read_only": True},
            {"name": "💰-cennik",      "topic": "Koszty ulepszeń, klanów, prestiżu — tokeny i znaczki.", "read_only": True},
            {"name": "🏰-klany",       "topic": "System klanowy — jak działają klany, ulepszenia, wkład osobisty.", "read_only": True},
            {"name": "💜-boosty",      "topic": "Aktywne boosty Discord i ich bonusy.", "read_only": True},
            {"name": "🌟-konkursy",    "topic": "Aktywne konkursy i eventy.", "read_only": True},
        ],
    },
    # ── Społeczność ───────────────────────────────────────────────────────────
    {
        "category": "🔥 SPOŁECZNOŚĆ",
        "channels": [
            {"name": "💬-ogolny",     "topic": "Ogólna rozmowa o serwerze i nie tylko."},
            {"name": "🖼-screeny",    "topic": "Screenshoty i klipy z rozgrywki."},
            {"name": "⭐-propozycje", "topic": "Pomysły na nowe funkcje i zmiany w grze."},
        ],
    },
    # ── Gra ───────────────────────────────────────────────────────────────────
    {
        "category": "🎮 GRA",
        "channels": [
            {"name": "💀-kill-feed",   "topic": "Automatyczne posty: killstreaki 10+, first blood, rekordy.", "read_only": True},
            {"name": "🏆-rankingi",    "topic": "Top 10 graczy i klanów — aktualizowane przez bota co godzinę.", "read_only": True},
            {"name": "📝-patch-notes", "topic": "Szczegółowe notki do każdej aktualizacji pluginu.", "read_only": True},
        ],
    },
    # ── Bot ───────────────────────────────────────────────────────────────────
    {
        "category": "🤖 BOT",
        "channels": [
            {
                "name": "🤖-komendy",
                "topic": "Wszystkie komendy bota: /daily /stats /zaproszenia /top /polacz — odpowiedzi widoczne tylko dla Ciebie.",
                "no_history": True,
            },
            {
                "name": "🔗-polacz-konto",
                "topic": "Tutorial połączenia konta DC-MC. Użyj /polacz-konto tutaj.",
                "no_history": True,
            },
        ],
    },
    # ── Beta (tylko Beta Testerzy) ────────────────────────────────────────────
    {
        "category": "🎟 BETA",
        "channels": [
            {"name": "💬-beta-czat",  "topic": "Czat dla beta testerów.", "beta_only": True},
            {"name": "🐛-bugi",       "topic": "Format: [BŁĄD] Opis + kroki do odtworzenia.", "beta_only": True},
            {"name": "💡-sugestie",   "topic": "Pomysły i propozycje zmian w rozgrywce.", "beta_only": True},
            {"name": "✅-naprawione", "topic": "Zamknięte bugi i wdrożone sugestie.", "beta_only": True, "read_only": True},
        ],
    },
    # ── Pomoc ─────────────────────────────────────────────────────────────────
    {
        "category": "🎫 POMOC",
        "channels": [
            {"name": "🎫-ticket", "topic": "Otwórz ticket jeśli masz problem lub pytanie do staffu."},
        ],
    },
    # ── Staff ─────────────────────────────────────────────────────────────────
    {
        "category": "🔧 STAFF",
        "staff_only": True,
        "channels": [
            {"name": "📊-staff-czat",  "topic": "Wewnętrzny czat staffu."},
            {"name": "📥-beta-log",    "topic": "Log rejestracji do bety (auto)."},
            {"name": "⚠-mod-log",     "topic": "Log akcji moderacyjnych."},
            {"name": "🔧-bot-komendy", "topic": "Komendy administracyjne bota."},
        ],
    },
]


def _ow(read=True, send=True) -> discord.PermissionOverwrite:
    return discord.PermissionOverwrite(
        read_messages=read, send_messages=send,
        view_channel=read, read_message_history=read,
    )


def _build_overwrites(ch_def: dict, staff_only: bool, roles: dict) -> dict:
    """Build permission overwrites dict for a channel definition."""
    everyone  = roles["everyone"]
    admin     = roles.get("admin")
    mod       = roles.get("mod")
    beta      = roles.get("beta")
    verified  = roles.get("verified")

    read_only    = ch_def.get("read_only", False)
    everyone_vis = ch_def.get("everyone_read", False)
    beta_only    = ch_def.get("beta_only", False)
    no_history   = ch_def.get("no_history", False)

    ow: dict = {}
    if everyone_vis:
        ow[everyone] = _ow(read=True, send=False)
        if verified: ow[verified] = _ow(True, False)
        if admin:    ow[admin]    = _ow(True, True)
        if mod:      ow[mod]      = _ow(True, True)
    elif staff_only:
        ow[everyone] = _ow(False, False)
        if admin:    ow[admin]    = _ow(True, True)
        if mod:      ow[mod]      = _ow(True, True)
    elif beta_only:
        ow[everyone] = _ow(False, False)
        if verified: ow[verified] = _ow(False, False)
        if beta:     ow[beta]     = _ow(True, not read_only)
        if admin:    ow[admin]    = _ow(True, True)
        if mod:      ow[mod]      = _ow(True, True)
    else:
        ow[everyone] = _ow(False, False)
        if verified:
            ow[verified] = _ow(True, not read_only)
            if no_history:
                ow[verified].read_message_history = False
        if admin:    ow[admin]    = _ow(True, True)
        if mod:      ow[mod]      = _ow(True, True)
    return ow


def _expected_channel_names() -> set[str]:
    names: set[str] = set()
    for cat_def in STRUCTURE:
        for ch_def in cat_def["channels"]:
            names.add(ch_def["name"])
    return names


async def build_server(guild: discord.Guild) -> list[str]:
    log: list[str] = []

    # ── 1. Role ───────────────────────────────────────────────────────────────
    log.append("**Tworzenie / weryfikacja ról...**")
    r: dict[str, discord.Role] = {}
    for rd in ROLES:
        existing = discord.utils.get(guild.roles, name=rd["name"])
        if existing:
            r[rd["name"]] = existing
            log.append(f"  ↩ {rd['name']} (już istnieje)")
            continue
        try:
            role = await guild.create_role(
                name=rd["name"],
                color=discord.Color(rd["color"]),
                hoist=rd.get("hoist", False),
                reason="AssasinBot /setup",
            )
            r[role.name] = role
            log.append(f"  ✅ {role.name}")
        except Exception as e:
            log.append(f"  ❌ {rd['name']}: {e}")

    roles = {
        "everyone": guild.default_role,
        "admin":    r.get("👑 Admin"),
        "mod":      r.get("🛡️ Mod"),
        "beta":     r.get("⚔ Beta Tester"),
        "verified": r.get("✔ Zweryfikowany"),
        "linked":   r.get("🔗 Połączony"),
    }

    # ── 2. Blokada @everyone ──────────────────────────────────────────────────
    log.append("\n**Blokowanie @everyone...**")
    try:
        await guild.default_role.edit(permissions=discord.Permissions.none(), reason="AssasinBot /setup")
        log.append("  ✅ @everyone = brak uprawnień")
    except Exception as e:
        log.append(f"  ⚠ @everyone: {e}")

    # ── 3. Uprawnienia ról ────────────────────────────────────────────────────
    base_perms = discord.Permissions(
        read_messages=True, send_messages=True, read_message_history=True,
        embed_links=True, attach_files=True, add_reactions=True,
        use_application_commands=True,
    )
    for key, label in [("verified", "Zweryfikowany"), ("linked", "Połączony")]:
        role = roles.get(key)
        if role:
            try:
                await role.edit(permissions=base_perms, reason="AssasinBot /setup")
                log.append(f"  ✅ {label} = podstawowe uprawnienia")
            except Exception as e:
                log.append(f"  ⚠ {label}: {e}")

    # ── 4. Kategorie i kanały (tworzy nowe + aktualizuje istniejące) ──────────
    log.append("\n**Synchronizacja kategorii i kanałów...**")
    for cat_def in STRUCTURE:
        cat_name   = cat_def["category"]
        staff_only = cat_def.get("staff_only", False)

        cat_ow: dict = {guild.default_role: _ow(False, False)}
        if roles.get("admin"):  cat_ow[roles["admin"]] = _ow(True, True)
        if roles.get("mod"):    cat_ow[roles["mod"]]   = _ow(True, True)
        if not staff_only and roles.get("verified"):
            cat_ow[roles["verified"]] = _ow(True, True)

        existing_cat = discord.utils.get(guild.categories, name=cat_name)
        if existing_cat:
            try:
                await existing_cat.edit(overwrites=cat_ow, reason="AssasinBot /setup sync")
                log.append(f"  🔄 {cat_name} (uprawnienia zaktualizowane)")
            except Exception as e:
                log.append(f"  ⚠ {cat_name}: {e}")
            cat = existing_cat
        else:
            try:
                cat = await guild.create_category(cat_name, overwrites=cat_ow, reason="AssasinBot /setup")
                log.append(f"  ✅ {cat_name} (nowa)")
            except Exception as e:
                log.append(f"  ❌ {cat_name}: {e}")
                continue

        for ch_def in cat_def["channels"]:
            ch_name = ch_def["name"]
            ow = _build_overwrites(ch_def, staff_only, roles)
            existing_ch = discord.utils.get(guild.text_channels, name=ch_name)
            if existing_ch:
                try:
                    await existing_ch.edit(
                        overwrites=ow,
                        topic=ch_def.get("topic", ""),
                        category=cat,
                        reason="AssasinBot /setup sync",
                    )
                    log.append(f"    🔄 #{ch_name} (uprawnienia zaktualizowane)")
                except Exception as e:
                    log.append(f"    ⚠ #{ch_name}: {e}")
            else:
                try:
                    await guild.create_text_channel(
                        ch_name, category=cat,
                        topic=ch_def.get("topic", ""),
                        overwrites=ow,
                        reason="AssasinBot /setup",
                    )
                    log.append(f"    ✅ #{ch_name} (nowy)")
                except Exception as e:
                    log.append(f"    ❌ #{ch_name}: {e}")

    log.append("\n✅ **Setup zakończony!**")
    log.append("\n**Następne kroki:**")
    log.append("1. `/cleanup` — usuń stare kanały spoza struktury")
    log.append("2. `/verify-panel` w #✅-weryfikacja")
    log.append("3. `/beta-panel` w #🔑-dolacz-do-bety")
    log.append("4. `/info-setup` — wypełnij kanały informacyjne embedami")
    log.append("5. Uzupełnij .env: BETA_ROLE_ID, STATUS_CHAN_ID, BETA_LOG_CHAN_ID")
    return log


# ── Cleanup confirmation view ─────────────────────────────────────────────────

class CleanupConfirmView(discord.ui.View):
    def __init__(self, channels_to_delete: list[discord.TextChannel]):
        super().__init__(timeout=60)
        self.channels_to_delete = channels_to_delete

    @discord.ui.button(label="✅ Tak, usuń", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        deleted, errors = [], []
        for ch in self.channels_to_delete:
            try:
                await ch.delete(reason="AssasinBot /cleanup")
                deleted.append(f"🗑 #{ch.name}")
            except Exception as e:
                errors.append(f"❌ #{ch.name}: {e}")
        result = "\n".join(deleted + errors) or "Brak kanałów do usunięcia."
        await interaction.response.edit_message(content=f"**Usunięto:**\n{result}", view=None)

    @discord.ui.button(label="❌ Anuluj", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.edit_message(content="Anulowano.", view=None)


class SetupCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="setup",
        description="[ADMIN] Synchronizuj strukturę kanałów i ról serwera",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        log  = await build_server(interaction.guild)
        text = "\n".join(log)
        for chunk in [text[i:i+1900] for i in range(0, len(text), 1900)]:
            await interaction.followup.send(f"```\n{chunk}\n```", ephemeral=True)

    @app_commands.command(
        name="cleanup",
        description="[ADMIN] Pokaż i usuń kanały spoza aktualnej struktury serwera",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def cleanup(self, interaction: discord.Interaction):
        expected = _expected_channel_names()
        # Ignoruj kanały systemowe (bez nazwy lub zaczynające się od system-)
        extras = [
            ch for ch in interaction.guild.text_channels
            if ch.name not in expected
        ]
        if not extras:
            await interaction.response.send_message(
                "✅ Brak zbędnych kanałów — struktura jest czysta.", ephemeral=True
            )
            return

        names_list = "\n".join(f"• #{ch.name}" for ch in extras)
        view = CleanupConfirmView(extras)
        await interaction.response.send_message(
            f"**Kanały spoza struktury ({len(extras)}):**\n{names_list}\n\n"
            f"Czy chcesz je usunąć? Tej operacji **nie można cofnąć**.",
            view=view,
            ephemeral=True,
        )

    @app_commands.command(
        name="sync-permissions",
        description="[ADMIN] Napraw read_message_history na wszystkich istniejących kanałach",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def sync_permissions(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        fixed = 0
        errors = 0

        for channel in guild.text_channels:
            new_overwrites = {}
            changed = False

            for target, overwrite in channel.overwrites.items():
                # Sprawdź czy read_messages jest explicite ustawione
                can_read = overwrite.read_messages
                can_view = overwrite.view_channel

                # Ustal czy ta rola/osoba może czytać kanał
                if can_read is True or can_view is True:
                    if overwrite.read_message_history is not True:
                        overwrite.read_message_history = True
                        changed = True
                elif can_read is False or can_view is False:
                    if overwrite.read_message_history is not False:
                        overwrite.read_message_history = False
                        changed = True

                new_overwrites[target] = overwrite

            if changed:
                try:
                    await channel.edit(overwrites=new_overwrites, reason="sync-permissions: fix read_message_history")
                    fixed += 1
                except Exception:
                    errors += 1

        await interaction.followup.send(
            f"✅ Naprawiono **{fixed}** kanałów. "
            + (f"❌ Błędy: {errors}" if errors else ""),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(SetupCog(bot))
