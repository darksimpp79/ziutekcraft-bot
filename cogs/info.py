import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID
from branding import GREEN, PURPLE, GOLD, BLOOD, BANNER_URL, THUMBNAIL_URL, SERVER_NAME, footer


# ── Embed: Jak zaczac ─────────────────────────────────────────────────────────

def embed_jak_zaczac() -> discord.Embed:
    e = discord.Embed(
        title="📖  Jak zacząć — Przewodnik dla nowych",
        color=GREEN,
    )
    e.add_field(
        name="1️⃣  Dołącz do bety",
        value="Przejdź do **#🔑-dolacz-do-bety**, kliknij przycisk i wpisz swój nick MC.\nAutomatycznie trafiasz na whitelist serwera.",
        inline=False,
    )
    e.add_field(
        name="2️⃣  Połącz konto Discord",
        value="W **#🔗-polacz-konto** wpisz `/polacz-konto`.\nOtrzymasz kod — wpisz go w MC komendą `/linkdc <kod>`.\nNagroda: **+50 żetonów** za pierwsze połączenie.",
        inline=False,
    )
    e.add_field(
        name="3️⃣  Wybierz klasę",
        value="Na serwerze wpisz `/klasa zmien` i wybierz jedną z **6 klas**:\n`⚔ Wojownik` `🐺 Wilkołak` `🐯 Człowiek-Tygrys`\n`💣 Żołnierz` `🏹 Kusznik` `✦ Mag`",
        inline=False,
    )
    e.add_field(
        name="4️⃣  Graj i zdobywaj",
        value="Rundy trwają **10 minut**. Za każdego kill'a dostajesz:\n• **Monety** — do wydania w arenie (reset po rundzie)\n• **Żetony** — stała waluta, służą do ulepszeń permanentnych",
        inline=False,
    )
    e.add_field(
        name="5️⃣  Rozwijaj postać",
        value="• `/ulepszenia` — permanentne bonusy za żetony\n• `/klasa` → drzewko umiejętności (3 ścieżki na klasę)\n• `/prestiz` — reset z nagrodą po osiągnięciu max levelu\n• `/klan` — dołącz do klanu lub załóż własny",
        inline=False,
    )
    e.add_field(
        name="💡  Porady",
        value="• Odbieraj codzienną nagrodę: `/daily` w **#🤖-komendy**\n• Zapraszaj znajomych: `/zaproszenia` — nagrody za milestony\n• Błąd? Pisz w **#🐛-bugi** (beta)",
        inline=False,
    )
    if THUMBNAIL_URL:
        e.set_thumbnail(url=THUMBNAIL_URL)
    e.set_footer(text=footer("Przewodnik v1"))
    return e


# ── Embed: Klasy ──────────────────────────────────────────────────────────────

def embed_klasy() -> discord.Embed:
    e = discord.Embed(
        title="⚔  6 Klas Bojowych — Wybierz Styl Walki",
        description="Każda klasa ma własne **drzewko umiejętności** (3 ścieżki), unikalne bronie i passive.",
        color=BLOOD,
    )
    e.add_field(
        name="⚔  Wojownik",
        value="Mistrz miecza. Wysoki DPS w zwarciu, duże HP.\n*Ścieżki: Barbarzyńca • Paladyn • Duelist*",
        inline=True,
    )
    e.add_field(
        name="🐺  Wilkołak",
        value="Szybki i agresywny. Bonus DMG przy niskim HP.\n*Ścieżki: Drapieżnik • Watacha • Skarzeń*",
        inline=True,
    )
    e.add_field(name="​", value="​", inline=False)
    e.add_field(
        name="🐯  Człowiek-Tygrys",
        value="Balans szybkości i siły. Efekty trucizny.\n*Ścieżki: Łowca • Cień • Zwinność*",
        inline=True,
    )
    e.add_field(
        name="💣  Żołnierz",
        value="Granaty, Furia, łańcuch killów. Kontrola tłumu.\n*Ścieżki: Berserker • Taktyk • Oblężnik*",
        inline=True,
    )
    e.add_field(name="​", value="​", inline=False)
    e.add_field(
        name="🏹  Kusznik",
        value="Zasięg i amunicja. Niewidoczny z dystansu.\n*Ścieżki: Snajper • Arsenał • Mobilność*",
        inline=True,
    )
    e.add_field(
        name="✦  Mag",
        value="Kula Lodu, Lodowa Tarcza, Arcane Nova. Burst DMG.\n*Ścieżki: Destrukcja • Kontrola • Mistyk*",
        inline=True,
    )
    e.add_field(
        name="​",
        value="Zmień klasę: `/klasa zmien` • Drzewko: `/drzewko` • Level: `/poziom`",
        inline=False,
    )
    if THUMBNAIL_URL:
        e.set_thumbnail(url=THUMBNAIL_URL)
    e.set_footer(text=footer())
    return e


