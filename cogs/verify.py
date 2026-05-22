import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID
from branding import GREEN, PURPLE, RED, SERVER_NAME, TAGLINE_1, TAGLINE_2, BANNER_URL, THUMBNAIL_URL, footer

RULES_TEXT = """\
**§1 — Kultura**
▸ Szanuj wszystkich. Zero hejtu, rasizmu i obrażania.
▸ Zakaz spamu, floodowania i niechcianej reklamy.
▸ Treści NSFW = natychmiastowy ban, bez ostrzeżenia.

**§2 — Beta Testing**
▸ Błędy zgłaszaj w <#bugs> — format: `[BŁĄD]` + opis + jak odtworzyć.
▸ Sugestie tylko w <#suggestions> — nie powtarzaj tych samych pomysłów.
▸ IP serwera jest prywatne — nie udostępniaj go poza betą.

**§3 — Discord**
▸ Pisz na odpowiednich kanałach.
▸ Nie pinguj @Admin / @Mod bez powodu — pisz na #❓-pomoc.
▸ Decyzje staffu są ostateczne.

**§4 — Kary**
▸ Ostrzeżenie → Wyciszenie → Kick → Ban.
▸ Cheating / doxxing = ban bez ostrzeżenia.
"""


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="✔  Akceptuję regulamin — daj mi dostęp",
        style=discord.ButtonStyle.success,
        custom_id="verify_accept_button",
    )
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild  = interaction.guild
        member = interaction.user

        verified_role = discord.utils.get(guild.roles, name="✔ Zweryfikowany")
        if not verified_role:
            await interaction.response.send_message(
                "❌ Rola `✔ Zweryfikowany` nie istnieje — napisz do admina.", ephemeral=True
            )
            return

        if verified_role in member.roles:
            await interaction.response.send_message(
                "ℹ️ Masz już dostęp — ciesz się serwerem! ⚔", ephemeral=True
            )
            return

        try:
            await member.add_roles(verified_role, reason="Zaakceptował regulamin")
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Bot nie może nadać roli. Upewnij się, że rola bota jest wyżej niż `✔ Zweryfikowany`.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"✅  Witaj na {SERVER_NAME}!",
            description=(
                f"Masz teraz dostęp do całego serwera.\n\n"
                f"**Chcesz grać w becie?**\n"
                f"Idź do #🔑-dolacz-do-bety i kliknij przycisk.\n\n"
                f"*{TAGLINE_2}*"
            ),
            color=GREEN,
        )
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer("Weryfikacja OK"))
        await interaction.response.send_message(embed=embed, ephemeral=True)


class VerifyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.add_view(VerifyView())

    @app_commands.command(
        name="verify-panel",
        description="[ADMIN] Wyślij panel zasad z przyciskiem weryfikacji",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def verify_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"⚔  {SERVER_NAME} — Regulamin",
            description=RULES_TEXT,
            color=PURPLE,
        )
        if BANNER_URL:
            embed.set_image(url=BANNER_URL)
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.add_field(
            name="─" * 32,
            value=(
                "Klikając przycisk potwierdzasz, że przeczytałeś\n"
                "i **akceptujesz** powyższy regulamin.\n\n"
                f"**Brak akceptacji = brak dostępu do serwera.**\n"
                f"*{TAGLINE_1}*"
            ),
            inline=False,
        )
        embed.set_footer(text=footer())
        await interaction.response.send_message(embed=embed, view=VerifyView())


async def setup(bot: commands.Bot):
    await bot.add_cog(VerifyCog(bot))
