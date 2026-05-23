import json, time
from pathlib import Path

DATA_DIR   = Path(__file__).parent.parent / "data"
DAILY_FILE = DATA_DIR / "daily_rewards.json"

COOLDOWN    = 86400  # 24h in seconds
BASE_TOKENS = 10
STREAK_STEP = 2      # +2 tokens per streak day
MAX_BONUS   = 20     # cap at +20 (= 10-day streak)


def _read() -> dict:
    if DAILY_FILE.exists():
        try:
            return json.loads(DAILY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _write(data: dict):
    DATA_DIR.mkdir(exist_ok=True)
    DAILY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def daily_claim(discord_id: int) -> dict:
    """
    Atomically claim the daily reward for a Discord user.
    Returns {"ok": True, "amount": int, "streak": int}
         or {"ok": False, "wait_seconds": int}
    """
    data  = _read()
    entry = data.get(str(discord_id), {"last_claim": 0, "streak": 0})
    now   = time.time()
    diff  = now - entry["last_claim"]

    if diff < COOLDOWN:
        return {"ok": False, "wait_seconds": int(COOLDOWN - diff)}

    entry["streak"] = (entry.get("streak", 0) + 1) if diff < COOLDOWN * 2 else 1
    entry["last_claim"] = now
    data[str(discord_id)] = entry
    _write(data)

    streak = entry["streak"]
    bonus  = min((streak - 1) * STREAK_STEP, MAX_BONUS)
    total  = BASE_TOKENS + bonus
    return {"ok": True, "amount": total, "streak": streak}


async def setup(bot):
    pass  # no Discord commands — /daily is now an in-game command
