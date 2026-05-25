import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID
from branding import PURPLE, GOLD, GREEN, RED, THUMBNAIL_URL, footer

STATUS_COLORS = {
    "⏳  Oczekuje":    0x555555,
    "🤔  Pod Rozwagą": 0xFFAA00,
    "✅  Przyjęto":    0x00CC44,
    "❌  Odrzucono":   0xCC2200,
}


# ── Modal: formularz sugestii ─────────────────────────────────────────────────

class SuggestionModal(discord.ui.Modal, title="💡 Dodaj Sugestię"):
    tytul = discord.ui.TextInput(
        label="Tytuł sugestii",
        placeholder="np. Dodaj tryb 2v2 na arenie",
        min_length=5,
        max_length=100,
    )
    opis = discord.ui.TextInput(
        label="Opis — jak to miałoby działać?",
        style=discord.TextStyle.paragraph,
        placeholder="Opisz pomysł dokładnie. Im więcej szczegółów tym lepiej...",
        min_length=20,
        max_length=600,
    )
    kategoria = discord.ui.TextInput(
        label="Kategoria (opcjonalnie)",
        placeholder="np. Klasy / Ekonomia / Klany / Discord / Inne",
        required=False,
        max_length=30,
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.channel
        user    = interaction.user

        tytul     = self.tytul.value.strip()
        opis      = self.opis.value.strip()
        kategoria = self.kategoria.value.strip() if self.kategoria.value else "Inne"

        embed = discord.Embed(
            title=f"💡  {tytul}",
            color=STATUS_COLORS["⏳  Oczekuje"],
        )
        embed.add_field(name="📝  Opis",      value=opis,           inline=False)
        embed.add_field(name="🏷️  Kategoria", value=f"`{kategoria}`", inline=True)
        embed.add_field(name="👤  Autor",     value=user.mention,   inline=True)
        embed.add_field(name="📊  Status",    value="⏳  Oczekuje",  inline=True)
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer("Sugestie"))

        msg = await channel.send(embed=embed, view=SuggestionStatusView())

        # Dodaj reakcje do głosowania
        try:
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")
        except discord.HTTPException:
            pass

        await interaction.response.send_message(
            "✅ Sugestia wysłana! Dziękujemy za pomysł — staff ją przejrzy.",
            ephemeral=True,
        )


# ── Przyciski staffu: zmiana statusu ─────────────────────────────────────────

class SuggestionStatusView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def _set_status(
        self,
        interaction: discord.Interaction,
        status: str,
        color: int,
    ):
        # Tylko staff może zmieniać status
        mod_role   = discord.utils.get(interaction.guild.roles, name="🔰 Moderator")
        admin_role = discord.utils.get(interaction.guild.roles, name="👑 Head Admin")
        staff_roles = {r for r in [mod_role, admin_role] if r}
        if not staff_roles.intersection(set(interaction.user.roles)):
            await interaction.response.send_message(
                "❌ Tylko staff może zmieniać status sugestii.", ephemeral=True
            )
            return

        msg = interaction.message
        if not msg or not msg.embeds:
            await interaction.response.send_message("❌ Nie znaleziono embeda.", ephemeral=True)
            return

        embed = msg.embeds[0].copy()
        embed.color = color

        # Znajdź pole "Status" i zaktualizuj
        for i, field in enumerate(embed.fields):
            if "Status" in field.name:
                embed.set_field_at(i, name=field.name, value=status, inline=field.inline)
                break

        await msg.edit(embed=embed)
        await interaction.response.send_message(
            f"✅ Status zmieniony na **{status}** przez {interaction.user.mention}.",
            ephemeral=True,
        )

    @discord.ui.button(
        label="✅ Przyjęto",
        style=discord.ButtonStyle.success,
        custom_id="suggestion:accept",
    )
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set_status(interaction, "✅  Przyjęto", STATUS_COLORS["✅  Przyjęto"])

    @discord.ui.button(
        label="🤔 Pod Rozwagą",
        style=discord.ButtonStyle.secondary,
        custom_id="suggestion:consider",
    )
    async def consider(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set_status(interaction, "🤔  Pod Rozwagą", STATUS_COLORS["🤔  Pod Rozwagą"])

    @discord.ui.button(
        label="❌ Odrzucono",
        style=discord.ButtonStyle.danger,
        custom_id="suggestion:reject",
    )
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set_status(interaction, "❌  Odrzucono", STATUS_COLORS["❌  Odrzucono"])


# ── Panel view (persistent) ───────────────────────────────────────────────────

class SuggestionPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="💡  Dodaj Sugestię",
        style=discord.ButtonStyle.primary,
        custom_id="suggestion:open",
    )
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SuggestionModal())


# ── Cog ───────────────────────────────────────────────────────────────────────

class SuggestionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="suggestion-panel",
        description="[ADMIN] Wyślij panel dodawania sugestii",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def suggestion_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="💡  Sugestie i Pomysły",
            description=(
                "Masz pomysł na ulepszenie serwera lub rozgrywki?\n\n"
                "Kliknij **Dodaj Sugestię**, wypełnij formularz,\n"
                "a staff przejrzy Twój pomysł.\n\n"
                "**Dobre sugestie to:**\n"
                "• Konkretne — wiadomo co i jak\n"
                "• Uzasadnione — dlaczego warto to dodać\n"
                "• Realistyczne — pasują do stylu gry\n\n"
                "Po wysłaniu inni gracze mogą głosować 👍 / 👎.\n"
                "Staff zmieni status sugestii gdy ją przejrzy."
            ),
            color=PURPLE,
        )
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer("Sugestie v1"))
        await interaction.response.send_message(embed=embed, view=SuggestionPanelView())


async def setup(bot: commands.Bot):
    await bot.add_cog(SuggestionsCog(bot))
