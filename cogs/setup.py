import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID

# Separator: ・ (U+30FB KATAKANA MIDDLE DOT)

ROLES = [
    {"name": "👑 Admin",          "color": 0xCC0000, "hoist": True},
    {"name": "🛡️ Mod",            "color": 0x0055CC, "hoist": True},
    {"name": "🔧 Helper",         "color": 0x0099FF, "hoist": True},
    {"name": "⚔ Beta Tester",    "color": 0xAA2200, "hoist": True},
    {"name": "🌟 Premium+",       "color": 0xFF5500, "hoist": True},
    {"name": "⭐ Premium",        "color": 0xFFAA00, "hoist": False},
    {"name": "✔ Zweryfikowany",  "color": 0x226600, "hoist": False},
    {"name": "🔗 Połączony",      "color": 0x00AA88, "hoist": False},
    {"name": "📨 Rekruter",       "color": 0xFFAA00, "hoist": False},
    {"name": "🏅 Ambasador",      "color": 0xFFCC00, "hoist": False},
    {"name": "💎 Legenda Ziutka", "color": 0x00CCFF, "hoist": True},
    # Kill ranks
    {"name": "⚜ Generał",    "color": 0xFF2222, "hoist": True},
    {"name": "🦅 Pułkownik",  "color": 0xFF6600, "hoist": False},
    {"name": "🎖 Major",      "color": 0xFFAA00, "hoist": False},
    {"name": "🗡 Kapitan",    "color": 0xFFDD00, "hoist": False},
    {"name": "🔱 Porucznik",  "color": 0x00CCFF, "hoist": False},
    {"name": "⚡ Sierżant",   "color": 0x00AA88, "hoist": False},
    {"name": "🔰 Kapral",     "color": 0x226600, "hoist": False},
    {"name": "🪖 Rekrut",     "color": 0x555555, "hoist": False},
]

