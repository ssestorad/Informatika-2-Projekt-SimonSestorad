from tkinter import *
from tkinter import messagebox
from random import randint, choice
from math import radians, cos, sin
from player import Player
from game import FarkleGame
from abilities import ABILITY_NAMES
from strings import STRINGS
from ai import AI_PROFILES, pick_scoring_dice_indices, should_bank

# ---- vizuální styl: plsťový herní stůl ----
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

DIE_PIP_LAYOUT = {
    1: [(2, 2)],
    2: [(1, 1), (3, 3)],
    3: [(1, 1), (2, 2), (3, 3)],
    4: [(1, 1), (1, 3), (3, 1), (3, 3)],
    5: [(1, 1), (1, 3), (2, 2), (3, 1), (3, 3)],
    6: [(1, 1), (1, 3), (2, 1), (2, 3), (3, 1), (3, 3)],
}

RESOLUTIONS = ["1100x900", "1280x1024", "1000x800", "1366x950"]

settings = {
    "language": "cs",
    "target_score": 10000,
    "bank_minimum": 500,
    "resolution": "1100x900",
}

# Udalosti se ukladaji jako (klic, {parametry}) a prekladaji az pri vykresleni,
# aby prepnuti jazyka v nastaveni fungovalo bez zasahu do herni logiky.
ABILITY_KEY_FIELDS = {
    "new_ability": ["ability_key"],
    "primary_abilities": ["a1_key", "a2_key"],
}

AI_STEP_DELAY_MS = 900

game = None
root = None
game_window = None
player_names = []
log_events = []
ai_player = None
ai_profile = None

def t(key, **kwargs):
    template = STRINGS[settings["language"]][key]
    return template.format(**kwargs) if kwargs else template

def ability_name(key):
    return ABILITY_NAMES[settings["language"]].get(key, key)

def format_event(event):
    key, params = event
    data = dict(params)
    for field in ABILITY_KEY_FIELDS.get(key, []):
        raw = data.pop(field)
        data[field[:-4]] = ability_name(raw).upper()
    return STRINGS[settings["language"]][f"ev_{key}"].format(**data)

def format_combo(combo):
    lang = settings["language"]
    kind = combo[0]
    if kind == "triple":
        _, value, points = combo
        return STRINGS[lang]["combo_triple"].format(value=value, points=points)
    _, points = combo
    return STRINGS[lang][f"combo_{kind}"].format(points=points)

def push_event(key, **params):
    global log_events
    log_events.append((key, params))
    log_events[:] = log_events[-30:]

def drain_events(*sources):
    global log_events
    for source in sources:
        if source:
            log_events.extend(source)
            log_events[:] = log_events[-30:]
            source.clear()

def flat_button(parent, text, bg, fg, command, font_size=11):
    return Button(parent, text=text, font=(BODY_FONT, font_size, "bold"), bg=bg, fg=fg,
                  activebackground=bg, activeforeground=fg, relief=FLAT, bd=0,
                  padx=26, pady=12, cursor="hand2", command=command)

def choice_chip(parent, text, selected, on_click):
    border_color = GOLD_500 if selected else FELT_700
    wrapper = Frame(parent, bg=border_color, padx=3, pady=3)
    label = Label(wrapper, text=text, font=(MONO_FONT, 10, "bold"), bg=IVORY_100, fg=FELT_700,
                  padx=14, pady=8, cursor="hand2")
    label.pack()
    label.bind("<Button-1>", lambda e: on_click())
    return wrapper

def is_ai_turn():
    return ai_player is not None and game is not None and game.current_player is ai_player

def draw_die(canvas, size, value, pip_color, bg_color):
    canvas.configure(bg=bg_color)
    canvas.delete("all")
    if value == 0:
        canvas.create_text(size / 2, size / 2, text="?", fill=pip_color,
                            font=(MONO_FONT, int(size * 0.28), "bold"))
        return
    radius = size * 0.07
    for row, col in DIE_PIP_LAYOUT[value]:
        cx = size * (col / 4)
        cy = size * (row / 4)
        canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                            fill=pip_color, outline="")

def draw_flag_cz(canvas):
    w, h = 46, 30
    canvas.create_rectangle(0, 0, w, h / 2, fill="#ffffff", outline="")
    canvas.create_rectangle(0, h / 2, w, h, fill="#d7141a", outline="")
    canvas.create_polygon(0, 0, 0, h, w * 0.42, h / 2, fill="#11457e", outline="")

