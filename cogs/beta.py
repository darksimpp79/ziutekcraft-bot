import re
import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID, RCON_HOST, RCON_PORT, RCON_PASSWORD, BETA_ROLE_ID, BETA_LOG_CHAN_ID
from branding import GREEN, PURPLE, RED, GOLD, SERVER_NAME, TAGLINE_1, BANNER_URL, THUMBNAIL_URL, footer

NICK_RE = re.compile(r"^[A-Za-z0-9_]{3,16}$")


# ── RCON ─────────────────────────────────────────────────────────────────────

def rcon_whitelist_add(nick: str) -> tuple[bool, str]:
    if not RCON_PASSWORD:
        return False, "RCON nie skonfigurowane (brak hasła w .env)"
    try:
        from mcrcon import MCRcon
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            resp = mcr.command(f"whitelist add {nick}")
        return True, resp.strip() or "OK"
    except Exception as e:
        return False, str(e)


# ── Modal ─────────────────────────────────────────────────────────────────────

class NickModal(discord.ui.Modal, title="Dołącz do Bety — podaj nick"):
    nick = discord.ui.TextInput(
        label="Twój nick w Minecraft",
        placeholder="np. Ziutek123  (3–16 znaków)",
        min_length=3,
        max_length=16,
    )

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        nick_val = self.nick.value.strip()

        if not NICK_RE.match(nick_val):
            await interaction.response.send_message(
                "❌ Nieprawidłowy nick. Tylko litery, cyfry i `_`, 3–16 znaków.",
                ephemeral=True,
            )
            return

        guild  = interaction.guild
        member = interaction.user

        beta_role = (
            guild.get_role(BETA_ROLE_ID)
            if BETA_ROLE_ID
            else discord.utils.get(guild.roles, name="⚔ Beta Tester")
        )

        if beta_role and beta_role in member.roles:
            await interaction.response.send_message(
                "ℹ️ Jesteś już zarejestrowany jako Beta Tester. Do zobaczenia na arenie! ⚔",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        ok, msg = rcon_whitelist_add(nick_val)

        role_ok = False
        if beta_role:
            try:
                await member.add_roles(beta_role, reason="Beta signup")
                role_ok = True
            except discord.Forbidden:
                pass

        # ── Odpowiedź dla gracza ───────────────────────────────────────────────
        if ok:
            embed = discord.Embed(
                title="✅  Jesteś w becie!",
                color=GREEN,
            )
            embed.add_field(
                name="Nick MC",
                value=f"`{nick_val}`",
                inline=True,
            )
            embed.add_field(
                name="Status whitelisty",
                value="✅ Dodany",
                inline=True,
            )
            if role_ok and beta_role:
                embed.add_field(
                    name="Rola",
                    value=f"✅ {beta_role.mention}",
                    inline=True,
                )
            embed.add_field(
                name="Co dalej?",
                value=(
                    "• Sprawdź IP w kanale #🟢-status-serwera\n"
                    "• Wejdź na serwer i wybierz klasę\n"
                    "• Feedback wrzucaj w #🐛-bugi i #💡-sugestie"
                ),
                inline=False,
            )
            if THUMBNAIL_URL:
                embed.set_thumbnail(url=THUMBNAIL_URL)
            embed.set_footer(text=footer("Beta Signup OK"))
        else:
            embed = discord.Embed(
                title="⚠️  Whitelist niedostępna",
                description=(
                    f"Nick `{nick_val}` zapisany — admin doda Cię ręcznie.\n"
                    f"```{msg}```"
                ),
                color=GOLD,
            )
            embed.set_footer(text=footer())

        await interaction.followup.send(embed=embed, ephemeral=True)

        # ── Log do staffu ──────────────────────────────────────────────────────
        log_chan = (
            self.bot.get_channel(BETA_LOG_CHAN_ID)
            if BETA_LOG_CHAN_ID
            else discord.utils.get(guild.text_channels, name="📥-beta-log")
        )
        if log_chan:
            status = "✅ RCON OK" if ok else f"❌ RCON FAIL: {msg}"
            log_embed = discord.Embed(
                title="📥 Nowy Beta Tester",
                color=GREEN if ok else GOLD,
            )
            log_embed.add_field(name="Discord", value=f"{member.mention} (`{member}`)", inline=True)
            log_embed.add_field(name="Nick MC",  value=f"`{nick_val}`",                 inline=True)
            log_embed.add_field(name="RCON",     value=status,                          inline=False)
            log_embed.set_footer(text=footer())
            await log_chan.send(embed=log_embed)


# ── Persistent button ─────────────────────────────────────────────────────────

class BetaSignupView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="⚔  Dołącz do Bety — wpisz nick MC",
        style=discord.ButtonStyle.danger,
        custom_id="beta_signup_button",
    )
    async def signup(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NickModal(self.bot))


# ── Cog ───────────────────────────────────────────────────────────────────────

class BetaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="beta-panel",
        description="[ADMIN] Wyślij panel rejestracji do bety",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def beta_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"⚔  {SERVER_NAME} — Beta Testing",
            color=PURPLE,
        )
        embed.add_field(
            name="Jak dołączyć?",
            value=(
                "**1.** Kliknij przycisk poniżej\n"
                "**2.** Wpisz swój nick w Minecraft\n"
                "**3.** Automatycznie trafiasz na whitelist!"
            ),
            inline=False,
        )
        embed.add_field(
            name="Co znajdziesz na serwerze?",
            value=(
                "⚔  6 unikalnych klas bojowych\n"
                "🌿 Drzewko umiejętności (3 ścieżki/klasa)\n"
                "🔫 Ulepszenia broni — 10 poziomów\n"
                "💰 Misje, rangi, prestiż, kosmetyki\n"
                "🏆 Rundy PvP 10 min — wygrywa najlepszy!"
            ),
            inline=False,
        )
        embed.add_field(
            name="─" * 32,
            value=f"*{TAGLINE_1}*",
            inline=False,
        )
        if BANNER_URL:
            embed.set_image(url=BANNER_URL)
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer("Miejsca ograniczone"))
        view = BetaSignupView(self.bot)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(
        name="whitelist-add",
        description="[ADMIN] Ręcznie dodaj nick do whitelisty MC",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def whitelist_add(self, interaction: discord.Interaction, nick: str):
        if not NICK_RE.match(nick):
            await interaction.response.send_message("❌ Nieprawidłowy nick.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        ok, msg = rcon_whitelist_add(nick)
        embed = discord.Embed(
            description=f"{'✅' if ok else '❌'} `whitelist add {nick}` → `{msg}`",
            color=GREEN if ok else RED,
        )
        embed.set_footer(text=footer())
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(BetaCog(bot))