STRUCTURE = [
    # ── Weryfikacja ───────────────────────────────────────────────────────────
    {
        "category": "✅ WERYFIKACJA",
        "channels": [
            {
                "name": "✅・weryfikacja",
                "topic": "Kliknij przycisk i rozwiąż działanie aby uzyskać dostęp do serwera.",
                "everyone_read": True,
            },
        ],
    },
    # ── Sieć ZiutekCraft ──────────────────────────────────────────────────────
    {
        "category": "🌐 SIEĆ ZIUTEKCRAFT",
        "channels": [
            {"name": "📢・ogloszenia",  "topic": "Oficjalne ogłoszenia sieci ZiutekCraft.",          "read_only": True},
            {"name": "📰・aktualnosci", "topic": "Nowości, aktualizacje, zmiany na serwerach.",      "read_only": True},
            {"name": "📜・regulamin",   "topic": "Zasady sieci — obowiązkowe dla wszystkich.",        "read_only": True},
            {"name": "🌟・konkursy",    "topic": "Aktywne konkursy i eventy na sieci.",              "read_only": True},
            {"name": "🔔・changelog",   "topic": "Historia zmian pluginów i serwerów.",              "read_only": True},
        ],
    },
    # ── Start ─────────────────────────────────────────────────────────────────
    {
        "category": "🚀 START",
        "channels": [
            {"name": "👋・powitalnia",   "topic": "Powitanie nowych graczy.",                        "read_only": True},
            {"name": "🔗・polacz-konto", "topic": "Połącz konto Discord z Minecraft.",              "read_only": True},
        ],
    },
    # ── Statystyki (kanały głosowe jako tablice wyników) ──────────────────────
    {
        "category": "📊 STATYSTYKI",
        "channels": [
            {"name": "🌐 Sieć: …",          "type": "voice", "stats_display": True},
            {"name": "⚔ Assassin: …",       "type": "voice", "stats_display": True},
            {"name": "🌲 Survival: wkrótce", "type": "voice", "stats_display": True},
            {"name": "👥 Discord: …",        "type": "voice", "stats_display": True},
            {"name": "🔗 Połączonych: …",    "type": "voice", "stats_display": True},
        ],
    },
    # ── Assassin Arena ────────────────────────────────────────────────────────
    {
        "category": "⚔ ASSASSIN ARENA",
        "channels": [
            {"name": "🟢・status-serwera",  "topic": "Status serwera Assassin Arena — auto co 5 min.", "read_only": True},
            {"name": "🔑・dolacz-do-bety",  "topic": "Wpisz nick MC aby dołączyć do bety!",           "read_only": True},
            {"name": "📖・jak-zaczac",      "topic": "Przewodnik dla nowych: klasy, rundy, tokeny.",   "read_only": True},
            {"name": "💰・cennik",          "topic": "Ekonomia: żetony, monety, koszty ulepszeń.",     "read_only": True},
            {"name": "🏰・klany",           "topic": "System klanowy — tworzenie, poziomy, ulepszenia.","read_only": True},
            {"name": "💬・assassin-czat",   "topic": "Czat dla beta testerów Assassin Arena.",         "beta_only": True},
            {"name": "🐛・bugi",            "topic": "Zgłoś buga — kliknij przycisk.",                "beta_only": True, "read_only": True},
            {"name": "💡・sugestie",        "topic": "Dodaj sugestię — kliknij przycisk.",            "beta_only": True, "read_only": True},
            {"name": "✅・naprawione",      "topic": "Zamknięte bugi i wdrożone sugestie.",           "beta_only": True, "read_only": True},
        ],
    },
    # ── Survival ─────────────────────────────────────────────────────────────
    {
        "category": "🌲 SURVIVAL",
        "channels": [
            {"name": "📣・survival-info", "topic": "Informacje o nadchodzącym serwerze Survival.", "read_only": True},
        ],
    },
    # ── Społeczność ───────────────────────────────────────────────────────────
    {
        "category": "🔥 SPOŁECZNOŚĆ",
        "channels": [
            {"name": "💬・ogolny",    "topic": "Ogólna rozmowa o sieci ZiutekCraft i nie tylko."},
            {"name": "🖼・screeny",   "topic": "Screenshoty i klipy z rozgrywki."},
            {"name": "🗣・off-topic", "topic": "Rozmowy niezwiązane z graniem."},
        ],
    },
    # ── Bot ───────────────────────────────────────────────────────────────────
    {
        "category": "🤖 BOT",
        "channels": [
            {
                "name": "🤖・komendy",
                "topic": "Komendy bota: /daily /stats /zaproszenia — odpowiedzi tylko dla Ciebie.",
                "no_history": True,
            },
        ],
    },
    # ── Pomoc ─────────────────────────────────────────────────────────────────
    {
        "category": "🎫 POMOC",
        "channels": [
            {"name": "🎫・ticket", "topic": "Otwórz ticket jeśli masz problem.", "read_only": True},
        ],
    },
    # ── Staff ─────────────────────────────────────────────────────────────────
    {
        "category": "🔧 STAFF",
        "staff_only": True,
        "channels": [
            {"name": "📊・staff-czat",  "topic": "Wewnętrzny czat staffu."},
            {"name": "📥・beta-log",    "topic": "Log rejestracji do bety (auto)."},
            {"name": "⚠・mod-log",     "topic": "Log akcji moderacyjnych."},
            {"name": "🔧・bot-komendy", "topic": "Komendy administracyjne bota."},
        ],
    },
    # ── Głosowy ───────────────────────────────────────────────────────────────
    {
        "category": "🎙️ GŁOSOWY",
        "voice_category": True,
        "channels": [
            {"name": "💬 MAX 2",     "type": "voice", "user_limit": 2, "count": 3},
            {"name": "💬 MAX 3",     "type": "voice", "user_limit": 3, "count": 3},
            {"name": "💬 MAX 4",     "type": "voice", "user_limit": 4, "count": 2},
            {"name": "💬 MAX 5",     "type": "voice", "user_limit": 5, "count": 2},
            {"name": "🔊 UNLIMITED", "type": "voice", "user_limit": 0, "count": 2},
        ],
    },
    # ── Własne kanały ─────────────────────────────────────────────────────────
    {
        "category": "🔊 WŁASNE KANAŁY",
        "voice_category": True,
        "channels": [
            {"name": "➕ Stwórz kanał", "type": "voice", "creator": True},
        ],
    },
]


# ── Permission helpers ────────────────────────────────────────────────────────

def _ow(read=True, send=True) -> discord.PermissionOverwrite:
    return discord.PermissionOverwrite(
        read_messages=read, send_messages=send,
        view_channel=read, read_message_history=read,
    )


def _vow(view=True, conn=True) -> discord.PermissionOverwrite:
    return discord.PermissionOverwrite(view_channel=view, connect=conn, speak=conn)


