"""
AssasinCore — centralne stałe brandingowe.
Zmień BANNER_URL na link do swojej grafiki (imgur, CDN, attachmenty Discord itp.)
"""

# ── Kolory ────────────────────────────────────────────────────────────────────
GREEN  = 0x00CC44   # neonowa zieleń
PURPLE = 0x7700BB   # fiolet
DARK   = 0x111111   # ciemne tło
RED    = 0xCC2200   # błędy / ostrzeżenia
GOLD   = 0xFFAA00   # rangi / nagrody
BLOOD  = 0xAA1111   # akcent assassin

# ── Tekst brandingowy ─────────────────────────────────────────────────────────
SERVER_NAME = "Assassin Arena"
TAGLINE_1   = "Klasa. Kill. Klan. Zwycięstwo."
TAGLINE_2   = "6 klas. Bez litości. Tylko jeden na szczycie."
FOOTER      = "Assassin Arena ⚔  |  by ziutek"

# ── Grafiki — wklej URL po wrzuceniu na imgur/CDN ─────────────────────────────
# Jak wrzucić: przeciągnij obraz na dowolny kanał Discord,
# kliknij PPM → Kopiuj link → wklej tutaj.
BANNER_URL      = ""   # szeroka grafika do embed .set_image()
THUMBNAIL_URL   = ""   # kwadratowa do embed .set_thumbnail()  (np. trzecia grafika)
ICON_URL        = ""   # ikona serwera (opcjonalna)


def footer(extra: str = "") -> str:
    """Zwraca tekst stopki embeda, opcjonalnie z dopiskiem."""
    return f"{FOOTER}  {('| ' + extra) if extra else ''}".strip()
