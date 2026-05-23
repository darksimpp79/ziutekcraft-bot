import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID
from branding import BLOOD, GREEN, GOLD, THUMBNAIL_URL, footer


# ── Modal: formularz zgłoszenia ───────────────────────────────────────────────

class BugModal(discord.ui.Modal, title="🐛 Zgłoszenie Buga"):
    tytul = discord.ui.TextInput(
        label="Tytuł / Skrócony opis",
        placeholder="np. Żetony nie naliczają się po killstreaku",
        min_length=5,
        max_length=100,
    )
    opis = discord.ui.TextInput(
        label="Co się stało?",
        style=discord.TextStyle.paragraph,
        placeholder="Dokładny opis błędu — co zobaczyłeś, czego się spodziewałeś...",
        min_length=10,
        max_length=500,
    )
    kroki = discord.ui.TextInput(
        label="Kroki do odtworzenia",
        style=discord.TextStyle.paragraph,
        placeholder="1. Wejdź na arenę\n2. Zrób kill przy killstreaku 5\n3. Sprawdź /portfel",
        min_length=5,
        max_length=400,
    )
    nick = discord.ui.TextInput(
        label="Nick Minecraft (opcjonalnie)",
        placeholder="Twój nick MC",
        required=False,
        max_length=16,
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.channel
        user    = interaction.user

        tytul = self.tytul.value.strip()
        opis  = self.opis.value.strip()
        kroki = self.kroki.value.strip()
        nick  = self.nick.value.strip() if self.nick.value else None

        # Utwórz wątek z numerem (liczymy istniejące wątki żeby zrobić #ID)
        existing = [t for t in channel.threads if not t.archived]
        bug_id   = len(existing) + 1

        try:
            thread = await channel.create_thread(
                name=f"[BUG #{bug_id:03d}] {tytul[:60]}",
                type=discord.ChannelType.private_thread,
                reason=f"Bug od {user}",
            )
        except discord.HTTPException:
            thread = await channel.create_thread(
                name=f"[BUG #{bug_id:03d}] {tytul[:60]}",
                auto_archive_duration=10080,
                reason=f"Bug od {user}",
            )

        await thread.add_user(user)

        embed = discord.Embed(
            title=f"🐛  {tytul}",
            color=BLOOD,
        )
        embed.add_field(name="📋  Co się stało?",            value=opis,  inline=False)
        embed.add_field(name="🔁  Kroki do odtworzenia",     value=kroki, inline=False)
        embed.add_field(name="👤  Zgłaszający",
                        value=f"{user.mention}" + (f"  •  MC: `{nick}`" if nick else ""),
                        inline=False)
        embed.set_footer(text=footer(f"Bug #{bug_id:03d}"))

        mod_role   = discord.utils.get(interaction.guild.roles, name="🛡️ Mod")
        admin_role = discord.utils.get(interaction.guild.roles, name="👑 Admin")
        staff_ping = " ".join(r.mention for r in [mod_role, admin_role] if r)

        await thread.send(
            content=staff_ping or None,
            embed=embed,
            view=BugFixView(tytul, user.display_name, nick),
        )

        await interaction.response.send_message(
            f"✅ Bug zgłoszony: {thread.mention}\nDziękujemy — staff sprawdzi go jak najszybciej!",
            ephemeral=True,
        )


# ── Przycisk: Naprawiono (dla staffu wewnątrz wątku) ─────────────────────────

class BugFixView(discord.ui.View):
    def __init__(self, tytul: str = "", reporter: str = "", nick: str | None = None):
        super().__init__(timeout=None)
        self.tytul    = tytul
        self.reporter = reporter
        self.nick     = nick

    # Persistent view — custom_id musi być stały; dane przekazujemy przez embed
    @discord.ui.button(
        label="✅  Naprawiono",
        style=discord.ButtonStyle.success,
        custom_id="bug:fixed",
    )
    async def mark_fixed(self, interaction: discord.Interaction, button: discord.ui.Button):
        thread = interaction.channel
        guild  = interaction.guild

        if not isinstance(thread, discord.Thread):
            await interaction.response.send_message("❌ Tej opcji można użyć tylko wewnątrz wątku.", ephemeral=True)
            return

        # Pobierz tytuł z nazwy wątku jeśli instancja nie ma danych
        tytul = self.tytul or thread.name

        # Wyślij do #✅-naprawione
        fixed_ch = discord.utils.get(guild.text_channels, name="✅-naprawione")
        if fixed_ch:
            embed = discord.Embed(
                title="✅  Bug Naprawiony",
                description=f"**{tytul}**",
                color=GREEN,
            )
            embed.add_field(
                name="Wątek",
                value=thread.mention,
                inline=True,
            )
            embed.add_field(
                name="Naprawił",
                value=interaction.user.mention,
                inline=True,
            )
            embed.set_footer(text=footer("Bug Tracker"))
            await fixed_ch.send(embed=embed)

        # Zakończ wątek
        await interaction.response.send_message(
            f"✅ Oznaczono jako naprawione przez {interaction.user.mention}. Wątek zostanie zamknięty."
        )
        await thread.edit(
            archived=True,
            locked=True,
            reason=f"Naprawione przez {interaction.user}",
        )

    @discord.ui.button(
        label="❌  Nie odtworzono",
        style=discord.ButtonStyle.secondary,
        custom_id="bug:cant_reproduce",
    )
    async def cant_reproduce(self, interaction: discord.Interaction, button: discord.ui.Button):
        thread = interaction.channel
        if not isinstance(thread, discord.Thread):
            await interaction.response.send_message("❌ Tej opcji można użyć tylko wewnątrz wątku.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"⚠️ Oznaczono jako **nie można odtworzyć** przez {interaction.user.mention}.\n"
            "Jeśli bug nadal występuje, utwórz nowe zgłoszenie z dokładniejszymi krokami."
        )
        await thread.edit(
            archived=True,
            locked=True,
            reason=f"Nie odtworzono — {interaction.user}",
        )


# ── Persistent panel view ─────────────────────────────────────────────────────

class BugPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🐛  Zgłoś Buga",
        style=discord.ButtonStyle.danger,
        custom_id="bug:report",
    )
    async def report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BugModal())


# ── Cog ───────────────────────────────────────────────────────────────────────

class BugsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="bug-panel",
        description="[ADMIN] Wyślij panel zgłaszania bugów",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def bug_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🐛  Zgłaszanie Bugów",
            description=(
                "Znalazłeś błąd? Pomóż nam go naprawić!\n\n"
                "Kliknij **Zgłoś Buga** i wypełnij formularz:\n"
                "• Tytuł błędu\n"
                "• Opis co się stało\n"
                "• Kroki do odtworzenia\n"
                "• Nick MC (opcjonalnie)\n\n"
                "Zostanie utworzony prywatny wątek, w którym staff go sprawdzi.\n\n"
                "**Nie zgłaszaj tutaj:**\n"
                "• Propozycji — użyj **#💡-sugestie**\n"
                "• Pytań — użyj **#💬-beta-czat**"
            ),
            color=BLOOD,
        )
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer("Bug Tracker v1"))
        await interaction.response.send_message(embed=embed, view=BugPanelView())


async def setup(bot: commands.Bot):
    await bot.add_cog(BugsCog(bot))
