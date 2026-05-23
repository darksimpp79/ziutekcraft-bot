"""
Persistent store for Discord-Minecraft account links.
  pending:  code -> {discord_id, expires_at}   (TTL 10 min)
  linked:   discord_id -> {mc_nick, mc_uuid}    (permanent)
"""
import json, time, secrets, string
from pathlib import Path

DATA_DIR     = Path(__file__).parent / "data"
PENDING_FILE = DATA_DIR / "pending_links.json"
LINKED_FILE  = DATA_DIR / "linked_accounts.json"

CODE_CHARS = string.ascii_uppercase + string.digits
CODE_TTL   = 600  # seconds


def _read(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _write(path: Path, data: dict):
    DATA_DIR.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Pending codes ─────────────────────────────────────────────────────────────

def create_code(discord_id: int) -> str:
    """Generate a new pending code, invalidating any previous one for this user."""
    pending = _read(PENDING_FILE)
    now     = time.time()
    # Remove stale/existing entries for this user and expired codes
    pending = {c: v for c, v in pending.items()
               if v["discord_id"] != discord_id and v["expires_at"] > now}
    while True:
        code = "".join(secrets.choice(CODE_CHARS) for _ in range(6))
        if code not in pending:
            break
    pending[code] = {"discord_id": discord_id, "expires_at": now + CODE_TTL}
    _write(PENDING_FILE, pending)
    return code


def consume_code(code: str) -> int | None:
    """Validate and consume a code. Returns discord_id or None if invalid/expired."""
    pending = _read(PENDING_FILE)
    entry   = pending.get(code.upper())
    if not entry:
        return None
    if entry["expires_at"] < time.time():
        del pending[code.upper()]
        _write(PENDING_FILE, pending)
        return None
    discord_id = entry["discord_id"]
    del pending[code.upper()]
    _write(PENDING_FILE, pending)
    return discord_id


# ── Confirmed links ───────────────────────────────────────────────────────────

def save_link(discord_id: int, mc_nick: str, mc_uuid: str):
    linked = _read(LINKED_FILE)
    linked[str(discord_id)] = {"mc_nick": mc_nick, "mc_uuid": mc_uuid, "reward_given": False}
    _write(LINKED_FILE, linked)


def get_link_by_discord(discord_id: int) -> dict | None:
    return _read(LINKED_FILE).get(str(discord_id))


def get_discord_id_by_uuid(mc_uuid: str) -> int | None:
    for did, data in _read(LINKED_FILE).items():
        if data.get("mc_uuid") == mc_uuid:
            return int(did)
    return None


def delete_link(discord_id: int) -> bool:
    linked = _read(LINKED_FILE)
    if str(discord_id) not in linked:
        return False
    del linked[str(discord_id)]
    _write(LINKED_FILE, linked)
    return True


def get_all_links() -> dict:
    return _read(LINKED_FILE)


def is_linked(discord_id: int) -> bool:
    return get_link_by_discord(discord_id) is not None


def try_claim_reward(mc_uuid: str) -> str:
    """Atomically check + mark reward as given.
    Returns: 'ok' (first claim), 'already_claimed', or 'not_linked'."""
    linked = _read(LINKED_FILE)
    for did, data in linked.items():
        if data.get("mc_uuid") == mc_uuid:
            if data.get("reward_given", False):
                return "already_claimed"
            data["reward_given"] = True
            _write(LINKED_FILE, linked)
            return "ok"
    return "not_linked"
