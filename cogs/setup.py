import json
import logging
import os
import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID

log = logging.getLogger(__name__)

EXTRA_MODES_FILE = "data/game_modes_extra.json"

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
    {"name": "⚜ Generał",        "color": 0xFF2222, "hoist": True},
    {"name": "🦅 Pułkownik",      "color": 0xFF6600, "hoist": False},
    {"name": "🎖 Major",          "color": 0xFFAA00, "hoist": False},
    {"name": "🗡 Kapitan",        "color": 0xFFDD00, "hoist": False},
    {"name": "🔱 Porucznik",      "color": 0x00CCFF, "hoist": False},
    {"name": "⚡ Sierżant",       "color": 0x00AA88, "hoist": False},
    {"name": "🔰 Kapral",         "color": 0x226600, "hoist": False},
    {"name": "🪖 Rekrut",         "color": 0x555555, "hoist": False},
]

# ── Built-in game modes ───────────────────────────────────────────────────────
# Each mode creates:
#   {emoji} {LABEL} — INFO   — public (everyone can view, not send)
#   {emoji} {LABEL} — GRACZE — mode_role gated (if info_only=False)
# A stats voice channel is also added to 📊 STATYSTYKI.

GAME_MODES: list[dict] = [
    {
        "name": "Assassin Arena",
        "slug": "assassin",
        "emoji": "⚔",
        "label": "ASSASSIN ARENA",
        "role_name": "⚔ Beta Tester",
        "role_color": 0xAA2200,
        "info_only": False,
        "info_channels": [
            {"name": "🟢・status-serwera",  "topic": "Status serwera Assassin Arena — auto co 5 min.", "read_only": True},
            {"name": "🔑・dolacz-do-bety",  "topic": "Wpisz nick MC aby dołączyć do bety!",           "read_only": True},
            {"name": "📖・jak-zaczac",      "topic": "Przewodnik dla nowych: klasy, rundy, tokeny.",   "read_only": True},
            {"name": "💰・cennik",          "topic": "Ekonomia: żetony, monety, koszty ulepszeń.",     "read_only": True},
            {"name": "🏰・klany",           "topic": "System klanowy — tworzenie, poziomy, ulepszenia.", "read_only": True},
        ],
        "player_channels": [
            {"name": "💬・assassin-czat",  "topic": "Czat dla beta testerów Assassin Arena."},
            {"name": "🐛・bugi",           "topic": "Zgłoś buga — kliknij przycisk.",      "read_only": True},
            {"name": "💡・sugestie",       "topic": "Dodaj sugestię — kliknij przycisk.",  "read_only": True},
            {"name": "✅・naprawione",     "topic": "Zamknięte bugi i wdrożone sugestie.", "read_only": True},
        ],
        "stats_channel": "⚔ Assassin: …",
    },
    {
        "name": "Survival",
        "slug": "survival",
        "emoji": "🌲",
        "label": "SURVIVAL",
        "role_name": None,
        "role_color": 0x228B22,
        "info_only": True,
        "info_channels": [
            {"name": "📣・survival-info", "topic": "Informacje o nadchodzącym serwerze Survival.", "read_only": True},
        ],
        "player_channels": [],
        "stats_channel": "🌲 Survival: wkrótce",
    },
]

# ── Static sections ───────────────────────────────────────────────────────────

STRUCTURE_TOP: list[dict] = [
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
    {
        "category": "🌐 SIEĆ ZIUTEKCRAFT",
        "channels": [
            {"name": "📢・ogloszenia",  "topic": "Oficjalne ogłoszenia sieci ZiutekCraft.",     "read_only": True},
            {"name": "📰・aktualnosci", "topic": "Nowości, aktualizacje, zmiany na serwerach.", "read_only": True},
            {"name": "📜・regulamin",   "topic": "Zasady sieci — obowiązkowe dla wszystkich.",  "read_only": True},
            {"name": "🌟・konkursy",    "topic": "Aktywne konkursy i eventy na sieci.",         "read_only": True},
            {"name": "🔔・changelog",   "topic": "Historia zmian pluginów i serwerów.",         "read_only": True},
        ],
    },
    {
        "category": "🚀 START",
        "channels": [
            {"name": "👋・powitalnia",   "topic": "Powitanie nowych graczy.",           "read_only": True},
            {"name": "🔗・polacz-konto", "topic": "Połącz konto Discord z Minecraft.", "read_only": True},
        ],
    },
    {
        "category": "📊 STATYSTYKI",
        "stats_category": True,
        "channels": [
            {"name": "🌐 Sieć: …",       "type": "voice", "stats_display": True},
            {"name": "👥 Discord: …",     "type": "voice", "stats_display": True},
            {"name": "🔗 Połączonych: …", "type": "voice", "stats_display": True},
        ],
    },
]