def _build_overwrites(ch_def: dict, staff_only: bool, roles: dict) -> dict:
    everyone = roles["everyone"]
    admin    = roles.get("admin")
    mod      = roles.get("mod")
    beta     = roles.get("beta")
    verified = roles.get("verified")

    is_voice      = ch_def.get("type") == "voice"
    stats_display = ch_def.get("stats_display", False)
    read_only     = ch_def.get("read_only", False)
    ev_vis        = ch_def.get("everyone_read", False)
    beta_only     = ch_def.get("beta_only", False)
    no_history    = ch_def.get("no_history", False)

    if stats_display:
        # Visible but unconnectable — pure sidebar scoreboard
        ow: dict = {everyone: discord.PermissionOverwrite(view_channel=False, connect=False)}
        if verified: ow[verified] = discord.PermissionOverwrite(view_channel=True, connect=False)
        if admin:    ow[admin]    = discord.PermissionOverwrite(view_channel=True, connect=False)
        if mod:      ow[mod]      = discord.PermissionOverwrite(view_channel=True, connect=False)
        return ow

    if is_voice:
        ow = {everyone: _vow(False, False)}
        if verified: ow[verified] = _vow(True, True)
        if admin:    ow[admin]    = _vow(True, True)
        if mod:      ow[mod]      = _vow(True, True)
        return ow

    ow = {}
    if ev_vis:
        ow[everyone] = _ow(True, False)
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
            if ch_def.get("type") != "voice":
                names.add(ch_def["name"])
    return names


# ── build_server ─────────────────────────────────────────────────────────────

async def build_server(guild: discord.Guild) -> list[str]:
    log: list[str] = []

    # 1. Role
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
                reason="ZiutekBot /setup",
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

    # 2. Blokada @everyone
    log.append("\n**Blokowanie @everyone...**")
    try:
        await guild.default_role.edit(permissions=discord.Permissions.none(), reason="ZiutekBot /setup")
        log.append("  ✅ @everyone = brak uprawnień")
    except Exception as e:
        log.append(f"  ⚠ @everyone: {e}")

    # 3. Uprawnienia ról bazowych
    base_perms = discord.Permissions(
        read_messages=True, send_messages=True, read_message_history=True,
        embed_links=True, attach_files=True, add_reactions=True,
        use_application_commands=True,
    )
    for key in ("verified", "linked"):
        role = roles.get(key)
        if role:
            try:
                await role.edit(permissions=base_perms, reason="ZiutekBot /setup")
                log.append(f"  ✅ {role.name} = podstawowe uprawnienia")
            except Exception as e:
                log.append(f"  ⚠ {role.name}: {e}")

    # 4. Kategorie i kanały
    log.append("\n**Synchronizacja kategorii i kanałów...**")
    for cat_def in STRUCTURE:
        cat_name   = cat_def["category"]
        staff_only = cat_def.get("staff_only", False)
        voice_cat  = cat_def.get("voice_category", False)

        if voice_cat:
            cat_ow = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False, connect=False),
            }
            if roles.get("admin"):    cat_ow[roles["admin"]]    = discord.PermissionOverwrite(view_channel=True, connect=True)
            if roles.get("mod"):      cat_ow[roles["mod"]]      = discord.PermissionOverwrite(view_channel=True, connect=True)
            if roles.get("verified"): cat_ow[roles["verified"]] = discord.PermissionOverwrite(view_channel=True, connect=True)
        else:
            cat_ow = {guild.default_role: _ow(False, False)}
            if roles.get("admin"):  cat_ow[roles["admin"]] = _ow(True, True)
            if roles.get("mod"):    cat_ow[roles["mod"]]   = _ow(True, True)
            if not staff_only and roles.get("verified"):
                cat_ow[roles["verified"]] = _ow(True, True)

        existing_cat = discord.utils.get(guild.categories, name=cat_name)
        if existing_cat:
            try:
                await existing_cat.edit(overwrites=cat_ow, reason="ZiutekBot /setup sync")
                log.append(f"  🔄 {cat_name}")
            except Exception as e:
                log.append(f"  ⚠ {cat_name}: {e}")
            cat = existing_cat
        else:
            try:
                cat = await guild.create_category(cat_name, overwrites=cat_ow, reason="ZiutekBot /setup")
                log.append(f"  ✅ {cat_name} (nowa)")
            except Exception as e:
                log.append(f"  ❌ {cat_name}: {e}")
                continue

        for ch_def in cat_def["channels"]:
            ch_name       = ch_def["name"]
            is_voice      = ch_def.get("type") == "voice"
            stats_display = ch_def.get("stats_display", False)
            ow            = _build_overwrites(ch_def, staff_only, roles)

            if is_voice:
                count = ch_def.get("count", 1)
                ul    = ch_def.get("user_limit", 0)

                if stats_display:
                    # Match by prefix before ":" — name changes as stats update
                    prefix   = ch_name.split(":")[0].strip()
                    existing = [c for c in guild.voice_channels
                                if c.name.startswith(prefix) and c.category_id == cat.id]
                else:
                    existing = [c for c in guild.voice_channels
                                if c.name == ch_name and c.category_id == cat.id]

                if existing:
                    log.append(f"    ↩ 🔊 {ch_name} ×{len(existing)}")
                for _ in range(max(0, count - len(existing))):
                    try:
                        await guild.create_voice_channel(
                            ch_name, category=cat,
                            user_limit=ul, overwrites=ow,
                            reason="ZiutekBot /setup",
                        )
                        log.append(f"    ✅ 🔊 {ch_name} (nowy)")
                    except Exception as e:
                        log.append(f"    ❌ 🔊 {ch_name}: {e}")
            else:
                existing_ch = discord.utils.get(guild.text_channels, name=ch_name)
                if existing_ch:
                    try:
                        await existing_ch.edit(
                            overwrites=ow, topic=ch_def.get("topic", ""),
                            category=cat, reason="ZiutekBot /setup sync",
                        )
                        log.append(f"    🔄 #{ch_name}")
                    except Exception as e:
                        log.append(f"    ⚠ #{ch_name}: {e}")
                else:
                    try:
                        await guild.create_text_channel(
                            ch_name, category=cat,
                            topic=ch_def.get("topic", ""),
                            overwrites=ow, reason="ZiutekBot /setup",
                        )
                        log.append(f"    ✅ #{ch_name} (nowy)")
                    except Exception as e:
                        log.append(f"    ❌ #{ch_name}: {e}")

    log.append("\n✅ **Setup zakończony!**")
    log.append("\n**Następne kroki:**")
    log.append("1. `/cleanup` — usuń stare kanały")
    log.append("2. `/verify-panel` w #✅・weryfikacja")
    log.append("3. `/beta-panel` w #🔑・dolacz-do-bety")
    log.append("4. `/link-panel` w #🔗・polacz-konto")
    log.append("5. `/bug-panel` w #🐛・bugi")
    log.append("6. `/suggestion-panel` w #💡・sugestie")
    log.append("7. `/ticket-panel` w #🎫・ticket")
    log.append("8. `/info-setup` — embedy informacyjne")
    return log


