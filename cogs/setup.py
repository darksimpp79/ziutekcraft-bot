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
    # ── Punkt wejścia — widoczny dla wszystkich ────────────────────────────────
    {
        "category": "🚪 WITAJ",
        "channels": [
            {
                "name": "📖-zasady",
                "topic": "Przeczytaj regulamin i kliknij przycisk aby uzyskać dostęp do serwera.",
                "everyone_read": True,
            },
            {
                "name": "📣-ogloszenia",
                "topic": "Oficjalne ogłoszenia serwera.",
                "read_only": True,
            },
            {
                "name": "🔔-changelog",
                "topic": "Historia zmian pluginu — nowe wersje, poprawki, balans.",
                "read_only": True,
            },
        ],
    },
    # ── Tryb Assassin ─────────────────────────────────────────────────────────
    {
        "category": "⚔ ASSASSIN — ARENA PVP",
        "channels": [
            {
                "name": "🟢-status-serwera",
                "topic": "Status serwera Minecraft — auto-aktualizacja co 5 min.",
                "read_only": True,
            },
            {
                "name": "🏆-hall-of-fame",
                "topic": "Top graczy — kille, prestiż, odznaki.",
                "read_only": True,
            },
            {
                "name": "📸-klipy",
                "topic": "Screenshoty i klipy z rozgrywki.",
            },
        ],
    },
    # ── Beta ──────────────────────────────────────────────────────────────────
    {
        "category": "🎟 BETA & DOSTĘP",
        "channels": [
            {
                "name": "🔑-dolacz-do-bety",
                "topic": "Kliknij przycisk i wpisz nick MC aby dołączyć do bety i trafić na whitelist.",
            },
            {"name": "💬-beta-czat",   "topic": "Czat dla beta testerów.",                              "beta_only": True},
            {"name": "🐛-bugi",        "topic": "Format: [BŁĄD] Opis + jak odtworzyć.",                 "beta_only": True},
            {"name": "💡-sugestie",    "topic": "Pomysły i propozycje zmian w rozgrywce.",              "beta_only": True},
            {"name": "✅-naprawione",  "topic": "Rozwiązane bugi i wdrożone sugestie.",                  "beta_only": True, "read_only": True},
        ],
    },
    # ── Nagrody & społeczność ─────────────────────────────────────────────────
    {
        "category": "💰 NAGRODY & SPOŁECZNOŚĆ",
        "channels": [
            {
                "name": "🔗-polacz-konto-mc",
                "topic": "Połącz konto Discord z Minecraft i zgarnij 50 znaczków. Użyj /polacz-konto",
                "no_history": True,
            },
            {
                "name": "🎁-daily",
                "topic": "Odbieraj codzienną nagrodę tokenów. Użyj /daily (wymaga połączonego konta MC).",
                "no_history": True,
            },
            {
                "name": "📨-zaproszenia",
                "topic": "Sprawdź swój wynik zaproszeń i milestony. Użyj /zaproszenia",
                "no_history": True,
            },
            {"name": "🗣-ogolny",  "topic": "Ogólna rozmowa o serwerze i nie tylko."},
            {"name": "❓-pomoc",   "topic": "Pytania techniczne, pomoc z pluginem."},
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
    return discord.PermissionOverwrite(read_messages=read, send_messages=send, view_channel=read, read_message_history=read)


async def build_server(guild: discord.Guild) -> list[str]:
    log: list[str] = []

    # ── 1. Role ───────────────────────────────────────────────────────────────
    log.append("**Tworzenie ról...**")
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

    admin    = r.get("👑 Admin")
    mod      = r.get("🛡️ Mod")
    beta     = r.get("⚔ Beta Tester")
    verified = r.get("✔ Zweryfikowany")
    linked   = r.get("🔗 Połączony")
    everyone = guild.default_role

    # ── 2. Blokada @everyone ──────────────────────────────────────────────────
    log.append("\n**Blokowanie @everyone...**")
    try:
        await everyone.edit(permissions=discord.Permissions.none(), reason="AssasinBot /setup")
        log.append("  ✅ @everyone = brak uprawnień")
    except Exception as e:
        log.append(f"  ⚠ @everyone: {e}")

    # ── 3. Uprawnienia ról ────────────────────────────────────────────────────
    for role, label, perms in [
        (verified, "Zweryfikowany", discord.Permissions(
            read_messages=True, send_messages=True, read_message_history=True,
            embed_links=True, attach_files=True, add_reactions=True,
            use_application_commands=True,
        )),
        (linked, "Połączony", discord.Permissions(
            read_messages=True, send_messages=True, read_message_history=True,
            embed_links=True, attach_files=True, add_reactions=True,
            use_application_commands=True,
        )),
    ]:
        if role:
            try:
                await role.edit(permissions=perms, reason="AssasinBot /setup")
                log.append(f"  ✅ {label} = podstawowe uprawnienia")
            except Exception as e:
                log.append(f"  ⚠ {label}: {e}")

    # ── 4. Kategorie i kanały ─────────────────────────────────────────────────
    log.append("\n**Tworzenie kategorii i kanałów...**")
    for cat_def in STRUCTURE:
        cat_name   = cat_def["category"]
        staff_only = cat_def.get("staff_only", False)

        existing_cat = discord.utils.get(guild.categories, name=cat_name)
        if existing_cat:
            cat = existing_cat
            log.append(f"  ↩ {cat_name} (już istnieje)")
        else:
            cat_ow: dict = {everyone: _ow(False, False)}
            if admin:    cat_ow[admin]    = _ow(True, True)
            if mod:      cat_ow[mod]      = _ow(True, True)
            if not staff_only and verified:
                cat_ow[verified] = _ow(True, True)
            try:
                cat = await guild.create_category(cat_name, overwrites=cat_ow,
                                                   reason="AssasinBot /setup")
                log.append(f"  ✅ {cat_name}")
            except Exception as e:
                log.append(f"  ❌ {cat_name}: {e}")
                continue

        for ch_def in cat_def["channels"]:
            ch_name      = ch_def["name"]
            beta_only    = ch_def.get("beta_only", False)
            read_only    = ch_def.get("read_only", False)
            everyone_vis = ch_def.get("everyone_read", False)
            no_history   = ch_def.get("no_history", False)

            if discord.utils.get(guild.text_channels, name=ch_name):
                log.append(f"    ↩ #{ch_name}")
                continue

            ow: dict = {}

            if everyone_vis:
                # Widoczny dla wszystkich (weryfikacja + ogłoszenia)
                ow[everyone] = _ow(read=True,  send=False)
                if verified: ow[verified] = _ow(True, False)
                if admin:    ow[admin]    = _ow(True, True)
                if mod:      ow[mod]      = _ow(True, True)
            elif staff_only:
                ow[everyone] = _ow(False, False)
                if admin:    ow[admin]    = _ow(True, True)
                if mod:      ow[mod]      = _ow(True, True)
            elif beta_only:
                ow[everyone]  = _ow(False, False)
                if verified:  ow[verified]  = _ow(False, False)
                if beta:      ow[beta]      = _ow(True, not read_only)
                if admin:     ow[admin]     = _ow(True, True)
                if mod:       ow[mod]       = _ow(True, True)
            else:
                ow[everyone] = _ow(False, False)
                if verified:
                    ow[verified] = _ow(True, not read_only)
                    if no_history:
                        ow[verified].read_message_history = False
                if admin:     ow[admin]     = _ow(True, True)
                if mod:       ow[mod]       = _ow(True, True)

            try:
                await guild.create_text_channel(
                    ch_name, category=cat,
                    topic=ch_def.get("topic", ""),
                    overwrites=ow,
                    reason="AssasinBot /setup",
                )
                log.append(f"    ✅ #{ch_name}")
            except Exception as e:
                log.append(f"    ❌ #{ch_name}: {e}")

    log.append("\n✅ **Setup zakończony!**")
    log.append("\n**Następne kroki:**")
    log.append("1. `/verify-panel` w #📖-zasady")
    log.append("2. `/beta-panel` w #🔑-dolacz-do-bety")
    log.append("3. Uzupełnij ID ról i kanałów w .env (BETA_ROLE_ID, STATUS_CHAN_ID, itd.)")
    log.append("4. Upewnij się że port LINK_BOT_PORT (domyślnie 8642) jest otwarty na firewallu VPS")
    return log


class SetupCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="setup",
        description="[ADMIN] Stwórz strukturę kanałów i ról serwera ZiutekCraft",
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