STRUCTURE_BOTTOM: list[dict] = [
    {
        "category": "🔥 SPOŁECZNOŚĆ",
        "channels": [
            {"name": "💬・ogolny",    "topic": "Ogólna rozmowa o sieci ZiutekCraft i nie tylko."},
            {"name": "🖼・screeny",   "topic": "Screenshoty i klipy z rozgrywki."},
            {"name": "🗣・off-topic", "topic": "Rozmowy niezwiązane z graniem."},
        ],
    },
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
    {
        "category": "🎫 POMOC",
        "channels": [
            {"name": "🎫・ticket", "topic": "Otwórz ticket jeśli masz problem.", "read_only": True},
        ],
    },
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
    {
        "category": "🔊 WŁASNE KANAŁY",
        "voice_category": True,
        "channels": [
            {"name": "➕ Stwórz kanał", "type": "voice", "creator": True},
        ],
    },
]


# ── Extra modes (persisted across restarts) ───────────────────────────────────

def _load_extra_modes() -> list[dict]:
    if not os.path.exists(EXTRA_MODES_FILE):
        return []
    try:
        with open(EXTRA_MODES_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_extra_modes(modes: list[dict]) -> None:
    os.makedirs(os.path.dirname(EXTRA_MODES_FILE), exist_ok=True)
    with open(EXTRA_MODES_FILE, "w", encoding="utf-8") as f:
        json.dump(modes, f, ensure_ascii=False, indent=2)


def _all_modes() -> list[dict]:
    return GAME_MODES + _load_extra_modes()


# ── Permission helpers ────────────────────────────────────────────────────────

def _ow(read: bool = True, send: bool = True) -> discord.PermissionOverwrite:
    return discord.PermissionOverwrite(
        read_messages=read, send_messages=send,
        view_channel=read, read_message_history=read,
    )


def _vow(view: bool = True, conn: bool = True) -> discord.PermissionOverwrite:
    return discord.PermissionOverwrite(view_channel=view, connect=conn, speak=conn)


def _build_overwrites(
    ch_def: dict,
    staff_only: bool,
    roles: dict,
    mode_role: discord.Role | None = None,
) -> dict:
    everyone = roles["everyone"]
    admin    = roles.get("admin")
    mod      = roles.get("mod")
    verified = roles.get("verified")

    is_voice      = ch_def.get("type") == "voice"
    stats_display = ch_def.get("stats_display", False)
    read_only     = ch_def.get("read_only", False)
    ev_vis        = ch_def.get("everyone_read", False)
    no_history    = ch_def.get("no_history", False)

    if stats_display:
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
        # Public channel — visible even to unverified
        ow[everyone] = _ow(True, False)
        if verified: ow[verified] = _ow(True, False)
        if admin:    ow[admin]    = _ow(True, True)
        if mod:      ow[mod]      = _ow(True, True)
    elif staff_only:
        ow[everyone] = _ow(False, False)
        if admin:    ow[admin]    = _ow(True, True)
        if mod:      ow[mod]      = _ow(True, True)
    elif mode_role is not None:
        # Visible only to mode_role holders (and staff)
        ow[everyone]  = _ow(False, False)
        if verified: ow[verified] = _ow(False, False)
        ow[mode_role] = _ow(True, not read_only)
        if admin:    ow[admin]    = _ow(True, True)
        if mod:      ow[mod]      = _ow(True, True)
    else:
        # Default: visible to verified
        ow[everyone] = _ow(False, False)
        if verified:
            ow[verified] = _ow(True, not read_only)
            if no_history:
                ow[verified].read_message_history = False
        if admin:    ow[admin]    = _ow(True, True)
        if mod:      ow[mod]      = _ow(True, True)
    return ow


def _resolve_roles(guild: discord.Guild) -> dict:
    return {
        "everyone": guild.default_role,
        "admin":    discord.utils.get(guild.roles, name="👑 Admin"),
        "mod":      discord.utils.get(guild.roles, name="🛡️ Mod"),
        "verified": discord.utils.get(guild.roles, name="✔ Zweryfikowany"),
        "linked":   discord.utils.get(guild.roles, name="🔗 Połączony"),
    }


# ── Core category/channel sync ────────────────────────────────────────────────

async def _process_category(
    guild: discord.Guild,
    cat_def: dict,
    roles: dict,
    lines: list[str],
    mode_role: discord.Role | None = None,
    cat_overwrites: dict | None = None,
) -> None:
    cat_name   = cat_def["category"]
    staff_only = cat_def.get("staff_only", False)
    voice_cat  = cat_def.get("voice_category", False)
    stats_cat  = cat_def.get("stats_category", False)

    if cat_overwrites is not None:
        cat_ow = cat_overwrites
    elif voice_cat:
        cat_ow = {guild.default_role: discord.PermissionOverwrite(view_channel=False, connect=False)}
        if roles.get("admin"):    cat_ow[roles["admin"]]    = discord.PermissionOverwrite(view_channel=True, connect=True)
        if roles.get("mod"):      cat_ow[roles["mod"]]      = discord.PermissionOverwrite(view_channel=True, connect=True)
        if roles.get("verified"): cat_ow[roles["verified"]] = discord.PermissionOverwrite(view_channel=True, connect=True)
    elif stats_cat:
        cat_ow = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        if roles.get("verified"): cat_ow[roles["verified"]] = discord.PermissionOverwrite(view_channel=True)
        if roles.get("admin"):    cat_ow[roles["admin"]]    = discord.PermissionOverwrite(view_channel=True)
        if roles.get("mod"):      cat_ow[roles["mod"]]      = discord.PermissionOverwrite(view_channel=True)
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
            lines.append(f"  🔄 {cat_name}")
        except Exception as e:
            lines.append(f"  ⚠ {cat_name}: {e}")
        cat = existing_cat
    else:
        try:
            cat = await guild.create_category(cat_name, overwrites=cat_ow, reason="ZiutekBot /setup")
            lines.append(f"  ✅ {cat_name} (nowa)")
        except Exception as e:
            lines.append(f"  ❌ {cat_name}: {e}")
            return

    for ch_def in cat_def["channels"]:
        ch_name       = ch_def["name"]
        is_voice      = ch_def.get("type") == "voice"
        stats_display = ch_def.get("stats_display", False)
        ow            = _build_overwrites(ch_def, staff_only, roles, mode_role=mode_role)

        if is_voice:
            count = ch_def.get("count", 1)
            ul    = ch_def.get("user_limit", 0)
            if stats_display:
                prefix   = ch_name.split(":")[0].strip()
                existing = [c for c in guild.voice_channels
                            if c.name.startswith(prefix) and c.category_id == cat.id]
            else:
                existing = [c for c in guild.voice_channels
                            if c.name == ch_name and c.category_id == cat.id]
            if existing:
                lines.append(f"    ↩ 🔊 {ch_name} ×{len(existing)}")
            for _ in range(max(0, count - len(existing))):
                try:
                    await guild.create_voice_channel(
                        ch_name, category=cat, user_limit=ul,
                        overwrites=ow, reason="ZiutekBot /setup",
                    )
                    lines.append(f"    ✅ 🔊 {ch_name} (nowy)")
                except Exception as e:
                    lines.append(f"    ❌ 🔊 {ch_name}: {e}")
        else:
            existing_ch = discord.utils.get(guild.text_channels, name=ch_name)
            if existing_ch:
                try:
                    await existing_ch.edit(
                        overwrites=ow, topic=ch_def.get("topic", ""),
                        category=cat, reason="ZiutekBot /setup sync",
                    )
                    lines.append(f"    🔄 #{ch_name}")
                except Exception as e:
                    lines.append(f"    ⚠ #{ch_name}: {e}")
            else:
                try:
                    await guild.create_text_channel(
                        ch_name, category=cat, topic=ch_def.get("topic", ""),
                        overwrites=ow, reason="ZiutekBot /setup",
                    )
                    lines.append(f"    ✅ #{ch_name} (nowy)")
                except Exception as e:
                    lines.append(f"    ❌ #{ch_name}: {e}")


async def create_mode_structure(
    guild: discord.Guild,
    mode: dict,
    roles: dict,
    lines: list[str],
) -> None:
    mode_role: discord.Role | None = None
    if mode.get("role_name"):
        mode_role = discord.utils.get(guild.roles, name=mode["role_name"])

    # INFO category — publicly visible (even unverified)
    info_cat_name = f"{mode['emoji']} {mode['label']} — INFO"
    info_cat_ow = {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=True, send_messages=False, read_message_history=True
        ),
    }
    if roles.get("admin"): info_cat_ow[roles["admin"]] = _ow(True, True)
    if roles.get("mod"):   info_cat_ow[roles["mod"]]   = _ow(True, True)

    await _process_category(
        guild,
        {
            "category": info_cat_name,
            "channels": [dict(ch, everyone_read=True) for ch in mode["info_channels"]],
        },
        roles, lines,
        mode_role=None,
        cat_overwrites=info_cat_ow,
    )

    # PLAYER category — visible only to mode_role
    if not mode.get("info_only") and mode_role:
        player_cat_name = f"{mode['emoji']} {mode['label']} — GRACZE"
        player_cat_ow = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
        }
        if roles.get("verified"): player_cat_ow[roles["verified"]] = discord.PermissionOverwrite(view_channel=False)
        player_cat_ow[mode_role] = discord.PermissionOverwrite(
            view_channel=True, send_messages=True, read_message_history=True
        )
        if roles.get("admin"): player_cat_ow[roles["admin"]] = _ow(True, True)
        if roles.get("mod"):   player_cat_ow[roles["mod"]]   = _ow(True, True)

        await _process_category(
            guild,
            {
                "category": player_cat_name,
                "channels": mode.get("player_channels", []),
            },
            roles, lines,
            mode_role=mode_role,
            cat_overwrites=player_cat_ow,
        )


