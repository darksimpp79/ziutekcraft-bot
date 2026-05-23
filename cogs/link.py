import asyncio
import logging
from aiohttp import web
import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID, LINK_BOT_PORT, LINKED_ROLE_ID, LINK_LOG_CHAN_ID
from branding import GREEN, RED, PURPLE, THUMBNAIL_URL, footer
import link_store

log = logging.getLogger(__name__)

LINK_TOKENS = 50


# ── Modal: wpisz nick MC ──────────────────────────────────────────────────────

class LinkModal(discord.ui.Modal, title="🔗 Połącz konto Minecraft"):
    nick = discord.ui.TextInput(
        label="Nick Minecraft",
        placeholder="Wpisz swój nick w grze (3–16 znaków)...",
        min_length=3,
        max_length=16,
    )

    async def on_submit(self, interaction: discord.Interaction):
        discord_id = interaction.user.id
        mc_nick    = self.nick.value.strip()

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
                f"Nick: **`{mc_nick}`**\n\n"
                f"Wejdź na serwer Minecraft i wpisz:\n\n"
                f"```\n/linkdc {code}\n```\n"
                f"Kod ważny przez **10 minut**.\n\n"
                f"Po potwierdzeniu:\n"
                f"• **{LINK_TOKENS} znaczków** 🪙\n"
                f"• Rola **🔗 Połączony**\n"
                f"• Dostęp do `/daily`"
            ),
            color=PURPLE,
        )
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer("DC-MC Link"))
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ── Persistent view: przycisk w #🔗-polacz-konto ─────────────────────────────

class LinkView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔗  Połącz konto",
        style=discord.ButtonStyle.primary,
        custom_id="link:connect",
    )
    async def connect(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LinkModal())


class LinkCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot    = bot
        self._runner: web.AppRunner | None = None

    async def cog_load(self):
        app = web.Application()
        app.router.add_get("/api/link",             self._handle_link)
        app.router.add_get("/api/linked",           self._handle_linked)
        app.router.add_get("/api/claim-dc-reward",  self._handle_claim_reward)
        app.router.add_get("/api/daily/claim",      self._handle_daily_claim)
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        await web.TCPSite(self._runner, "0.0.0.0", LINK_BOT_PORT).start()
        try:
            await web.TCPSite(self._runner, "::", LINK_BOT_PORT).start()
        except Exception:
            pass
        print(f"[Link] HTTP webhook server on port {LINK_BOT_PORT} (IPv4+IPv6)")

    async def cog_unload(self):
        if self._runner:
            await self._runner.cleanup()

    # ── GET /api/linked?uuid=XXX — sprawdź czy UUID jest połączony ───────────

    async def _handle_linked(self, request: web.Request) -> web.Response:
        uuid = request.rel_url.query.get("uuid", "")
        if not uuid:
            return web.json_response({"ok": False, "error": "missing uuid"}, status=400)

        discord_id = link_store.get_discord_id_by_uuid(uuid)
        if discord_id is None:
            return web.json_response({"linked": False}, status=404)

        data = link_store.get_link_by_discord(discord_id)
        guild  = self.bot.get_guild(GUILD_ID)
        member = guild.get_member(discord_id) if guild else None
        discord_tag = str(member) if member else str(discord_id)

        return web.json_response({
            "linked":        True,
            "discord_id":    discord_id,
            "discord_tag":   discord_tag,
            "mc_nick":       data.get("mc_nick", ""),
            "reward_given":  data.get("reward_given", False),
        })

    # ── GET /api/daily/claim?uuid=XXX — odbiór dziennej nagrody w grze ──────────

    async def _handle_daily_claim(self, request: web.Request) -> web.Response:
        uuid = request.rel_url.query.get("uuid", "")
        if not uuid:
            return web.json_response({"ok": False, "error": "missing uuid"}, status=400)
        discord_id = link_store.get_discord_id_by_uuid(uuid)
        if discord_id is None:
            return web.json_response({"ok": False, "error": "not linked"}, status=404)
        from cogs.daily_dc import daily_claim
        result = daily_claim(discord_id)
        if result["ok"]:
            return web.json_response(result)
        return web.json_response(result, status=429)

    # ── GET /api/claim-dc-reward?uuid=XXX — atomowo oznacz nagrodę jako odebrana ──

    async def _handle_claim_reward(self, request: web.Request) -> web.Response:
        uuid = request.rel_url.query.get("uuid", "")
        if not uuid:
            return web.json_response({"ok": False, "error": "missing uuid"}, status=400)
        result = link_store.try_claim_reward(uuid)
        if result == "ok":
            return web.json_response({"ok": True})
        if result == "already_claimed":
            return web.json_response({"ok": False, "error": "already claimed"}, status=409)
        return web.json_response({"ok": False, "error": "not linked"}, status=404)

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
        log.info("Account linked: discord=%s nick=%s uuid=%s", discord_id, nick, uuid)

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

        # Natychmiastowy sync LP rangi po połączeniu (bez czekania na 5-min pętlę)
        try:
            from cogs.ranks import assign_lp_rank, _get_lp_group
            lp_group = _get_lp_group(mc_nick)
            await assign_lp_rank(member, lp_group)
        except Exception as e:
            print(f"[Link] LP rank sync error for {mc_nick}: {e}")

    # ── /link-panel — embed z przyciskiem do #🔗-polacz-konto ────────────────

    @app_commands.command(
        name="link-panel",
        description="[ADMIN] Wyślij panel połączenia konta DC-MC (embed + przycisk)",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def link_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🔗  Połącz konto Discord z Minecraft",
            description=(
                "Kliknij przycisk poniżej i wpisz swój **nick Minecraft**.\n"
                "Następnie wejdź na serwer MC i użyj komendy, którą otrzymasz.\n\n"
                "**Nagroda za pierwsze połączenie:**\n"
                f"• `+{LINK_TOKENS}` znaczków 🪙\n"
                "• Rola **🔗 Połączony**\n"
                "• Dostęp do `/daily` — codzienne nagrody\n\n"
                "*Połączenie możesz wykonać tylko raz. Jeden nick MC = jedno konto Discord.*"
            ),
            color=PURPLE,
        )
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer("DC-MC Link"))
        await interaction.response.send_message(embed=embed, view=LinkView())

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
        log.info("Account unlinked: discord=%s nick=%s (by %s)", target.id, data["mc_nick"], interaction.user)

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


    # ── /rozlacz-force ────────────────────────────────────────────────────────

    @app_commands.command(
        name="rozlacz-force",
        description="[ADMIN] Usuń całkowicie wpis linkowania (DC + reward_given) — do testów",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        uzytkownik="Użytkownik Discord do rozłączenia",
        mc_nick="Albo nick MC (jeśli użytkownik niedostępny)",
    )
    async def rozlacz_force(
        self,
        interaction: discord.Interaction,
        uzytkownik: discord.Member | None = None,
        mc_nick: str | None = None,
    ):
        if not uzytkownik and not mc_nick:
            await interaction.response.send_message(
                "Podaj `uzytkownik` lub `mc_nick`.", ephemeral=True
            )
            return

        # Resolve the entry
        if uzytkownik:
            data = link_store.get_link_by_discord(uzytkownik.id)
            discord_id = uzytkownik.id
        else:
            all_links = link_store.get_all_links()
            discord_id = next(
                (int(did) for did, d in all_links.items()
                 if d.get("mc_nick", "").lower() == mc_nick.lower()),
                None,
            )
            data = link_store.get_link_by_discord(discord_id) if discord_id else None

        if not data:
            await interaction.response.send_message(
                "❌ Nie znaleziono wpisu linkowania.", ephemeral=True
            )
            return

        nick        = data["mc_nick"]
        reward_was  = data.get("reward_given", False)
        link_store.delete_link(discord_id)
        log.info("Force-unlinked: discord=%s nick=%s reward_was=%s (by %s)",
                 discord_id, nick, reward_was, interaction.user)

        # Remove role if member is available
        member = interaction.guild.get_member(discord_id) if interaction.guild else None
        if member:
            linked_role = discord.utils.get(interaction.guild.roles, name="🔗 Połączony")
            if linked_role and linked_role in member.roles:
                try:
                    await member.remove_roles(linked_role, reason="rozlacz-force")
                except discord.Forbidden:
                    pass

        await interaction.response.send_message(
            f"✅ Usunięto wpis dla `{nick}` (discord: `{discord_id}`).\n"
            f"reward_given było: `{reward_was}`\n"
            f"Pamiętaj ustawić `dc_link_reward_given = 0` w SQLite na serwerze MC.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(LinkCog(bot))
