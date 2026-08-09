from tkinter import *
from tkinter import messagebox
from random import randint, choice
from player import Player
from game import FarkleGame

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

game = None
root = None
game_window = None
player_names = []
log_lines = []

def push_log(*messages):
    global log_lines
    log_lines.extend(m for m in messages if m)
    log_lines[:] = log_lines[-30:]

def drain_events(*sources):
    for source in sources:
        if source:
            push_log(*source)
            source.clear()

def flat_button(parent, text, bg, fg, command, font_size=11):
    return Button(parent, text=text, font=(BODY_FONT, font_size, "bold"), bg=bg, fg=fg,
                  activebackground=bg, activeforeground=fg, relief=FLAT, bd=0,
                  padx=26, pady=12, cursor="hand2", command=command)

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

def show_game_screen():
    global game_window, game
    if game_window is None:
        game_window = Toplevel()
        game_window.geometry("1100x900")
        game_window.resizable(False, False)
        game_window.configure(bg=FELT_950)

    game_window.title(f"{game.current_player.name} - Farkle se SCHOPNOSTMI")

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
    ability_text = f"SCHOPNOST: {ability.upper()}"
    if ability in game.current_player.abilities_used:
        ability_text += " (POUŽITO)"
    Label(hud_center, text=ability_text, font=(MONO_FONT, 10, "bold"),
          bg=VIOLET_300, fg=FELT_950, padx=12, pady=4).pack()
    Label(hud_center, text=f"TAH #{game.current_player.turn_count}", font=(MONO_FONT, 9),
          bg=FELT_950, fg=IVORY_300).pack(pady=(6, 0))

    score_block(pad, opponent, IVORY_300, VIOLET_500, "e").grid(row=0, column=2, sticky="e")

    Frame(content, bg=GOLD_500, height=2).pack(fill=X)

    # ---------- table area: ledger + dice pit ----------
    table_area = Frame(content, bg=FELT_800)
    table_area.pack(fill=BOTH, expand=True)

    ledger = Frame(table_area, bg=IVORY_100, width=260)
    ledger.pack(side=LEFT, fill=Y, padx=(26, 16), pady=22)
    ledger.pack_propagate(False)

    ledger_pad = Frame(ledger, bg=IVORY_100)
    ledger_pad.pack(fill=BOTH, expand=True, padx=20, pady=20)

    sel_score, sel_combos = game.current_player.calculate_score(only_selected=True)

    Label(ledger_pad, text="VYBRÁNO K ODLOŽENÍ", font=(MONO_FONT, 10, "bold"),
          bg=IVORY_100, fg=FELT_700, anchor="w").pack(fill=X)
    Label(ledger_pad, text=f"{sel_score} bodů", font=(DISPLAY_FONT, 22, "bold"),
          bg=IVORY_100, fg=INK_900, anchor="w").pack(fill=X, pady=(0, 6))
    for combo in sel_combos:
        Label(ledger_pad, text=f"✓ {combo}", font=(MONO_FONT, 11),
              bg=IVORY_100, fg=FELT_700, anchor="w").pack(fill=X)

    Frame(ledger_pad, bg=FELT_700, height=1).pack(fill=X, pady=16)

    Label(ledger_pad, text="NASBÍRÁNO V KOLE", font=(MONO_FONT, 10, "bold"),
          bg=IVORY_100, fg=FELT_700, anchor="w").pack(fill=X)
    Label(ledger_pad, text=f"{game.current_player.round_score} bodů", font=(DISPLAY_FONT, 22, "bold"),
          bg=IVORY_100, fg=INK_900, anchor="w").pack(fill=X)

    dice_pit = Frame(table_area, bg=FELT_700)
    dice_pit.pack(side=RIGHT, fill=BOTH, expand=True, padx=(0, 26), pady=22)

    dice_grid = Frame(dice_pit, bg=FELT_700)
    dice_grid.pack(expand=True)

    for i in range(6):
        die = game.current_player.dice[i]

        if die.kept:
            tile_bg, status, pip_color = IVORY_300, "ULOŽENO", INK_900
        elif die.selected:
            tile_bg, status, pip_color = IVORY_100, "VYBRÁNO", GOLD_500
        else:
            tile_bg, status, pip_color = IVORY_100, "AKTIVNÍ", INK_900

        border_color = GOLD_500 if die.selected else FELT_700

        wrapper = Frame(dice_grid, bg=border_color, padx=3, pady=3)
        wrapper.grid(row=i // 3, column=i % 3, padx=10, pady=10)

        canvas = Canvas(wrapper, width=110, height=110, highlightthickness=0)
        canvas.pack()
        draw_die(canvas, 110, die.value, pip_color, tile_bg)

        Label(wrapper, text=status, font=(MONO_FONT, 8, "bold"), bg=tile_bg, fg=FELT_700).pack(fill=X)

        if not die.kept and die.value > 0:
            canvas.configure(cursor="hand2")
            canvas.bind("<Button-1>", lambda e, idx=i: select_die(idx))

    # ---------- event log ----------
    log_strip = Frame(content, bg=INK_900, height=100)
    log_strip.pack(fill=X)
    log_strip.pack_propagate(False)

    log_pad = Frame(log_strip, bg=INK_900)
    log_pad.pack(fill=BOTH, expand=True, padx=26, pady=10)

    lines = log_lines[-4:] if log_lines else ["Hra začíná..."]
    for line in lines:
        if line.upper().startswith("FARKLE"):
            color = EMBER_500
        elif line.startswith(("Nová schopnost", "Začíná", "Primární", "Cíl:")):
            color = IVORY_300
        else:
            color = GOLD_300
        Label(log_pad, text=line, font=(MONO_FONT, 10), bg=INK_900, fg=color,
              anchor="w", justify=LEFT).pack(fill=X)

    # ---------- actions ----------
    action_row = Frame(content, bg=FELT_950)
    action_row.pack(fill=X)

    action_pad = Frame(action_row, bg=FELT_950)
    action_pad.pack(pady=18)

    flat_button(action_pad, "HÁZEJ", GOLD_500, INK_900, roll_dice_action).pack(side=LEFT, padx=8)

    if sel_score > 0:
        flat_button(action_pad, "POTVRĎ VÝBĚR", VIOLET_500, IVORY_100, keep_dice).pack(side=LEFT, padx=8)

    if game.current_player.round_score >= 500:
        flat_button(action_pad, "BANK", IVORY_100, INK_900, bank_points_action).pack(side=LEFT, padx=8)

    if old_content is not None:
        old_content.destroy()
    content.pack(fill=BOTH, expand=True)
    game_window.content_frame = content

def select_die(index):
    die = game.current_player.dice[index]
    if not die.kept and die.value > 0:
        die.selected = not die.selected
        show_game_screen()

def roll_dice_action():
    global game
    if any(d.selected for d in game.current_player.dice):
        push_log("⚠ Nejdřív potvrď výběr kostek!")
        show_game_screen()
        return

    success = game.current_player.roll_dice()

    if not success:
        ability = game.current_player.get_active_ability()
        if ability == "insurance" and ability not in game.current_player.abilities_used:
            saved_points = game.current_player.round_score
            if saved_points > 0:
                game.current_player.total_score += saved_points
                push_log(f"Pojistka aktivována! Farkle, ale {game.current_player.name} si nechává {saved_points} bodů.")
            else:
                push_log(f"Farkle! Pojistku {game.current_player.name} nezachránila, žádné body v kole.")
            game.current_player.abilities_used[ability] = True
            next_player()
        else:
            push_log(f"FARKLE! {game.current_player.name} ztrácí vše.")
            next_player()
    else:
        show_game_screen()

def keep_dice():
    global game
    points, is_hot = game.current_player.confirm_selection()
    if is_hot:
        push_log("Horké kostky! Házíš znovu všemi šesti!")
    show_game_screen()

def bank_points_action():
    global game, root
    opponent = game.get_opponent()
    banked = game.current_player.bank_points(opponent)

    push_log(f"{game.current_player.name} uložil {banked} bodů do banku.")
    drain_events(game.current_player.events)

    winner = game.check_winner()
    if winner:
        messagebox.showinfo("VÍTĚZ!", f"Gratulujeme! {winner.name} vyhrál!")
        root.destroy()
    else:
        next_player()

def next_player():
    global game
    game.switch_player()
    drain_events(game.current_player.events)
    for die in game.current_player.dice:
        die.reset_full()
    show_game_screen()

def start_game():
    global game, root
    game = FarkleGame()
    p1 = Player(player_names[0])
    p2 = Player(player_names[1])
    game.start_game(p1, p2)
    drain_events(game.events, p1.events, p2.events)
    show_game_screen()

def player2_screen(root_win):
    global player_names
    root_win.withdraw()
    win = Toplevel()
    win.title("Hráč 2")
    win.geometry("360x300")
    win.configure(bg=FELT_950)

    pad = Frame(win, bg=FELT_800)
    pad.pack(fill=BOTH, expand=True)

    inner = Frame(pad, bg=FELT_800)
    inner.pack(expand=True, fill=X, padx=34, pady=34)

    Label(inner, text="JMÉNO HRÁČE 2", font=(MONO_FONT, 10, "bold"),
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
            messagebox.showerror("Chyba", "Zadejte jiný název!")

    entry.bind("<Return>", lambda e: submit())

    flat_button(inner, "START HRY", GOLD_500, INK_900, submit, font_size=12).pack(fill=X, pady=(20, 0))

def player1_screen(root_win):
    global player_names
    root_win.withdraw()
    win = Toplevel()
    win.title("Hráč 1")
    win.geometry("360x300")
    win.configure(bg=FELT_950)

    pad = Frame(win, bg=FELT_800)
    pad.pack(fill=BOTH, expand=True)

    inner = Frame(pad, bg=FELT_800)
    inner.pack(expand=True, fill=X, padx=34, pady=34)

    Label(inner, text="JMÉNO HRÁČE 1", font=(MONO_FONT, 10, "bold"),
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
            messagebox.showerror("Chyba", "Zadejte jméno!")

    entry.bind("<Return>", lambda e: submit())

    flat_button(inner, "POKRAČOVAT", GOLD_500, INK_900, submit, font_size=12).pack(fill=X, pady=(20, 0))

def main_menu():
    global player_names, root
    player_names = []

    root = Tk()
    root.title("FARKLE se SCHOPNOSTMI KAŽDÝCH 5 TAHŮ")
    root.geometry("460x420")
    root.resizable(False, False)
    root.configure(bg=FELT_950)

    body = Frame(root, bg=FELT_800)
    body.pack(fill=BOTH, expand=True)

    inner = Frame(body, bg=FELT_800)
    inner.pack(expand=True)

    Label(inner, text="FARKLE", font=(DISPLAY_FONT, 46, "bold"), bg=FELT_800, fg=GOLD_300).pack(pady=(40, 8))
    Frame(inner, bg=VIOLET_500, height=2, width=60).pack(pady=(0, 18))
    Label(inner, text="1 = 100 · 5 = 50 · 3 stejné = 300+\nnová schopnost každých 5 tahů\ncíl: 10 000 bodů",
          font=(MONO_FONT, 11), bg=FELT_800, fg=IVORY_300, justify=CENTER).pack(pady=(0, 30))

    flat_button(inner, "ZAČÍT HRU", GOLD_500, INK_900, lambda: player1_screen(root), font_size=14).pack(pady=(0, 40))

    root.mainloop()


if __name__ == "__main__":
    main_menu()
