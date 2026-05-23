"""
Persistent store for RCON rewards that failed to deliver (server offline etc.).
Format: data/pending_rewards.json — list of reward dicts.
"""
import json, time, logging
from pathlib import Path

DATA_DIR     = Path(__file__).parent / "data"
PENDING_FILE = DATA_DIR / "pending_rewards.json"

log = logging.getLogger(__name__)


def _read() -> list[dict]:
    if PENDING_FILE.exists():
        try:
            return json.loads(PENDING_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _write(data: list[dict]):
    DATA_DIR.mkdir(exist_ok=True)
    PENDING_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def add(discord_id: int, nick: str, amount: int, reason: str):
    """Queue a reward that could not be delivered."""
    pending = _read()
    pending.append({
        "discord_id": discord_id,
        "nick":       nick,
        "amount":     amount,
        "reason":     reason,
        "created_at": int(time.time()),
    })
    _write(pending)
    log.warning("Pending reward queued: %s +%d (%s)", nick, amount, reason)


def flush(rcon_fn) -> tuple[int, int]:
    """
    Try to deliver all pending rewards via rcon_fn(nick, amount).
    Returns (delivered, still_pending).
    """
    pending = _read()
    if not pending:
        return 0, 0

    failed  = []
    delivered = 0
    for entry in pending:
        try:
            rcon_fn(entry["nick"], entry["amount"])
            delivered += 1
            log.info("Pending delivered: %s +%d (%s)", entry["nick"], entry["amount"], entry["reason"])
        except Exception as e:
            log.warning("Pending still failing for %s: %s", entry["nick"], e)
            failed.append(entry)

    _write(failed)
    return delivered, len(failed)


def count() -> int:
    return len(_read())