async def _add_mode_stats_channel(
    guild: discord.Guild,
    mode: dict,
    roles: dict,
    lines: list[str],
) -> None:
    stats_ch_name = mode.get("stats_channel")
    if not stats_ch_name:
        return
    stats_cat = discord.utils.get(guild.categories, name="📊 STATYSTYKI")
    if not stats_cat:
        return
    prefix   = stats_ch_name.split(":")[0].strip()
    existing = [c for c in guild.voice_channels
                if c.name.startswith(prefix) and c.category_id == stats_cat.id]
    if existing:
        lines.append(f"    ↩ 🔊 {stats_ch_name}")
        return
    ow = {guild.default_role: discord.PermissionOverwrite(view_channel=False, connect=False)}
    if roles.get("verified"): ow[roles["verified"]] = discord.PermissionOverwrite(view_channel=True, connect=False)
    if roles.get("admin"):    ow[roles["admin"]]    = discord.PermissionOverwrite(view_channel=True, connect=False)
    if roles.get("mod"):      ow[roles["mod"]]      = discord.PermissionOverwrite(view_channel=True, connect=False)
    try:
        await guild.create_voice_channel(
            stats_ch_name, category=stats_cat, overwrites=ow, reason="ZiutekBot /setup",
        )
        lines.append(f"    ✅ 🔊 {stats_ch_name} (nowy)")
    except Exception as e:
        lines.append(f"    ❌ 🔊 {stats_ch_name}: {e}")


