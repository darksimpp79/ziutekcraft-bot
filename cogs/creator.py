import json
from pathlib import Path
import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID, RCON_HOST, RCON_PORT, RCON_PASSWORD
from branding import GREEN, RED, PURPLE, GOLD, SERVER_NAME, THUMBNAIL_URL, footer

DATA_DIR = Path(__file__).parent.parent / "data"
APPS_FILE = DATA_DIR / "creator_applications.json"

CREATOR_ROLE_NAME = "🎬 Creator"
CREATOR_LOG_CHAN  = "🔧-bot-komendy"  # staff sees applications here


def _read_apps() -> list:
    if APPS_FILE.exists():
        try:
            return json.loads(APPS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _write_apps(data: list):
    DATA_DIR.mkdir(exist_ok=True)
    APPS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _rcon(cmd: str) -> tuple[bool, str]:
    if not RCON_PASSWORD:
        return False, "RCON nie skonfigurowane"
    try:
        from mcrcon import MCRcon
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            resp = mcr.command(cmd)
        return True, resp.strip() or "OK"
    except Exception as e:
        return False, str(e)


# ── Application modal ─────────────────────────────────────────────────────────

class CreatorAppModal(discord.ui.Modal, title="Zostań Twórcą ZiutekCraft"):
    mc_nick = discord.ui.TextInput(
        label="Nick Minecraft", placeholder="np. Ziutek123", min_length=3, max_length=16
    )
    channel_url = discord.ui.TextInput(
        label="Link do kanału (YouTube/TikTok)", placeholder="https://youtube.com/@...", max_length=200
    )
    requested_code = discord.ui.TextInput(
        label="Żądany kod (max 12 znaków, litery+cyfry)",
        placeholder="np. ZIUTEK albo JANUSZ99",
        min_length=3, max_length=12,
    )
    about = discord.ui.TextInput(
        label="Kilka słów o sobie / swoim kanale",
        style=discord.TextStyle.paragraph,
        max_length=300, required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        code     = self.requested_code.value.strip().upper()
        nick     = self.mc_nick.value.strip()
        url      = self.channel_url.value.strip()
        about_me = self.about.value.strip()
        user     = interaction.user

        # Validate code format
        if not code.isalnum():
            await interaction.response.send_message(
                "❌ Kod może zawierać tylko litery i cyfry (np. JANUSZ99).", ephemeral=True
            )
            return

        apps = _read_apps()
        apps.append({
            "discord_id": str(user.id),
            "discord_tag": str(user),
            "mc_nick":     nick,
            "code":        code,
            "channel_url": url,
            "about":       about_me,
            "status":      "pending",
        })
        _write_apps(apps)

        # Notify staff
        guild    = interaction.guild
        log_chan = discord.utils.get(guild.text_channels, name=CREATOR_LOG_CHAN)
        if log_chan:
            embed = discord.Embed(title="🎬 Nowe zgłoszenie Creator", color=PURPLE)
            embed.add_field(name="Discord",  value=f"{user.mention} (`{user}`)",  inline=True)
            embed.add_field(name="Nick MC",  value=f"`{nick}`",                   inline=True)
            embed.add_field(name="Kod",      value=f"`{code}`",                   inline=True)
            embed.add_field(name="Kanał",    value=url,                           inline=False)
            if about_me:
                embed.add_field(name="O sobie", value=about_me, inline=False)
            embed.add_field(
                name="Zatwierdzenie",
                value=f"`/admin creator zatwierdz {code} {nick} {user.id}`\n"
                      f"Lub `/creator-zatwierdz {code} {nick}`",
                inline=False,
            )
            embed.set_footer(text=footer("Creator Applications"))
            await log_chan.send(embed=embed)

        await interaction.response.send_message(
            "✅ Zgłoszenie wysłane! Staff rozpatrzy je wkrótce i odezwie się do Ciebie.",
            ephemeral=True,
        )


# ── Cog ───────────────────────────────────────────────────────────────────────

class CreatorCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="creator-zgloszenie",
        description="Złóż zgłoszenie do Programu Twórców ZiutekCraft",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def creator_zgloszenie(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CreatorAppModal())

    @app_commands.command(
        name="creator-zatwierdz",
        description="[ADMIN] Zatwierdź twórcę i aktywuj jego kod na serwerze MC",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def creator_zatwierdz(
        self,
        interaction: discord.Interaction,
        kod: str,
        mc_nick: str,
        discord_id: str = "",
    ):
        await interaction.response.defer(ephemeral=True)
        kod = kod.upper()

        ok, msg = _rcon(f"admin creator zatwierdz {kod} {mc_nick} {discord_id}")

        if ok:
            guild  = interaction.guild
            # Give creator role
            member = None
            if discord_id:
                try:
                    member = await guild.fetch_member(int(discord_id))
                except Exception:
                    pass
            if member:
                role = discord.utils.get(guild.roles, name=CREATOR_ROLE_NAME)
                if role:
                    try:
                        await member.add_roles(role, reason="Creator program approval")
                    except discord.Forbidden:
                        pass
                # DM the creator
                dm = discord.Embed(
                    title=f"🎬  Zostałeś Twórcą {SERVER_NAME}!",
                    description=(
                        f"Twój kod **`{kod}`** jest aktywny!\n\n"
                        f"**Jak to działa:**\n"
                        f"Gracze wpisują `/creator {kod}` na serwerze MC.\n"
                        f"Za każdą otwartą przez nich skrzynkę dostajesz **10% wartości** jako znaczki.\n\n"
                        f"Sprawdź swoje statsy i odbierz prowizję: `/mojkod`\n"
                        f"Wypłata: `/mojkod odbierz`\n\n"
                        f"Dziękujemy za promowanie {SERVER_NAME}! ⚔"
                    ),
                    color=PURPLE,
                )
                if THUMBNAIL_URL:
                    dm.set_thumbnail(url=THUMBNAIL_URL)
                dm.set_footer(text=footer("Creator Program"))
                try:
                    await member.send(embed=dm)
                except discord.Forbidden:
                    pass

            # Update app status
            apps = _read_apps()
            for app in apps:
                if app["code"] == kod and app["status"] == "pending":
                    app["status"] = "approved"
            _write_apps(apps)

            embed = discord.Embed(
                description=f"✅ Twórca `{mc_nick}` z kodem `{kod}` zatwierdzony. RCON: `{msg}`",
                color=GREEN,
            )
        else:
            embed = discord.Embed(
                description=f"⚠️ RCON error: `{msg}`\nDodaj kod ręcznie w `creator_codes.yml`.",
                color=GOLD,
            )

        embed.set_footer(text=footer())
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="creator-lista",
        description="[ADMIN] Pokaż listę aktywnych twórców i ich statsy",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def creator_lista(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        ok, msg = _rcon("admin creator lista")
        embed = discord.Embed(
            title="🎬 Lista Twórców",
            description=f"```\n{msg}\n```" if ok else f"⚠️ RCON: `{msg}`",
            color=PURPLE if ok else GOLD,
        )
        embed.set_footer(text=footer())
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="creator-oczekujace",
        description="[ADMIN] Pokaż niezatwierdzone zgłoszenia twórców",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def creator_oczekujace(self, interaction: discord.Interaction):
        apps = [a for a in _read_apps() if a.get("status") == "pending"]
        if not apps:
            await interaction.response.send_message("Brak oczekujących zgłoszeń.", ephemeral=True)
            return

        embed = discord.Embed(title=f"🎬 Zgłoszenia ({len(apps)})", color=PURPLE)
        for app in apps[:10]:
            embed.add_field(
                name=f"`{app['code']}` — {app['mc_nick']}",
                value=f"DC: <@{app['discord_id']}>\n[Kanał]({app['channel_url']})\n"
                      f"`/creator-zatwierdz {app['code']} {app['mc_nick']} {app['discord_id']}`",
                inline=False,
            )
        embed.set_footer(text=footer("Creator Applications"))
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(CreatorCog(bot))
