import discord
from discord.ext import commands
from config import GUILD_ID

CREATOR_NAME    = "➕ Stwórz kanał"
OWN_CATEGORY    = "🔊 WŁASNE KANAŁY"


class VoiceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._temp: set[int] = set()   # IDs of bot-created temp channels

    # ── Cleanup orphaned temp channels on ready ───────────────────────────────

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return
        cat = discord.utils.get(guild.categories, name=OWN_CATEGORY)
        if not cat:
            return
        for ch in list(cat.voice_channels):
            if ch.name == CREATOR_NAME:
                continue
            if len(ch.members) == 0:
                try:
                    await ch.delete(reason="Bot restart — orphaned temp voice channel")
                except discord.NotFound:
                    pass
            else:
                self._temp.add(ch.id)

    # ── Main logic ────────────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if member.guild.id != GUILD_ID:
            return

        # ── Joined the creator channel → spawn temp channel ──────────────────
        if after.channel and after.channel.name == CREATOR_NAME:
            cat = after.channel.category
            try:
                temp = await member.guild.create_voice_channel(
                    name=f"🔊 {member.display_name}",
                    category=cat,
                    overwrites=after.channel.overwrites,
                    reason=f"Temp voice — {member}",
                )
                self._temp.add(temp.id)
                await member.move_to(temp)
            except (discord.Forbidden, discord.HTTPException):
                pass

        # ── Left a channel → delete if it's a tracked temp and now empty ─────
        if before.channel and before.channel.id in self._temp:
            if len(before.channel.members) == 0:
                self._temp.discard(before.channel.id)
                try:
                    await before.channel.delete(reason="Temp voice — empty")
                except (discord.NotFound, discord.Forbidden):
                    pass


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceCog(bot))
