import os
from dotenv import load_dotenv

load_dotenv()

# Discord
TOKEN    = os.getenv("DISCORD_TOKEN", "")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

# Minecraft server
MC_IP   = os.getenv("MC_IP", "localhost")
MC_PORT = int(os.getenv("MC_PORT", "25565"))

# RCON (do whitelisty)
RCON_HOST     = os.getenv("RCON_HOST", "localhost")
RCON_PORT     = int(os.getenv("RCON_PORT", "25575"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD", "")

# Role / channel IDs (wypelniane przez /setup albo recznie)
BETA_ROLE_ID    = int(os.getenv("BETA_ROLE_ID", "0"))
STATUS_CHAN_ID   = int(os.getenv("STATUS_CHAN_ID", "0"))
BETA_LOG_CHAN_ID = int(os.getenv("BETA_LOG_CHAN_ID", "0"))
LINKED_ROLE_ID   = int(os.getenv("LINKED_ROLE_ID", "0"))
LINK_LOG_CHAN_ID = int(os.getenv("LINK_LOG_CHAN_ID", "0"))

# DC-MC link webhook server (musi sie zgadzac z discord.link-bot-port w config.yml MC)
LINK_BOT_PORT = int(os.getenv("LINK_BOT_PORT", "8642"))
