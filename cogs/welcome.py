import discord
from discord.ext import commands
from config import GUILD_ID
from branding import GREEN, PURPLE, SERVER_NAME, TAGLINE_1, TAGLINE_2, BANNER_URL, THUMBNAIL_URL, footer


class WelcomeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id != GUILD_ID:
            return

        # ── DM powitalny ──────────────────────────────────────────────────────
        embed = discord.Embed(
            title=f"⚔  Witaj na {SERVER_NAME}, {member.display_name}!",
            description=(
                f"Cieszę się, że tu jesteś!\n\n"
                f"**Żeby uzyskać dostęp do serwera:**\n"
                f”Wejdź na kanał **#✅・weryfikacja**, kliknij przycisk\n”
                f'i rozwiąż działanie — dostaniesz dostęp do serwera.\n\n'
                f”**Chcesz grać w becie?**\n”
                f”Po weryfikacji idź do **#🔑・dolacz-do-bety**.\n”
                f"Wpisujesz nick MC → automatyczny whitelist!\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"*{TAGLINE_2}*"
            ),
            color=PURPLE,
        )
        if BANNER_URL:
            embed.set_image(url=BANNER_URL)
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=footer())

        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass  # DM zablokowane

        # ── Powiadomienie w #👋・powitalnia (kasuje się po 30s) ─────────────
        welcome_chan = discord.utils.get(member.guild.text_channels, name="👋・powitalnia")
        if welcome_chan:
            try:
                await welcome_chan.send(
                    f"👋 {member.mention} dołączył do serwera! Witamy!",
                    delete_after=30,
                )
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.guild.id != GUILD_ID:
            return

        staff_chan = discord.utils.get(member.guild.text_channels, name="📊・staff-czat")
        if staff_chan:
            embed = discord.Embed(
                description=f"👋 **{member}** (`{member.id}`) opuścił serwer.",
                color=0x555555,
            )
            embed.set_footer(text=footer())
            try:
                await staff_chan.send(embed=embed)
            except discord.Forbidden:
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeCog(bot))
