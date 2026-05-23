import re
import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
from aiohttp import web
from config import GUILD_ID, RCON_HOST, RCON_PORT, RCON_PASSWORD, LINK_BOT_PORT
from branding import GREEN, RED, PURPLE, footer
import link_store

# ── Kill rank thresholds (sorted descending) ─────────────────────────────────
KILL_RANKS = [
    (10000, "⚜ Generał"),
    (5000,  "🦅 Pułkownik"),
    (2500,  "🎖 Major"),
    (1000,  "🗡 Kapitan"),
    (500,   "🔱 Porucznik"),
    (150,   "⚡ Sierżant"),
    (50,    "🔰 Kapral"),
    (0,     "🪖 Rekrut"),
]

ALL_KILL_RANK_NAMES = {name for _, name in KILL_RANKS}

# ── LuckPerms group → Discord role ───────────────────────────────────────────
LP_ROLE_MAP = {
    "helper":       "🔧 Helper",
    "premium-plus": "🌟 Premium+",
    "premium":      "⭐ Premium",
}
ALL_LP_ROLE_NAMES = set(LP_ROLE_MAP.values())


def get_kill_rank(kills: int) -> str:
    for threshold, name in KILL_RANKS:
        if kills >= threshold:
            return name
    return "🪖 Rekrut"


def _strip_color(text: str) -> str:
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    text = re.sub(r'§[0-9a-fk-orA-FK-OR]', '', text)
    return text


def _get_lp_group(nick: str) -> str | None:
    if not RCON_PASSWORD:
        print("[Ranks] RCON_PASSWORD not set — LP rank sync disabled. Set it in .env to enable.")
        return None
    try:
        from mcrcon import MCRcon
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as r:
            result = _strip_color(r.command(f"lp user {nick} info"))
        match = re.search(r'[Pp]rimary\s+[Gg]roup[:\s]+([a-zA-Z0-9_-]+)', result)
        if match:
            return match.group(1).lower()
    except Exception as e:
        print(f"[Ranks] RCON error for {nick}: {e}")
    return None


async def assign_kill_rank(member: discord.Member, kills: int) -> bool:
    target = get_kill_rank(kills)
    to_remove = [r for r in member.roles if r.name in ALL_KILL_RANK_NAMES and r.name != target]
    try:
        if to_remove:
            await member.remove_roles(*to_remove, reason="Kill rank sync")
        if not any(r.name == target for r in member.roles):
            role = discord.utils.get(member.guild.roles, name=target)
            if role:
                await member.add_roles(role, reason=f"Kill rank: {kills} kills")
    except discord.Forbidden:
        return False
    return True


async def assign_lp_rank(member: discord.Member, lp_group: str | None):
    target_name = LP_ROLE_MAP.get(lp_group or "")
    to_remove = [r for r in member.roles
                 if r.name in ALL_LP_ROLE_NAMES and r.name != target_name]
    try:
        if to_remove:
            await member.remove_roles(*to_remove, reason="LP rank sync")
        if target_name and not any(r.name == target_name for r in member.roles):
            role = discord.utils.get(member.guild.roles, name=target_name)
            if role:
                await member.add_roles(role, reason=f"LP sync: {lp_group}")
    except discord.Forbidden:
        pass


class RanksCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._runner: web.AppRunner | None = None
        self.lp_sync_task.start()

    def cog_unload(self):
        self.lp_sync_task.cancel()
        if self._runner:
            asyncio.create_task(self._runner.cleanup())

    async def cog_load(self):
        app = web.Application()
        app.router.add_get("/api/killrank", self._handle_killrank)
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, "0.0.0.0", LINK_BOT_PORT + 1)
        await site.start()
        print(f"[Ranks] Kill rank webhook on port {LINK_BOT_PORT + 1}")

    # ── Webhook: MC plugin → bot on kill milestone ────────────────────────────

    async def _handle_killrank(self, request: web.Request) -> web.Response:
        uuid     = request.rel_url.query.get("uuid", "")
        kills_s  = request.rel_url.query.get("kills", "")
        if not uuid or not kills_s:
            return web.json_response({"ok": False, "error": "missing params"}, status=400)
        try:
            kills = int(kills_s)
        except ValueError:
            return web.json_response({"ok": False, "error": "invalid kills"}, status=400)

        discord_id = link_store.get_discord_id_by_uuid(uuid)
        if discord_id is None:
            return web.json_response({"ok": False, "error": "not linked"}, status=404)

        asyncio.create_task(self._sync_kill_rank_by_id(discord_id, kills))
        return web.json_response({"ok": True})

    async def _sync_kill_rank_by_id(self, discord_id: int, kills: int):
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return
        member = guild.get_member(discord_id)
        if not member:
            try:
                member = await guild.fetch_member(discord_id)
            except discord.NotFound:
                return
        await assign_kill_rank(member, kills)

    # ── Periodic LP sync ──────────────────────────────────────────────────────

    @tasks.loop(minutes=5)
    async def lp_sync_task(self):
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return
        for discord_id_str, data in link_store.get_all_links().items():
            nick = data.get("mc_nick", "")
            if not nick:
                continue
            member = guild.get_member(int(discord_id_str))
            if not member:
                continue
            lp_group = await asyncio.get_event_loop().run_in_executor(
                None, _get_lp_group, nick
            )
            await assign_lp_rank(member, lp_group)

    @lp_sync_task.before_loop
    async def before_lp_sync(self):
        await self.bot.wait_until_ready()

    # ── /sync-rangi ───────────────────────────────────────────────────────────

    @app_commands.command(
        name="sync-rangi",
        description="[ADMIN] Ręcznie zsynchronizuj rangi dla gracza",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(uzytkownik="Gracz do zsynchronizowania")
    async def sync_rangi(self, interaction: discord.Interaction, uzytkownik: discord.Member):
        await interaction.response.defer(ephemeral=True)

        data = link_store.get_link_by_discord(uzytkownik.id)
        if not data:
            await interaction.followup.send(
                "❌ Ten użytkownik nie ma połączonego konta MC.", ephemeral=True
            )
            return

        nick = data["mc_nick"]
        lp_group = await asyncio.get_event_loop().run_in_executor(None, _get_lp_group, nick)
        await assign_lp_rank(uzytkownik, lp_group)

        embed = discord.Embed(
            title="🔄 Sync rang",
            color=GREEN,
        )
        embed.add_field(name="Gracz",    value=uzytkownik.mention,       inline=True)
        embed.add_field(name="Nick MC",  value=f"`{nick}`",              inline=True)
        embed.add_field(name="LP Grupa", value=f"`{lp_group or 'brak'}`", inline=True)
        embed.set_footer(text=footer())
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RanksCog(bot))
