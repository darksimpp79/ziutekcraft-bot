# AssasinBot — Discord bot dla ZiutekCraft Beta

Python 3.11+ / discord.py 2.x

---

## Komendy

| Komenda | Opis | Uprawnienia |
|---------|------|-------------|
| `/setup` | Tworzy wszystkie kanały i role na Discordzie | Admin |
| `/beta-panel` | Wysyła panel rejestracji z przyciskiem | Admin |
| `/status` | Sprawdza status serwera MC na żądanie | Wszyscy |
| `/whitelist-add <nick>` | Ręcznie dodaje nick do whitelisty | Admin |

---

## Szybki start

### 1. Stwórz bota na Discord Developer Portal

1. Wejdź na https://discord.com/developers/applications
2. **New Application** → nadaj nazwę (np. `ZiutekCraft Bot`)
3. Zakładka **Bot** → **Add Bot**
4. Skopiuj **Token** (używasz go w `.env`)
5. W sekcji **Privileged Gateway Intents** włącz:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
6. Zakładka **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Manage Roles`, `Manage Channels`, `Send Messages`, `Read Message History`
   - Skopiuj link i wklej w przeglądarce → dodaj bota na swój serwer

### 2. Skonfiguruj .env

```bash
cp .env.example .env
# Wypełnij .env swoimi danymi
```

Żeby skopiować ID serwera Discord:
1. Ustawienia Discord → Zaawansowane → **Tryb Dewelopera** ✅
2. Prawy klik na ikonę serwera → **Kopiuj identyfikator serwera**

### 3. Zainstaluj zależności

```bash
cd discord-bot
pip install -r requirements.txt
```

### 4. Włącz RCON na serwerze Minecraft

W `server.properties`:
```properties
enable-rcon=true
rcon.port=25575
rcon.password=twoje_silne_haslo
```
Restart serwera MC.

### 5. Uruchom bota

```bash
python bot.py
```

Bot zaloguje się i zsynchronizuje slash komendy. Może minąć do 1 minuty zanim komendy będą widoczne.

---

## Setup serwera Discord

Po uruchomieniu bota na swoim Discord wpisz:

```
/setup
```

Bot automatycznie stworzy:

**Role:**
- 👑 Admin
- 🛡️ Mod
- ⚔ Beta Tester
- ✔ Zweryfikowany

**Kanały:**
```
📢 OGŁOSZENIA
  📣-ogłoszenia     (tylko do odczytu)
  📋-zasady         (tylko do odczytu)

🎮 BETA TESTING
  🔑-rejestracja    ← tutaj wysyłasz /beta-panel
  🟢-status-serwera ← auto-aktualizowany co 5 min
  💬-beta-czat      (tylko Beta Testerzy)
  🐛-bugi           (tylko Beta Testerzy)
  💡-pomysły        (tylko Beta Testerzy)

💬 SPOŁECZNOŚĆ
  👋-ogólny
  🎨-media

🔧 STAFF (ukryte dla zwykłych)
  📊-staff-czat
  📥-beta-log       ← logi rejestracji
```

Następnie w `#🔑-rejestracja` wpisz `/beta-panel` — pojawi się embed z przyciskiem.

---

## Jak działa rejestracja

1. Gracz klika **⚔ Dołącz do Bety**
2. Pojawia się okno modalne z polem na nick MC
3. Bot waliduje nick (3-16 znaków, litery/cyfry/`_`)
4. Automatycznie dodaje nick do whitelisty via RCON
5. Nadaje rolę **⚔ Beta Tester** (daje dostęp do kanałów beta)
6. Loguje zdarzenie w `#📥-beta-log`

---

## Hosting (po testach lokalnych)

Najprościej: VPS na tym samym maszycie co Minecraft.

```bash
# Na VPS, w tle z nohup lub screen
screen -S bot
python bot.py
# Ctrl+A D aby odłączyć
```

Lub jako systemd service:
```ini
[Unit]
Description=AssasinBot Discord
After=network.target

[Service]
WorkingDirectory=/home/user/AssasinCore/discord-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```