# ── Embed: Ekonomia / Cennik ──────────────────────────────────────────────────

def embed_cennik() -> discord.Embed:
    e = discord.Embed(
        title="💰  Ekonomia i Cennik",
        color=GOLD,
    )
    e.add_field(
        name="💎  Żetony (Tokeny) — waluta stała",
        value=(
            "Zdobywane: **1/kill** (mnożniki za rangi, klany, zwoje, killstreaki)\n"
            "Wydawane na permanentne ulepszenia — **nie resetują się** po rundzie\n\n"
            "Codziennie: `/daily` → **+20–100 żetonów** (wymaga połączonego konta DC)"
        ),
        inline=False,
    )
    e.add_field(
        name="🪙  Monety — waluta rundy",
        value=(
            "Zdobywane: **~50/kill** + killstreak bonus\n"
            "Wydawane: sklep na arenie (`/sklep`) — ekwipunek tymczasowy\n"
            "**Reset po każdej rundzie** — nie trzymaj ich na zapas"
        ),
        inline=False,
    )
    e.add_field(
        name="📊  Koszty głównych funkcji",
        value=(
            "```"
            "Założenie klanu         2 000 żetonów\n"
            "Ulepszenie klanu Lvl1   500–800 żetonów (skarbiec)\n"
            "Wkład osobisty Lvl1     150 żetonów\n"
            "Prestiż (reset+nagroda) 5 000 żetonów\n"
            "Bank — lokata 30 dni    min. 100 żetonów (+10%/dzień)\n"
            "Zwój Siły               150 żetonów\n"
            "Zwój Fortuny            300 żetonów"
            "```"
        ),
        inline=False,
    )
    e.add_field(
        name="🏦  Bank",
        value=(
            "Zamroź żetony i zarabiaj odsetki:\n"
            "• 7 dni → **+3%/dzień**\n"
            "• 14 dni → **+7%/dzień**\n"
            "• 30 dni → **+10%/dzień**\n"
            "Zerwanie przed czasem: **-2% kary**. Użyj `/bank`."
        ),
        inline=False,
    )
    e.set_footer(text=footer("Ceny mogą ulec zmianie w aktualizacjach"))
    return e


# ── Embed: Klany ──────────────────────────────────────────────────────────────

def embed_klany() -> discord.Embed:
    e = discord.Embed(
        title="🏰  System Klanowy",
        color=PURPLE,
    )
    e.add_field(
        name="Tworzenie",
        value="Koszt: **2 000 żetonów**\nKomenda: `/klan stworz <TAG> <Nazwa>`\nTAG max 4 znaki, wyświetlany w chacie przed nickiem",
        inline=False,
    )
    e.add_field(
        name="Poziomy klanu (1–5)",
        value=(
            "```"
            "Lvl 1 →  1 000 killi  | max 10 członków\n"
            "Lvl 2 →  3 000 killi  | max 15 członków\n"
            "Lvl 3 →  8 000 killi  | max 20 członków\n"
            "Lvl 4 → 20 000 killi  | max 25 członków\n"
            "Lvl 5 → MAX            | max 30 członków"
            "```"
        ),
        inline=False,
    )
    e.add_field(
        name="Ulepszenia klanu (ze skarbca)",
        value=(
            "**Trener** — +XP z killów dla wszystkich (max +60%)\n"
            "**Skarbnik** — +Tokeny z killów (max +35%)\n"
            "Każde ulepszenie ma 3 poziomy — opłacane ze skarbca klanu"
        ),
        inline=False,
    )
    e.add_field(
        name="Wkład osobisty",
        value=(
            "Każdy gracz ulepsza swój wkład 1–20 (koszt: `lvl × 150` żetonów)\n"
            "Suma wkładów całego klanu = bonus do tokenów dla **wszystkich**\n"
            "Przykład: 10 graczy na max (lvl 20) = **+20% tokenów**"
        ),
        inline=False,
    )
    e.add_field(
        name="Role",
        value="👑 Lider • ⚔ Oficer • 🧑 Członek\n`/klan awansuj` `/klan degraduj` `/klan przekaz`",
        inline=False,
    )
    e.add_field(
        name="Komendy",
        value=(
            "`/klan stworz` `/klan zapros` `/klan dolacz` `/klan opusc`\n"
            "`/klan wplac` `/klan ulepsz` `/klan wklad` `/klan info` `/klan top`"
        ),
        inline=False,
    )
    e.set_footer(text=footer())
    return e


