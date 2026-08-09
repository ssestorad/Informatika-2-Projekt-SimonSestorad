"""Vizuální styl hry: plsťový herní stůl (barvy, fonty, pomocné funkce na odstíny)."""

__all__ = [
    "FELT_950", "FELT_800", "FELT_700",
    "IVORY_100", "IVORY_300",
    "GOLD_500", "GOLD_300",
    "VIOLET_500", "VIOLET_300",
    "EMBER_500", "INK_900",
    "DISPLAY_FONT", "BODY_FONT", "MONO_FONT",
    "lighten", "darken",
]

FELT_950 = "#0e2019"
FELT_800 = "#1c3a2c"
FELT_700 = "#274a39"
IVORY_100 = "#f4ecd8"
IVORY_300 = "#d9cfb6"
GOLD_500 = "#d6a24a"
GOLD_300 = "#e9c27a"
VIOLET_500 = "#9078c9"
VIOLET_300 = "#b6a4dd"
EMBER_500 = "#cf5b3e"
INK_900 = "#08120e"

DISPLAY_FONT = "Bahnschrift"
BODY_FONT = "Segoe UI"
MONO_FONT = "Consolas"


def lighten(hex_color, amount=0.18):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def darken(hex_color, amount=0.08):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r, g, b = int(r * (1 - amount)), int(g * (1 - amount)), int(b * (1 - amount))
    return f"#{r:02x}{g:02x}{b:02x}"