def _expected_channel_names() -> set[str]:
    names: set[str] = set()
    for section in (STRUCTURE_TOP, STRUCTURE_BOTTOM):
        for cat_def in section:
            for ch_def in cat_def["channels"]:
                if ch_def.get("type") != "voice":
                    names.add(ch_def["name"])
    for mode in _all_modes():
        for ch in mode.get("info_channels", []):
            if ch.get("type") != "voice":
                names.add(ch["name"])
        for ch in mode.get("player_channels", []):
            if ch.get("type") != "voice":
                names.add(ch["name"])
    return names


# ── build_server ──────────────────────────────────────────────────────────────

async def build_server(guild: discord.Guild) -> list[str]:
    lines: list[str] = []

    # 1. Roles
    lines.append("**Tworzenie / weryfikacja ról...**")
    r: dict[str, discord.Role] = {}
    for rd in ROLES:
        existing = discord.utils.get(guild.roles, name=rd["name"])
        if existing:
            r[rd["name"]] = existing
            lines.append(f"  ↩ {rd['name']} (już istnieje)")
            continue
        try:
            role = await guild.create_role(
                name=rd["name"],
                color=discord.Color(rd["color"]),
                hoist=rd.get("hoist", False),
                reason="ZiutekBot /setup",
            )
            r[role.name] = role
            lines.append(f"  ✅ {role.name}")
        except Exception as e:
            lines.append(f"  ❌ {rd['name']}: {e}")

    roles = {
        "everyone": guild.default_role,
        "admin":    r.get("👑 Admin")         or discord.utils.get(guild.roles, name="👑 Admin"),
        "mod":      r.get("🛡️ Mod")           or discord.utils.get(guild.roles, name="🛡️ Mod"),
        "verified": r.get("✔ Zweryfikowany") or discord.utils.get(guild.roles, name="✔ Zweryfikowany"),
        "linked":   r.get("🔗 Połączony")    or discord.utils.get(guild.roles, name="🔗 Połączony"),
    }

    # 2. Lock @everyone
    lines.append("\n**Blokowanie @everyone...**")
    try:
        await guild.default_role.edit(permissions=discord.Permissions.none(), reason="ZiutekBot /setup")
        lines.append("  ✅ @everyone = brak uprawnień")
    except Exception as e:
        lines.append(f"  ⚠ @everyone: {e}")

    # 3. Base permissions for verified + linked
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
                lines.append(f"  ✅ {role.name} = podstawowe uprawnienia")
            except Exception as e:
                lines.append(f"  ⚠ {role.name}: {e}")

    # 4. TOP static structure
    lines.append("\n**Sekcja górna...**")
    for cat_def in STRUCTURE_TOP:
        await _process_category(guild, cat_def, roles, lines)

    # 5. Mode stats channels (added to 📊 STATYSTYKI)
    lines.append("\n**Kanały statystyk trybów...**")
    for mode in _all_modes():
        await _add_mode_stats_channel(guild, mode, roles, lines)

    # 6. Game mode categories
    lines.append("\n**Struktury trybów gry...**")
    for mode in _all_modes():
        await create_mode_structure(guild, mode, roles, lines)

    # 7. BOTTOM static structure
    lines.append("\n**Sekcja dolna...**")
    for cat_def in STRUCTURE_BOTTOM:
        await _process_category(guild, cat_def, roles, lines)

    lines.append("\n✅ **Setup zakończony!**")
    lines.append("\n**Następne kroki:**")
    lines.append("1. `/cleanup` — usuń stare kanały")
    lines.append("2. `/verify-panel` w #✅・weryfikacja")
    lines.append("3. `/beta-panel` w #🔑・dolacz-do-bety")
    lines.append("4. `/link-panel` w #🔗・polacz-konto")
    lines.append("5. `/bug-panel` w #🐛・bugi")
    lines.append("6. `/suggestion-panel` w #💡・sugestie")
    lines.append("7. `/ticket-panel` w #🎫・ticket")
    lines.append("8. `/info-setup` — embedy informacyjne")
    return lines