def draw_flag_en(canvas):
    w, h = 46, 30
    half = w / 2

    # levá polovina – stylizovaný Union Jack (diagonální i rovný kříž)
    canvas.create_rectangle(0, 0, half, h, fill="#012169", outline="")
    canvas.create_line(0, 0, half, h, fill="#ffffff", width=4)
    canvas.create_line(0, h, half, 0, fill="#ffffff", width=4)
    canvas.create_line(half / 2, 0, half / 2, h, fill="#ffffff", width=7)
    canvas.create_line(0, h / 2, half, h / 2, fill="#ffffff", width=7)
    canvas.create_line(half / 2, 0, half / 2, h, fill="#c8102e", width=3)
    canvas.create_line(0, h / 2, half, h / 2, fill="#c8102e", width=3)

    # pravá polovina – stylizovaná americká vlajka (pruhy + hvězdy v kantonu)
    stripe_h = h / 5
    colors = ["#b22234", "#ffffff", "#b22234", "#ffffff", "#b22234"]
    for i, c in enumerate(colors):
        canvas.create_rectangle(half, i * stripe_h, w, (i + 1) * stripe_h, fill=c, outline="")
    canton_w = half * 0.6
    canton_h = stripe_h * 2
    canvas.create_rectangle(half, 0, half + canton_w, canton_h, fill="#3c3b6e", outline="")
    for sx, sy in [(0.25, 0.3), (0.75, 0.3), (0.5, 0.75)]:
        cx, cy = half + canton_w * sx, canton_h * sy
        canvas.create_oval(cx - 1.4, cy - 1.4, cx + 1.4, cy + 1.4, fill="#ffffff", outline="")

def draw_flag_il(canvas):
    w, h = 46, 30
    canvas.create_rectangle(0, 0, w, h, fill="#ffffff", outline="")
    stripe_h = h * 0.16
    canvas.create_rectangle(0, h * 0.12, w, h * 0.12 + stripe_h, fill="#0038b8", outline="")
    canvas.create_rectangle(0, h - h * 0.12 - stripe_h, w, h - h * 0.12, fill="#0038b8", outline="")

    # Davidova hvězda – dva překrývající se rovnostranné trojúhelníky
    cx, cy, r = w / 2, h / 2, h * 0.26

    def triangle_points(rotation_deg):
        points = []
        for k in range(3):
            angle = radians(rotation_deg + k * 120 - 90)
            points.extend([cx + r * cos(angle), cy + r * sin(angle)])
        return points

    canvas.create_polygon(*triangle_points(0), outline="#0038b8", fill="", width=2)
    canvas.create_polygon(*triangle_points(60), outline="#0038b8", fill="", width=2)

def language_button(parent, lang_code, draw_fn, label_key, on_change):
    selected = settings["language"] == lang_code
    border_color = GOLD_500 if selected else FELT_700

    wrapper = Frame(parent, bg=border_color, padx=3, pady=3)
    canvas = Canvas(wrapper, width=46, height=30, highlightthickness=0, bg=IVORY_100)
    canvas.pack()
    draw_fn(canvas)
    Label(wrapper, text=STRINGS[settings["language"]][label_key], font=(MONO_FONT, 8, "bold"),
          bg=IVORY_100, fg=FELT_700).pack(fill=X)
    canvas.configure(cursor="hand2")

    def select(event=None):
        settings["language"] = lang_code
        on_change()

    canvas.bind("<Button-1>", select)
    return wrapper