# ── Embed: Regulamin ──────────────────────────────────────────────────────────

def embed_regulamin() -> discord.Embed:
    e = discord.Embed(
        title="📜  Regulamin Serwera",
        color=BLOOD,
    )
    e.add_field(
        name="§1  Zachowanie",
        value=(
            "• Szanuj innych graczy i staff\n"
            "• Zakaz obrażania, rasizmu, mowy nienawiści\n"
            "• Zakaz spamu, flood'u i reklamy innych serwerów"
        ),
        inline=False,
    )
    e.add_field(
        name="§2  Rozgrywka",
        value=(
            "• Zakaz cheatingi, exploitów i bugusing'u\n"
            "• Kill-trading (celowe podbijanie statystyk z partnerem) = ban\n"
            "• Zgłaszaj bugi w **#🐛-bugi**, nie wykorzystuj ich"
        ),
        inline=False,
    )
    e.add_field(
        name="§3  Kanały Discord",
        value=(
            "• Komendy bota tylko w **#🤖-komendy**\n"
            "• Screeny i klipy tylko w **#🖼-screeny**\n"
            "• Propozycje tylko w **#⭐-propozycje** (jeden temat = jeden post)"
        ),
        inline=False,
    )
    e.add_field(
        name="§4  Sankcje",
        value=(
            "**Warn** → **Mute** → **Kick** → **Ban**\n"
            "Ciężkie naruszenia (cheating, toksyczność) = natychmiastowy ban\n"
            "Odwołania: otwórz ticket w **#🎫-ticket**"
        ),
        inline=False,
    )
    e.add_field(
        name="​",
        value="*Wejście na serwer = akceptacja regulaminu.*",
        inline=False,
    )
    e.set_footer(text=footer("Regulamin v1.0"))
    return e


# ── Cog ───────────────────────────────────────────────────────────────────────

class InfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── /info-setup — wysyła wszystkie embedy do odpowiednich kanałów ─────────

    @app_commands.command(
        name="info-setup",
        description="[ADMIN] Wyślij wszystkie embedy informacyjne do kanałów",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def info_setup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        results = []

        mapping = {
            "📖・jak-zaczac": [embed_jak_zaczac(), embed_klasy()],
            "💰・cennik":     [embed_cennik()],
            "📜・regulamin":  [embed_regulamin()],
            "🏰・klany":      [embed_klany()],
        }

        for ch_name, embeds in mapping.items():
            ch = discord.utils.get(guild.text_channels, name=ch_name)
            if not ch:
                results.append(f"❌ Brak kanału `#{ch_name}`")
                continue
            for emb in embeds:
                await ch.send(embed=emb)
            results.append(f"✅ `#{ch_name}` — {len(embeds)} embed(ów)")

        await interaction.followup.send("\n".join(results), ephemeral=True)

    # ── Pojedyncze komendy do re-postowania konkretnych embedów ───────────────

    @app_commands.command(name="panel-jak-zaczac", description="[ADMIN] Wyślij przewodnik dla nowych")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def panel_jak_zaczac(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=embed_jak_zaczac())
        await interaction.channel.send(embed=embed_klasy())

    @app_commands.command(name="panel-cennik", description="[ADMIN] Wyślij cennik ekonomii")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def panel_cennik(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=embed_cennik())

    @app_commands.command(name="panel-regulamin", description="[ADMIN] Wyślij regulamin")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def panel_regulamin(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=embed_regulamin())

    @app_commands.command(name="panel-klany", description="[ADMIN] Wyślij opis systemu klanowego")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def panel_klany(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=embed_klany())


async def setup(bot: commands.Bot):
    await bot.add_cog(InfoCog(bot))