# ── Cleanup ───────────────────────────────────────────────────────────────────

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
                await ch.delete(reason="ZiutekBot /cleanup")
                deleted.append(f"🗑 #{ch.name}")
            except Exception as e:
                errors.append(f"❌ #{ch.name}: {e}")
        result = "\n".join(deleted + errors) or "Brak kanałów do usunięcia."
        await interaction.response.edit_message(content=f"**Usunięto:**\n{result}", view=None)

    @discord.ui.button(label="❌ Anuluj", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.edit_message(content="Anulowano.", view=None)


# ── Cog ───────────────────────────────────────────────────────────────────────

class SetupCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setup", description="[ADMIN] Synchronizuj strukturę kanałów i ról serwera")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        log  = await build_server(interaction.guild)
        text = "\n".join(log)
        for chunk in [text[i:i+1900] for i in range(0, len(text), 1900)]:
            await interaction.followup.send(f"```\n{chunk}\n```", ephemeral=True)

    @app_commands.command(name="cleanup", description="[ADMIN] Usuń kanały tekstowe spoza aktualnej struktury")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def cleanup(self, interaction: discord.Interaction):
        expected = _expected_channel_names()
        extras = [ch for ch in interaction.guild.text_channels if ch.name not in expected]
        if not extras:
            await interaction.response.send_message("✅ Brak zbędnych kanałów.", ephemeral=True)
            return
        names_list = "\n".join(f"• #{ch.name}" for ch in extras)
        view = CleanupConfirmView(extras)
        await interaction.response.send_message(
            f"**Kanały spoza struktury ({len(extras)}):**\n{names_list}\n\n"
            f"Czy chcesz je usunąć? Tej operacji **nie można cofnąć**.",
            view=view, ephemeral=True,
        )

    @app_commands.command(name="sync-permissions", description="[ADMIN] Napraw uprawnienia na wszystkich kanałach")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def sync_permissions(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        fixed = errors = 0
        for channel in interaction.guild.text_channels:
            new_ow = {}
            changed = False
            for target, overwrite in channel.overwrites.items():
                can_read = overwrite.read_messages or overwrite.view_channel
                can_deny = overwrite.read_messages is False or overwrite.view_channel is False
                if can_read and overwrite.read_message_history is not True:
                    overwrite.read_message_history = True
                    changed = True
                elif can_deny and overwrite.read_message_history is not False:
                    overwrite.read_message_history = False
                    changed = True
                new_ow[target] = overwrite
            if changed:
                try:
                    await channel.edit(overwrites=new_ow, reason="sync-permissions")
                    fixed += 1
                except Exception:
                    errors += 1
        await interaction.followup.send(
            f"✅ Naprawiono **{fixed}** kanałów." + (f" ❌ Błędy: {errors}" if errors else ""),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(SetupCog(bot))