def show_game_screen():
    global game_window, game
    if game_window is None:
        game_window = Toplevel()
        game_window.geometry(settings["resolution"])
        game_window.resizable(False, False)
        game_window.configure(bg=FELT_950)

    game_window.title(f"{game.current_player.name} - {t('game_window_suffix')}")

    # Nový obsah se sestaví stranou a vymění se za starý až v okamžiku,
    # kdy je hotový – okno tak nikdy není mezitím prázdné (žádné bliknutí).
    old_content = getattr(game_window, "content_frame", None)
    content = Frame(game_window, bg=FELT_950)

    opponent = game.get_opponent()
    ability = game.current_player.get_active_ability()

    # ---------- scoreboard rail ----------
    scoreboard = Frame(content, bg=FELT_950)
    scoreboard.pack(fill=X)

    pad = Frame(scoreboard, bg=FELT_950)
    pad.pack(fill=X, padx=26, pady=(16, 10))
    pad.columnconfigure(0, weight=1)
    pad.columnconfigure(2, weight=1)

    def score_block(parent, player, name_color, bar_color, anchor):
        block = Frame(parent, bg=FELT_950)
        Label(block, text=player.name.upper(), font=(MONO_FONT, 11, "bold"),
              bg=FELT_950, fg=name_color).pack(anchor=anchor)
        Label(block, text=f"{player.total_score:,}", font=(MONO_FONT, 26, "bold"),
              bg=FELT_950, fg=IVORY_100).pack(anchor=anchor)

        track = Frame(block, bg=FELT_700, height=6, width=220)
        track.pack(anchor=anchor, pady=(4, 2))
        track.pack_propagate(False)
        pct = min(100, player.total_score / game.target_score * 100)
        fill_w = int(220 * pct / 100)
        fill_x = 220 - fill_w if anchor == "e" else 0
        Frame(track, bg=bar_color, height=6, width=fill_w).place(x=fill_x, y=0)

        Label(block, text=f"{player.total_score:,} / {game.target_score:,}", font=(MONO_FONT, 9),
              bg=FELT_950, fg=IVORY_300).pack(anchor=anchor)
        return block

    score_block(pad, game.current_player, GOLD_300, GOLD_500, "w").grid(row=0, column=0, sticky="w")

    hud_center = Frame(pad, bg=FELT_950)
    hud_center.grid(row=0, column=1, padx=30)
    ability_text = f"{t('ability_prefix')}{ability_name(ability).upper()}"
    if ability in game.current_player.abilities_used:
        ability_text += t("ability_used_suffix")
    Label(hud_center, text=ability_text, font=(MONO_FONT, 10, "bold"),
          bg=VIOLET_300, fg=FELT_950, padx=12, pady=4).pack()
    Label(hud_center, text=t("turn_label", turn=game.current_player.turn_count), font=(MONO_FONT, 9),
          bg=FELT_950, fg=IVORY_300).pack(pady=(6, 0))

    score_block(pad, opponent, IVORY_300, VIOLET_500, "e").grid(row=0, column=2, sticky="e")

    Frame(content, bg=EMBER_500 if game.farkle_pending else GOLD_500, height=2).pack(fill=X)

    # ---------- table area: ledger + dice pit ----------
    table_area = Frame(content, bg=FELT_800)
    table_area.pack(fill=BOTH, expand=True)

    ledger = Frame(table_area, bg=IVORY_100, width=260)
    ledger.pack(side=LEFT, fill=Y, padx=(26, 16), pady=22)
    ledger.pack_propagate(False)

    ledger_pad = Frame(ledger, bg=IVORY_100)
    ledger_pad.pack(fill=BOTH, expand=True, padx=20, pady=20)

    sel_score, sel_combos = game.current_player.calculate_score(only_selected=True)
    points_suffix = t("points_suffix")

    Label(ledger_pad, text=t("ledger_selected"), font=(MONO_FONT, 10, "bold"),
          bg=IVORY_100, fg=FELT_700, anchor="w").pack(fill=X)
    Label(ledger_pad, text=f"{sel_score} {points_suffix}", font=(DISPLAY_FONT, 22, "bold"),
          bg=IVORY_100, fg=INK_900, anchor="w").pack(fill=X, pady=(0, 6))
    for combo in sel_combos:
        Label(ledger_pad, text=f"✓ {format_combo(combo)}", font=(MONO_FONT, 11),
              bg=IVORY_100, fg=FELT_700, anchor="w").pack(fill=X)

    Frame(ledger_pad, bg=FELT_700, height=1).pack(fill=X, pady=16)

    Label(ledger_pad, text=t("ledger_round"), font=(MONO_FONT, 10, "bold"),
          bg=IVORY_100, fg=FELT_700, anchor="w").pack(fill=X)
    Label(ledger_pad, text=f"{game.current_player.round_score} {points_suffix}", font=(DISPLAY_FONT, 22, "bold"),
          bg=IVORY_100, fg=INK_900, anchor="w").pack(fill=X)

    dice_pit = Frame(table_area, bg=FELT_700)
    dice_pit.pack(side=RIGHT, fill=BOTH, expand=True, padx=(0, 26), pady=22)

    if game.farkle_pending:
        Label(dice_pit, text=t("farkle_banner"), font=(DISPLAY_FONT, 15, "bold"),
              bg=FELT_700, fg=EMBER_500).pack(pady=(18, 0))

    dice_grid = Frame(dice_pit, bg=FELT_700)
    dice_grid.pack(expand=True)

    for i in range(6):
        die = game.current_player.dice[i]

        if game.farkle_pending:
            tile_bg, status, pip_color = IVORY_300, t("die_active"), EMBER_500
        elif die.kept:
            tile_bg, status, pip_color = IVORY_300, t("die_kept"), INK_900
        elif die.selected:
            tile_bg, status, pip_color = IVORY_100, t("die_selected"), GOLD_500
        else:
            tile_bg, status, pip_color = IVORY_100, t("die_active"), INK_900

        if game.farkle_pending:
            border_color = EMBER_500
        else:
            border_color = GOLD_500 if die.selected else FELT_700

        wrapper = Frame(dice_grid, bg=border_color, padx=3, pady=3)
        wrapper.grid(row=i // 3, column=i % 3, padx=10, pady=10)

        canvas = Canvas(wrapper, width=110, height=110, highlightthickness=0)
        canvas.pack()
        draw_die(canvas, 110, die.value, pip_color, tile_bg)

        Label(wrapper, text=status, font=(MONO_FONT, 8, "bold"), bg=tile_bg, fg=FELT_700).pack(fill=X)

        if not die.kept and die.value > 0 and not game.farkle_pending and not is_ai_turn():
            canvas.configure(cursor="hand2")
            canvas.bind("<Button-1>", lambda e, idx=i: select_die(idx))

    # ---------- event log ----------
    log_strip = Frame(content, bg=INK_900, height=100)
    log_strip.pack(fill=X)
    log_strip.pack_propagate(False)

    log_pad = Frame(log_strip, bg=INK_900)
    log_pad.pack(fill=BOTH, expand=True, padx=26, pady=10)

    if log_events:
        for key, params in log_events[-4:]:
            text = format_event((key, params))
            if key == "farkle":
                color = EMBER_500
            elif key in ("new_ability", "game_start", "primary_abilities", "target"):
                color = IVORY_300
            else:
                color = GOLD_300
            Label(log_pad, text=text, font=(MONO_FONT, 10), bg=INK_900, fg=color,
                  anchor="w", justify=LEFT).pack(fill=X)
    else:
        Label(log_pad, text=t("log_empty"), font=(MONO_FONT, 10), bg=INK_900, fg=IVORY_300,
              anchor="w", justify=LEFT).pack(fill=X)

    # ---------- actions ----------
    action_row = Frame(content, bg=FELT_950)
    action_row.pack(fill=X)

    action_pad = Frame(action_row, bg=FELT_950)
    action_pad.pack(pady=18)

    if is_ai_turn():
        Label(action_pad, text=t("ai_turn_status"), font=(MONO_FONT, 12, "bold"),
              bg=FELT_950, fg=VIOLET_300).pack()
    elif game.farkle_pending:
        flat_button(action_pad, t("btn_continue"), EMBER_500, IVORY_100, continue_after_farkle).pack()
    else:
        flat_button(action_pad, t("btn_roll"), GOLD_500, INK_900, roll_dice_action).pack(side=LEFT, padx=8)

        if sel_score > 0:
            flat_button(action_pad, t("btn_confirm"), VIOLET_500, IVORY_100, keep_dice).pack(side=LEFT, padx=8)

        if game.current_player.round_score >= settings["bank_minimum"]:
            flat_button(action_pad, t("btn_bank"), IVORY_100, INK_900, bank_points_action).pack(side=LEFT, padx=8)

    # Novy obsah se nejdriv prekryje pres stary (place, ne pack – umi
    # se prekryvat) a az pak se stary smaze, aby mezi tim okno ani na
    # okamzik nebylo prazdne.
    content.place(x=0, y=0, relwidth=1, relheight=1)
    if old_content is not None:
        old_content.destroy()
    game_window.content_frame = content

def select_die(index):
    die = game.current_player.dice[index]
    if not die.kept and die.value > 0:
        die.selected = not die.selected
        show_game_screen()

def roll_dice_action():
    global game
    if any(d.selected for d in game.current_player.dice):
        push_event("confirm_first")
        show_game_screen()
        return

    success = game.current_player.roll_dice()

    if not success:
        game.current_player.farkle_count += 1
        ability = game.current_player.get_active_ability()
        if ability == "insurance" and ability not in game.current_player.abilities_used:
            saved_points = game.current_player.round_score
            if saved_points > 0:
                game.current_player.total_score += saved_points
                push_event("insurance_saved", player=game.current_player.name, points=saved_points)
            else:
                push_event("insurance_failed", player=game.current_player.name)
            game.current_player.abilities_used[ability] = True
        else:
            push_event("farkle", player=game.current_player.name)
        game.farkle_pending = True
        show_game_screen()
    else:
        show_game_screen()

def continue_after_farkle():
    global game
    game.farkle_pending = False
    next_player()

def keep_dice():
    global game
    points, is_hot = game.current_player.confirm_selection()
    if is_hot:
        push_event("hot_dice")
    show_game_screen()

def ability_list(player):
    names = [ability_name(a) for a in player.abilities_used]
    return ", ".join(names) if names else t("no_abilities")

def show_end_screen(winner):
    global game_window, root

    old_content = getattr(game_window, "content_frame", None)
    content = Frame(game_window, bg=FELT_950)

    p1, p2 = game.head_player, game.tail_player

    def color_for(player):
        return GOLD_300 if player is winner else IVORY_300

    Label(content, text=t("end_winner", name=winner.name.upper()), font=(DISPLAY_FONT, 34, "bold"),
          bg=FELT_950, fg=GOLD_300).pack(pady=(36, 4))
    Frame(content, bg=VIOLET_500, height=2, width=80).pack(pady=(0, 26))

    table = Frame(content, bg=FELT_800)
    table.pack(padx=60, pady=(0, 30), fill=X)

    header = Frame(table, bg=FELT_800)
    header.pack(fill=X, padx=24, pady=(20, 10))
    header.columnconfigure(0, weight=2)
    header.columnconfigure(1, weight=1)
    header.columnconfigure(2, weight=1)
    Label(header, text="", bg=FELT_800).grid(row=0, column=0, sticky="w")
    Label(header, text=p1.name.upper(), font=(MONO_FONT, 12, "bold"), bg=FELT_800, fg=color_for(p1)).grid(row=0, column=1)
    Label(header, text=p2.name.upper(), font=(MONO_FONT, 12, "bold"), bg=FELT_800, fg=color_for(p2)).grid(row=0, column=2)

    def farkle_pct(player):
        return f" ({player.farkle_count / player.turn_count * 100:.0f} %)" if player.turn_count else ""

    rows = [
        (t("end_final_score"), f"{p1.total_score:,}", f"{p2.total_score:,}"),
        (t("end_turns"), f"{p1.turn_count}", f"{p2.turn_count}"),
        (t("end_farkles"), f"{p1.farkle_count}{farkle_pct(p1)}", f"{p2.farkle_count}{farkle_pct(p2)}"),
        (t("end_banks"), f"{p1.bank_count}", f"{p2.bank_count}"),
        (t("end_best_bank"), f"{p1.best_bank:,}", f"{p2.best_bank:,}"),
        (t("end_total_banked"), f"{p1.total_banked:,}", f"{p2.total_banked:,}"),
        (t("end_gained"), f"+{p1.points_gained_from_abilities:,}", f"+{p2.points_gained_from_abilities:,}"),
        (t("end_lost"), f"-{p1.points_lost_to_attacks:,}", f"-{p2.points_lost_to_attacks:,}"),
        (t("end_abilities"), ability_list(p1), ability_list(p2)),
    ]

    for label, v1, v2 in rows:
        row = Frame(table, bg=FELT_800)
        row.pack(fill=X, padx=24, pady=6)
        row.columnconfigure(0, weight=2)
        row.columnconfigure(1, weight=1)
        row.columnconfigure(2, weight=1)
        Label(row, text=label, font=(MONO_FONT, 10), bg=FELT_800, fg=IVORY_300, anchor="w").grid(row=0, column=0, sticky="w")
        Label(row, text=v1, font=(MONO_FONT, 11, "bold"), bg=FELT_800, fg=color_for(p1),
              wraplength=170, justify=CENTER).grid(row=0, column=1)
        Label(row, text=v2, font=(MONO_FONT, 11, "bold"), bg=FELT_800, fg=color_for(p2),
              wraplength=170, justify=CENTER).grid(row=0, column=2)

    Frame(table, bg=FELT_800, height=10).pack()

    flat_button(content, t("end_close"), GOLD_500, INK_900, root.destroy, font_size=13).pack(pady=(0, 30))

    content.place(x=0, y=0, relwidth=1, relheight=1)
    if old_content is not None:
        old_content.destroy()
    game_window.content_frame = content

def bank_points_action():
    global game, root
    opponent = game.get_opponent()
    banked = game.current_player.bank_points(opponent)

    push_event("banked", player=game.current_player.name, amount=banked)
    drain_events(game.current_player.events)

    winner = game.check_winner()
    if winner:
        show_end_screen(winner)
    else:
        next_player()

def next_player():
    global game
    game.switch_player()
    drain_events(game.current_player.events)
    for die in game.current_player.dice:
        die.reset_full()
    show_game_screen()
    ai_maybe_take_turn()

def start_game():
    global game, root, ai_player, ai_profile
    ai_player = None
    ai_profile = None
    game = FarkleGame()
    game.target_score = settings["target_score"]
    p1 = Player(player_names[0])
    p2 = Player(player_names[1])
    game.start_game(p1, p2)
    drain_events(game.events, p1.events, p2.events)
    show_game_screen()

def start_game_vs_ai(human_name, difficulty):
    global game, root, ai_player, ai_profile
    game = FarkleGame()
    game.target_score = settings["target_score"]
    p1 = Player(human_name)
    p2 = Player(t("ai_name"))
    ai_player = p2
    ai_profile = difficulty
    game.start_game(p1, p2)
    drain_events(game.events, p1.events, p2.events)
    show_game_screen()
    ai_maybe_take_turn()

# ---------- orchestrace tahu AI ----------
# Kazdy krok tahu AI (hod, vyber, potvrzeni, rozhodnuti bankovat/hazet dal)
# se naplanuje s malym zpozdenim pres game_window.after(), aby hrac stihl
# sledovat, co se deje, misto aby se cely tah AI odehral naraz.

def ai_maybe_take_turn():
    if is_ai_turn():
        game_window.after(AI_STEP_DELAY_MS, ai_roll_step)

def ai_roll_step():
    if not is_ai_turn():
        return
    roll_dice_action()
    if game.farkle_pending:
        game_window.after(AI_STEP_DELAY_MS, ai_continue_after_farkle_step)
    else:
        game_window.after(AI_STEP_DELAY_MS, ai_select_step)

def ai_continue_after_farkle_step():
    if not is_ai_turn():
        return
    continue_after_farkle()

def ai_select_step():
    if not is_ai_turn():
        return
    for i in pick_scoring_dice_indices(game.current_player.dice):
        game.current_player.dice[i].selected = True
    show_game_screen()
    game_window.after(AI_STEP_DELAY_MS, ai_confirm_step)

def ai_confirm_step():
    if not is_ai_turn():
        return
    keep_dice()
    game_window.after(AI_STEP_DELAY_MS, ai_decide_step)

def ai_decide_step():
    if not is_ai_turn():
        return
    player = game.current_player
    dice_remaining = sum(1 for d in player.dice if not d.kept)
    if should_bank(player, dice_remaining, settings["bank_minimum"], settings["target_score"], ai_profile):
        bank_points_action()
    else:
        game_window.after(AI_STEP_DELAY_MS, ai_roll_step)

def player2_screen(root_win):
    global player_names
    root_win.withdraw()
    win = Toplevel()
    win.title(t("win_title_p2"))
    win.geometry("360x300")
    win.configure(bg=FELT_950)

    pad = Frame(win, bg=FELT_800)
    pad.pack(fill=BOTH, expand=True)

    inner = Frame(pad, bg=FELT_800)
    inner.pack(expand=True, fill=X, padx=34, pady=34)

    Label(inner, text=t("label_name2"), font=(MONO_FONT, 10, "bold"),
          bg=FELT_800, fg=VIOLET_300, anchor="w").pack(fill=X, pady=(0, 8))

    entry = Entry(inner, font=(BODY_FONT, 14), bg=IVORY_100, fg=INK_900, relief=FLAT,
                  insertbackground=INK_900, highlightthickness=0)
    entry.pack(fill=X, ipady=8)
    entry.focus()

    def submit():
        name = entry.get().strip()
        if name and name != player_names[0]:
            player_names.append(name)
            win.destroy()
            start_game()
        else:
            messagebox.showerror(t("err_title"), t("err_dup_name"))

    entry.bind("<Return>", lambda e: submit())

    flat_button(inner, t("btn_start_game"), GOLD_500, INK_900, submit, font_size=12).pack(fill=X, pady=(20, 0))

def player1_screen(root_win):
    global player_names
    root_win.withdraw()
    win = Toplevel()
    win.title(t("win_title_p1"))
    win.geometry("360x300")
    win.configure(bg=FELT_950)

    pad = Frame(win, bg=FELT_800)
    pad.pack(fill=BOTH, expand=True)

    inner = Frame(pad, bg=FELT_800)
    inner.pack(expand=True, fill=X, padx=34, pady=34)

    Label(inner, text=t("label_name1"), font=(MONO_FONT, 10, "bold"),
          bg=FELT_800, fg=VIOLET_300, anchor="w").pack(fill=X, pady=(0, 8))

    entry = Entry(inner, font=(BODY_FONT, 14), bg=IVORY_100, fg=INK_900, relief=FLAT,
                  insertbackground=INK_900, highlightthickness=0)
    entry.pack(fill=X, ipady=8)
    entry.focus()

    def submit():
        name = entry.get().strip()
        if name:
            player_names.append(name)
            win.destroy()
            player2_screen(root)
        else:
            messagebox.showerror(t("err_title"), t("err_no_name"))

    entry.bind("<Return>", lambda e: submit())

    flat_button(inner, t("btn_continue"), GOLD_500, INK_900, submit, font_size=12).pack(fill=X, pady=(20, 0))

def ai_setup_screen(root_win):
    root_win.withdraw()
    win = Toplevel()
    win.geometry("380x440")
    win.resizable(False, False)
    win.configure(bg=FELT_950)

    state = {"difficulty": "cautious", "name_draft": "", "content": None}

    def render():
        win.title(t("win_title_ai_setup"))
        old = state["content"]
        content = Frame(win, bg=FELT_800)

        inner = Frame(content, bg=FELT_800)
        inner.pack(fill=BOTH, expand=True, padx=34, pady=34)

        Label(inner, text=t("label_name_solo"), font=(MONO_FONT, 10, "bold"),
              bg=FELT_800, fg=VIOLET_300, anchor="w").pack(fill=X, pady=(0, 8))

        entry = Entry(inner, font=(BODY_FONT, 14), bg=IVORY_100, fg=INK_900, relief=FLAT,
                      insertbackground=INK_900, highlightthickness=0)
        entry.insert(0, state["name_draft"])
        entry.pack(fill=X, ipady=8, pady=(0, 22))
        entry.focus()

        Label(inner, text=t("ai_difficulty_label"), font=(MONO_FONT, 10, "bold"),
              bg=FELT_800, fg=VIOLET_300, anchor="w").pack(fill=X, pady=(0, 8))

        diff_row = Frame(inner, bg=FELT_800)
        diff_row.pack(anchor="w", pady=(0, 26))

        def set_difficulty(value):
            state["name_draft"] = entry.get()
            state["difficulty"] = value
            render()

        choice_chip(diff_row, t("ai_difficulty_cautious"), state["difficulty"] == "cautious",
                    lambda: set_difficulty("cautious")).pack(side=LEFT, padx=(0, 10))
        choice_chip(diff_row, t("ai_difficulty_aggressive"), state["difficulty"] == "aggressive",
                    lambda: set_difficulty("aggressive")).pack(side=LEFT)

        def submit():
            name = entry.get().strip()
            if name:
                win.destroy()
                start_game_vs_ai(name, state["difficulty"])
            else:
                messagebox.showerror(t("err_title"), t("err_no_name"))

        entry.bind("<Return>", lambda e: submit())

        flat_button(inner, t("btn_start_game"), GOLD_500, INK_900, submit, font_size=12).pack(fill=X)

        content.place(x=0, y=0, relwidth=1, relheight=1)
        if old is not None:
            old.destroy()
        state["content"] = content

    render()

def settings_screen(root_win):
    root_win.withdraw()
    win = Toplevel()
    win.geometry("430x600")
    win.resizable(False, False)
    win.configure(bg=FELT_950)

    state = {"content": None}

    def render():
        win.title(t("settings_title"))
        old = state["content"]
        content = Frame(win, bg=FELT_800)

        inner = Frame(content, bg=FELT_800)
        inner.pack(fill=BOTH, expand=True, padx=34, pady=28)

        Label(inner, text=t("settings_title"), font=(DISPLAY_FONT, 20, "bold"),
              bg=FELT_800, fg=GOLD_300).pack(anchor="w", pady=(0, 20))

        Label(inner, text=t("settings_target"), font=(MONO_FONT, 10, "bold"),
              bg=FELT_800, fg=VIOLET_300, anchor="w").pack(fill=X)
        target_entry = Entry(inner, font=(BODY_FONT, 13), bg=IVORY_100, fg=INK_900,
                              relief=FLAT, insertbackground=INK_900, highlightthickness=0)
        target_entry.insert(0, str(settings["target_score"]))
        target_entry.pack(fill=X, ipady=6, pady=(4, 16))

        Label(inner, text=t("settings_bank_min"), font=(MONO_FONT, 10, "bold"),
              bg=FELT_800, fg=VIOLET_300, anchor="w").pack(fill=X)
        bank_entry = Entry(inner, font=(BODY_FONT, 13), bg=IVORY_100, fg=INK_900,
                            relief=FLAT, insertbackground=INK_900, highlightthickness=0)
        bank_entry.insert(0, str(settings["bank_minimum"]))
        bank_entry.pack(fill=X, ipady=6, pady=(4, 16))

        Label(inner, text=t("settings_resolution"), font=(MONO_FONT, 10, "bold"),
              bg=FELT_800, fg=VIOLET_300, anchor="w").pack(fill=X)
        res_var = StringVar(value=settings["resolution"])
        res_menu = OptionMenu(inner, res_var, *RESOLUTIONS)
        res_menu.configure(font=(BODY_FONT, 11), bg=IVORY_100, fg=INK_900, activebackground=IVORY_300,
                            relief=FLAT, bd=0, highlightthickness=0, anchor="w")
        res_menu["menu"].configure(font=(BODY_FONT, 11), bg=IVORY_100, fg=INK_900)
        res_menu.pack(fill=X, pady=(4, 16), ipady=5)

        Label(inner, text=t("settings_language"), font=(MONO_FONT, 10, "bold"),
              bg=FELT_800, fg=VIOLET_300, anchor="w").pack(fill=X, pady=(0, 8))
        lang_row = Frame(inner, bg=FELT_800)
        lang_row.pack(anchor="w", pady=(0, 24))
        language_button(lang_row, "cs", draw_flag_cz, "lang_cs", render).pack(side=LEFT, padx=(0, 12))
        language_button(lang_row, "en", draw_flag_en, "lang_en", render).pack(side=LEFT, padx=(0, 12))
        language_button(lang_row, "he", draw_flag_il, "lang_he", render).pack(side=LEFT)

        btn_row = Frame(inner, bg=FELT_800)
        btn_row.pack(fill=X)

        def save():
            try:
                target = int(target_entry.get().strip())
                bank_min = int(bank_entry.get().strip())
                if target <= 0 or bank_min <= 0 or bank_min > target:
                    raise ValueError
            except ValueError:
                messagebox.showerror(t("err_title"), t("err_invalid_number"))
                return
            settings["target_score"] = target
            settings["bank_minimum"] = bank_min
            settings["resolution"] = res_var.get()
            win.destroy()
            root_win.deiconify()
            render_main_menu()

        def back():
            win.destroy()
            root_win.deiconify()

        flat_button(btn_row, t("btn_save"), GOLD_500, INK_900, save, font_size=11).pack(side=LEFT, padx=(0, 10))
        flat_button(btn_row, t("btn_back"), VIOLET_500, IVORY_100, back, font_size=11).pack(side=LEFT)

        content.place(x=0, y=0, relwidth=1, relheight=1)
        if old is not None:
            old.destroy()
        state["content"] = content

    render()

def render_main_menu():
    global root
    root.title(t("app_title"))

    old_content = getattr(root, "content_frame", None)
    body = Frame(root, bg=FELT_800)

    inner = Frame(body, bg=FELT_800)
    inner.pack(expand=True)

    Label(inner, text=t("brand"), font=(DISPLAY_FONT, 46, "bold"), bg=FELT_800, fg=GOLD_300).pack(pady=(36, 8))
    Frame(inner, bg=VIOLET_500, height=2, width=60).pack(pady=(0, 16))

    Label(inner, text=t("menu_tagline"), font=(BODY_FONT, 12), bg=FELT_800, fg=IVORY_100,
          justify=CENTER, wraplength=340).pack(pady=(0, 10))
    Label(inner, text=t("menu_rules_short"), font=(MONO_FONT, 9), bg=FELT_800, fg=IVORY_300,
          justify=CENTER, wraplength=360).pack(pady=(0, 14))
    Label(inner, text=t("menu_goal", target=f"{settings['target_score']:,}"), font=(MONO_FONT, 12, "bold"),
          bg=FELT_800, fg=GOLD_300, justify=CENTER).pack(pady=(0, 30))

    flat_button(inner, t("btn_pvp"), GOLD_500, INK_900, lambda: player1_screen(root), font_size=13).pack(pady=(0, 10))
    flat_button(inner, t("btn_pva"), IVORY_100, INK_900, lambda: ai_setup_screen(root), font_size=13).pack(pady=(0, 10))
    flat_button(inner, t("btn_settings"), VIOLET_500, IVORY_100, lambda: settings_screen(root), font_size=11).pack()

    body.place(x=0, y=0, relwidth=1, relheight=1)
    if old_content is not None:
        old_content.destroy()
    root.content_frame = body

def main_menu():
    global player_names, root
    player_names = []

    root = Tk()
    root.geometry("460x520")
    root.resizable(False, False)
    root.configure(bg=FELT_950)

    render_main_menu()

    root.mainloop()


if __name__ == "__main__":
    main_menu()
