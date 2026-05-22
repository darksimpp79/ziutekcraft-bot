"""
ZiutekCraft — centralne stałe brandingowe.
Zmień BANNER_URL na link do swojej grafiki (imgur, CDN, attachmenty Discord itp.)
"""

# ── Kolory (z grafiki: neonowa zieleń + fiolet) ───────────────────────────────
GREEN  = 0x00CC44   # neonowa zieleń — "craft" z logo
PURPLE = 0x7700BB   # fiolet portalu
DARK   = 0x111111   # ciemne tło
RED    = 0xCC2200   # błędy / ostrzeżenia
GOLD   = 0xFFAA00   # rangi / nagrody

# ── Tekst brandingowy ─────────────────────────────────────────────────────────
SERVER_NAME = "ZiutekCraft"
TAGLINE_1   = "Twórz • Graj • Zwyciężaj • Razem"
TAGLINE_2   = "Twój serwer. Twoja przygoda."
FOOTER      = "ZiutekCraft ⚔  |  ziutekcraft.pl"

# ── Grafiki — wklej URL po wrzuceniu na imgur/CDN ─────────────────────────────
# Jak wrzucić: przeciągnij obraz na dowolny kanał Discord,
# kliknij PPM → Kopiuj link → wklej tutaj.
BANNER_URL      = ""   # szeroka grafika do embed .set_image()
THUMBNAIL_URL   = ""   # kwadratowa do embed .set_thumbnail()  (np. trzecia grafika)
ICON_URL        = ""   # ikona serwera (opcjonalna)


def footer(extra: str = "") -> str:
    """Zwraca tekst stopki embeda, opcjonalnie z dopiskiem."""
    return f"{FOOTER}  {('| ' + extra) if extra else ''}".strip()