# ── Cleanup confirm view ──────────────────────────────────────────────────────

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

    @app_commands.command(
        name="setup",
        description="[ADMIN] Synchronizuj strukturę kanałów i ról serwera",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        result = await build_server(interaction.guild)
        text   = "\n".join(result)
        for chunk in [text[i:i+1900] for i in range(0, len(text), 1900)]:
            await interaction.followup.send(f"```\n{chunk}\n```", ephemeral=True)

    @app_commands.command(
        name="cleanup",
        description="[ADMIN] Usuń kanały tekstowe spoza aktualnej struktury",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def cleanup(self, interaction: discord.Interaction):
        expected = _expected_channel_names()
        extras   = [ch for ch in interaction.guild.text_channels if ch.name not in expected]
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

    @app_commands.command(
        name="sync-permissions",
        description="[ADMIN] Napraw uprawnienia na wszystkich kanałach",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def sync_permissions(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        fixed = errors = 0
        for channel in interaction.guild.text_channels:
            new_ow  = {}
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

    @app_commands.command(
        name="dodaj-tryb",
        description="[ADMIN] Dodaj nowy tryb gry — tworzy kategorię INFO, GRACZE i rolę",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        tryb="Nazwa trybu (np. Skyblock)",
        emoji="Emoji trybu (np. 🏝)",
        opis="Krótki opis do kanału info",
        kolor="Kolor roli hex bez # (np. 7289DA)",
        info_only="Tylko kanały informacyjne — bez kategorii graczy",
    )
    async def dodaj_tryb(
        self,
        interaction: discord.Interaction,
        tryb: str,
        emoji: str,
        opis: str,
        kolor: str = "7289DA",
        info_only: bool = False,
    ):
        await interaction.response.defer(ephemeral=True)
        lines: list[str] = []

        try:
            color_int = int(kolor.lstrip("#"), 16)
        except ValueError:
            color_int = 0x7289DA

        slug      = tryb.lower().replace(" ", "-")
        label     = tryb.upper()
        role_name = None if info_only else f"{emoji} {tryb}"

        extras = _load_extra_modes()
        all_slugs = {m["slug"] for m in GAME_MODES} | {m["slug"] for m in extras}
        if slug in all_slugs:
            await interaction.followup.send(f"❌ Tryb `{slug}` już istnieje.", ephemeral=True)
            return

        guild = interaction.guild
        roles = _resolve_roles(guild)

        # Create role
        mode_role: discord.Role | None = None
        if role_name:
            existing_role = discord.utils.get(guild.roles, name=role_name)
            if existing_role:
                mode_role = existing_role
                lines.append(f"  ↩ Rola {role_name} (już istnieje)")
            else:
                try:
                    mode_role = await guild.create_role(
                        name=role_name,
                        color=discord.Color(color_int),
                        hoist=True,
                        reason=f"ZiutekBot /dodaj-tryb: {tryb}",
                    )
                    lines.append(f"  ✅ Rola {role_name}")
                except Exception as e:
                    lines.append(f"  ❌ Rola {role_name}: {e}")

        mode: dict = {
            "name":      tryb,
            "slug":      slug,
            "emoji":     emoji,
            "label":     label,
            "role_name": role_name,
            "role_color": color_int,
            "info_only": info_only,
            "info_channels": [
                {"name": f"📣・{slug}-info", "topic": opis, "read_only": True},
            ],
            "player_channels": [] if info_only else [
                {"name": f"💬・{slug}-czat",     "topic": f"Czat dla graczy {tryb}."},
                {"name": f"🐛・{slug}-bugi",     "topic": "Zgłoś buga — kliknij przycisk.",    "read_only": True},
                {"name": f"💡・{slug}-sugestie", "topic": "Dodaj sugestię — kliknij przycisk.", "read_only": True},
            ],
            "stats_channel": f"{emoji} {tryb}: …",
        }

        await create_mode_structure(guild, mode, roles, lines)
        await _add_mode_stats_channel(guild, mode, roles, lines)

        extras.append(mode)
        _save_extra_modes(extras)
        log.info("Added game mode: %s (slug=%s, info_only=%s)", tryb, slug, info_only)

        lines.append(f"\n✅ Tryb **{emoji} {tryb}** dodany i zapisany!")
        if not info_only:
            lines.append(f"Rola gracza: **{role_name}**")
        lines.append("Uruchom `/setup` aby zsynchronizować uprawnienia całego serwera.")

        text = "\n".join(lines)
        for chunk in [text[i:i+1900] for i in range(0, len(text), 1900)]:
            await interaction.followup.send(f"```\n{chunk}\n```", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(SetupCog(bot))
