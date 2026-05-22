import asyncio
from aiohttp import web
import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID, LINK_BOT_PORT, LINKED_ROLE_ID, LINK_LOG_CHAN_ID
from branding import GREEN, RED, PURPLE, THUMBNAIL_URL, footer
import link_store

LINK_TOKENS = 50


class LinkCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot    = bot
        self._runner: web.AppRunner | None = None

    async def cog_load(self):
        app = web.Application()
        app.router.add_get("/api/link", self._handle_link)
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, "0.0.0.0", LINK_BOT_PORT)
        await site.start()
        print(f"[Link] HTTP webhook server on port {LINK_BOT_PORT}")

    async def cog_unload(self):
        if self._runner:
            await self._runner.cleanup()

    # ── Webhook called by MC plugin ───────────────────────────────────────────

    async def _handle_link(self, request: web.Request) -> web.Response:
        """GET /api/link?code=XXX&nick=YYY&uuid=ZZZ — called by /linkdc on MC."""
        code = request.rel_url.query.get("code", "").upper()
        nick = request.rel_url.query.get("nick", "")
        uuid = request.rel_url.query.get("uuid", "")

        if not code or not nick or not uuid:
            return web.json_response({"ok": False, "error": "missing params"}, status=400)

        discord_id = link_store.consume_code(code)
        if discord_id is None:
            return web.json_response({"ok": False, "error": "invalid or expired code"}, status=404)

        link_store.save_link(discord_id, nick, uuid)
        asyncio.create_task(self._post_link(discord_id, nick))

        return web.json_response({"ok": True, "discord_id": discord_id, "tokens": LINK_TOKENS})

    async def _post_link(self, discord_id: int, mc_nick: str):
        """Give role + DM + log after a successful link."""
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return

        member = guild.get_member(discord_id)
        if not member:
            try:
                member = await guild.fetch_member(discord_id)
            except discord.NotFound:
                return

        linked_role = (
            guild.get_role(LINKED_ROLE_ID)
            if LINKED_ROLE_ID
            else discord.utils.get(guild.roles, name="🔗 Połączony")
        )
        if linked_role:
            try:
                await member.add_roles(linked_role, reason="DC-MC link")
            except discord.Forbidden:
                pass

        embed = discord.Embed(
            title="🔗  Konto połączone!",
            description=(
                f"Twój nick MC `{mc_nick}` jest połączony z Discordem.\n\n"
                f"**Nagroda:** `+{LINK_TOKENS}` znaczków dodanych na serwer!\n\n"
                f"Możesz teraz używać `/daily` aby zbierać codzienne nagrody. 🎁"
            ),
            color=GREEN,
        )
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer("DC-MC Link"))
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

        log_chan = (
            self.bot.get_channel(LINK_LOG_CHAN_ID)
            if LINK_LOG_CHAN_ID
            else discord.utils.get(guild.text_channels, name="🔗-polacz-konto-mc")
        )
        if log_chan:
            log = discord.Embed(title="🔗 Nowe połączenie DC-MC", color=GREEN)
            log.add_field(name="Discord", value=f"{member.mention} (`{member}`)", inline=True)
            log.add_field(name="Nick MC", value=f"`{mc_nick}`",                  inline=True)
            log.set_footer(text=footer())
            await log_chan.send(embed=log)

    # ── /polacz-konto ─────────────────────────────────────────────────────────

    @app_commands.command(
        name="polacz-konto",
        description="Połącz konto Discord z Minecraft i zgarnij 50 znaczków",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def polacz_konto(self, interaction: discord.Interaction):
        discord_id = interaction.user.id

        if link_store.is_linked(discord_id):
            data = link_store.get_link_by_discord(discord_id)
            await interaction.response.send_message(
                f"ℹ️ Jesteś już połączony jako `{data['mc_nick']}`.",
                ephemeral=True,
            )
            return

        code = link_store.create_code(discord_id)
        embed = discord.Embed(
            title="🔗  Połącz konto Discord z Minecraft",
            description=(
                f"Wejdź na serwer Minecraft i wpisz:\n\n"
                f"```\n/linkdc {code}\n```\n"
                f"Kod ważny przez **10 minut**.\n\n"
                f"Po potwierdzeniu otrzymasz:\n"
                f"• **{LINK_TOKENS} znaczków** 🪙\n"
                f"• Rolę **🔗 Połączony**\n"
                f"• Dostęp do `/daily` (codzienne nagrody)"
            ),
            color=PURPLE,
        )
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer("DC-MC Link"))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── /rozlacz-konto ────────────────────────────────────────────────────────

    @app_commands.command(
        name="rozlacz-konto",
        description="[ADMIN] Rozłącz konto Discord od Minecraft",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(uzytkownik="Użytkownik którego konto rozłączyć")
    async def rozlacz_konto(self, interaction: discord.Interaction,
                            uzytkownik: discord.Member):
        target = uzytkownik
        data = link_store.get_link_by_discord(target.id)

        if not data:
            await interaction.response.send_message(
                f"ℹ️ {'Ten użytkownik nie ma' if uzytkownik else 'Nie masz'} połączonego konta MC.",
                ephemeral=True,
            )
            return

        link_store.delete_link(target.id)

        linked_role = discord.utils.get(interaction.guild.roles, name="🔗 Połączony")
        if linked_role and linked_role in target.roles:
            try:
                await target.remove_roles(linked_role, reason="Rozłączono konto DC-MC")
            except discord.Forbidden:
                pass

        await interaction.response.send_message(
            f"✅ Konto MC `{data['mc_nick']}` zostało rozłączone od "
            f"{'użytkownika ' + target.mention if uzytkownik else 'Twojego konta Discord'}.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(LinkCog(bot))
