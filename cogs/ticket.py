import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID
from branding import BLOOD, THUMBNAIL_URL, footer


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔒 Zamknij ticket",
        style=discord.ButtonStyle.danger,
        custom_id="ticket:close",
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        thread = interaction.channel
        if not isinstance(thread, discord.Thread):
            await interaction.response.send_message(
                "❌ Tej komendy można użyć tylko wewnątrz wątku ticketu.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="🔒  Ticket zamknięty",
            description=(
                f"Ticket zamknięty przez {interaction.user.mention}.\n"
                "Wątek zostanie zarchiwizowany."
            ),
            color=BLOOD,
        )
        embed.set_footer(text=footer("System Ticketów"))
        await interaction.response.send_message(embed=embed)
        await thread.edit(
            archived=True,
            locked=True,
            reason=f"Zamknięty przez {interaction.user}",
        )


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🎫  Utwórz ticket",
        style=discord.ButtonStyle.primary,
        custom_id="ticket:create",
    )
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild  = interaction.guild
        user   = interaction.user
        channel = interaction.channel

        # Sprawdź czy gracz ma już otwarty ticket w tym kanale
        for thread in channel.threads:
            if (
                not thread.archived
                and thread.name == f"🎫 {user.display_name}"
            ):
                await interaction.response.send_message(
                    f"❌ Masz już otwarty ticket: {thread.mention}",
                    ephemeral=True,
                )
                return

        # Utwórz prywatny wątek (fallback: publiczny jeśli brak uprawnień)
        try:
            thread = await channel.create_thread(
                name=f"🎫 {user.display_name}",
                type=discord.ChannelType.private_thread,
                reason=f"Ticket od {user}",
            )
        except discord.HTTPException:
            thread = await channel.create_thread(
                name=f"🎫 {user.display_name}",
                auto_archive_duration=10080,
                reason=f"Ticket od {user}",
            )

        await thread.add_user(user)

        mod_role   = discord.utils.get(guild.roles, name="🛠️ Moderator")
        admin_role = discord.utils.get(guild.roles, name="⚔️ Head Admin")
        staff_ping = " ".join(r.mention for r in [mod_role, admin_role] if r)

        embed = discord.Embed(
            title="🎫  Ticket otwarty",
            description=(
                f"Cześć {user.mention}! 👋\n\n"
                "Opisz swój problem lub pytanie poniżej,\n"
                "a staff odpowie jak najszybciej.\n\n"
                "**Wskazówki:**\n"
                "• Opisz dokładnie co się stało\n"
                "• Dodaj screenshoty jeśli potrzeba\n"
                "• Podaj nick MC jeśli nie masz połączonego konta"
            ),
            color=BLOOD,
        )
        embed.set_footer(text=footer("Support"))

        await thread.send(
            content=staff_ping or None,
            embed=embed,
            view=TicketCloseView(),
        )

        await interaction.response.send_message(
            f"✅ Ticket utworzony: {thread.mention}",
            ephemeral=True,
        )


class TicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="ticket-panel",
        description="[ADMIN] Wyślij panel tworzenia ticketów",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def ticket_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫  Pomoc i Wsparcie",
            description=(
                "Potrzebujesz pomocy lub chcesz skontaktować się ze staffem?\n\n"
                "Kliknij **Utwórz ticket** — zostanie otwarty prywatny wątek,\n"
                "w którym staff Ci pomoże.\n\n"
                "**Kiedy tworzyć ticket:**\n"
                "• 🐛 Znalazłeś poważny błąd\n"
                "• ⚠️  Chcesz zgłosić gracza za cheating\n"
                "• 🔗  Problem z kontem lub połączeniem DC-MC\n"
                "• ❓  Pytanie które wymaga kontaktu ze staffem\n\n"
                "*Zwykłe pytania zadawaj na **#💬-ogolny**.*"
            ),
            color=BLOOD,
        )
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer("Support"))
        await interaction.response.send_message(embed=embed, view=TicketView())


async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))
