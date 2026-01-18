from tkinter import *
from tkinter import messagebox
from random import *
from random import randint, choice
from player import Player
from dice import Dice
from game import FarkleGame


game = None
game_window = None
player_names = []

def show_game_screen():
    global game_window
    try:
        game_window.destroy()
    except:
        pass
    
    game_window = Toplevel()
    game_window.title(f"{game.current_player.name} - Farkle se SCHOPNOSTMI")
    game_window.geometry("1000x700")
    game_window.resizable(False, False)
    
    top_frame = Frame(game_window, bg="navy", height=60)
    top_frame.pack(fill=X)
    top_frame.pack_propagate(False)
    
    opponent = game.head_player if game.current_player == game.tail_player else game.tail_player
    Label(top_frame, text=f"{game.current_player.name}: {game.current_player.total_score:,}", 
          font=("Arial", 16, "bold"), bg="navy", fg="yellow").pack(side=LEFT, padx=20, pady=10)
    Label(top_frame, text=f"{opponent.name}: {opponent.total_score:,}", 
          font=("Arial", 16, "bold"), bg="navy", fg="white").pack(side=RIGHT, padx=20, pady=10)
    
    ability = game.current_player.get_active_ability()
    ability_status = f"SCHOPNOST: {ability.upper()}"
    if ability in game.current_player.abilities_used:
        ability_status += " (použito)"
    elif game.current_player.turn_count % 5 == 0:
        ability_status += " (NOVÁ!)"
    
    Label(top_frame, text=ability_status, font=("Arial", 12, "bold"), 
          bg="navy", fg="white").pack()
    Label(top_frame, text=f"Tahy: {game.current_player.turn_count}", 
          font=("Arial", 12), bg="navy", fg="white").pack()
    
    center_frame = Frame(game_window)
    center_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

    score_frame = Frame(center_frame, bg="#e0e0e0", relief="ridge", bd=2)
    score_frame.pack(side=LEFT, fill=Y, padx=(0, 20))

    current_score, combos = game.current_player.calculate_score()
    score_text = f"Aktuální hod: {current_score:,} bodů\n\n"
    if combos:
        score_text += "Kombinace:\n" + "\n".join(f"• {c}" for c in combos)
    else:
        score_text += "ŽÁDNÉ BODOVACÍ KOSTKY!"
    
    score_text += f"\n\nKolo: {game.current_player.round_score:,}"
    score_text += f"\nCelkem: {game.current_player.total_score:,}"
    score_text += f"\nCíl: 10 000"

    Label(score_frame, text=score_text, font=("Consolas", 12), 
          bg="white", justify=LEFT, padx=15, pady=15).pack(pady=10)

    dice_frame = Frame(center_frame, bg="white", relief="ridge", bd=2)
    dice_frame.pack(side=RIGHT, fill=BOTH, expand=True)

    Label(dice_frame, text="KOSTKY (klikni pro výběr)", 
          font=("Arial", 14, "bold"), bg="white").pack(pady=10)

    dice_grid = Frame(dice_frame)
    dice_grid.pack(pady=20)

    for i in range(6):
        die = game.current_player.dice[i]
        if not die.kept:
            color = "orange" if die.selected else "lightblue"
            status = "VYBRÁNO" if die.selected else "AKTIVNÍ"
            
            btn = Button(dice_grid, text=f"{status}\n\n{die.get_display()}", 
                        font=("Courier", 14, "bold"),
                        width=10, height=4, bg=color, fg="black",
                        command=lambda idx=i: select_die(idx))
            btn.grid(row=i//3, column=i%3, padx=8, pady=8)

    btn_frame = Frame(game_window, bg="#c0c0c0", height=80)
    btn_frame.pack(fill=X, pady=10)
    btn_frame.pack_propagate(False)

    active_count = game.current_player.get_active_count()
    selected_count = sum(1 for d in game.current_player.dice if d.selected)
    has_score = game.current_player.has_scoring_dice()

    if active_count == 0:
        Label(btn_frame, text="Hráč musí házet znovu", 
              font=("Arial", 12, "bold"), bg="yellow", fg="green").pack(pady=10)
    elif not has_score:
        Label(btn_frame, text="Žádné bodovací kostky", 
              font=("Arial", 12, "bold"), bg="yellow", fg="red").pack(pady=10)
    else:
        Label(btn_frame, text=f"Vybráno {selected_count} kostek", 
              font=("Arial", 12, "bold"), bg="lightblue").pack(pady=10)

    action_frame = Frame(btn_frame, bg="#c0c0c0")
    action_frame.pack(pady=10)

    if has_score and selected_count > 0:
        Button(action_frame, text="ODLOŽ VYBRANÉ", font=("Arial", 12, "bold"),
               command=keep_dice, bg="green", fg="white", width=15, height=2).pack(side=LEFT, padx=10)

    Button(action_frame, text="HAZEJ", font=("Arial", 12, "bold"),
           command=roll_dice_action, bg="blue", fg="white", width=15, height=2).pack(side=LEFT, padx=10)

    Button(action_frame, text="BANK (Uložit)", font=("Arial", 12, "bold"),
           command=bank_points_action, bg="orange", fg="white", width=15, height=2).pack(side=LEFT, padx=10)

    if not has_score:
        Button(action_frame, text="DALŠÍ HRÁČ", font=("Arial", 12, "bold"),
               command=next_player, bg="red", fg="white", width=15, height=2).pack(side=LEFT, padx=10)

    game_window.wait_window()

def select_die(index):
    if index < 6 and not game.current_player.dice[index].kept:
        game.current_player.dice[index].selected = not game.current_player.dice[index].selected
        show_game_screen()

def roll_dice_action():
    """VŽDY hází 6 kostek na začátku tahu, pak jen aktivní"""
    active_count = game.current_player.get_active_count()
    
    if active_count == 0:
        game.current_player.roll_dice(6)
    else:
        game.current_player.roll_dice(active_count)
    
    show_game_screen()

def keep_dice():
    score, _ = game.current_player.calculate_score()
    if score > 0:
        game.current_player.round_score += score
    game.current_player.keep_selected()
    roll_dice_action()

def bank_points_action():
    if game.current_player.round_score > 0:
        opponent = game.head_player if game.current_player == game.tail_player else game.tail_player
        banked = game.current_player.bank_points(opponent)
        messagebox.showinfo("BANK", f"Uloženo {banked:,} bodů!")
    
    if game.check_winner():
        messagebox.showinfo("VÍTĚZ!", f"{game.current_player.name} vyhrál!")
        root.quit()
    else:
        next_player()

def next_player():
    game.current_player.reset_round()
    game.switch_player()
    game.current_player.reset_round()
    show_game_screen()

def start_game():
    global game
    game = FarkleGame()
    p1 = Player(player_names[0])
    p2 = Player(player_names[1])
    game.start_game(p1, p2)
    show_game_screen()

def player2_screen(root):
    root.withdraw()
    win = Toplevel()
    win.title("Hráč 2")
    win.geometry("400x300")
    
    Label(win, text="Jméno hráče 2:", font=("Arial", 18, "bold"), 
          bg="lightblue").pack(pady=30)
    
    entry = Entry(win, font=("Arial", 16), width=20)
    entry.pack(pady=10)
    entry.focus()
    
    def submit():
        name = entry.get().strip()
        if name and name != player_names[0]:
            player_names.append(name)
            win.destroy()
            start_game()
        else:
            messagebox.showerror("Chyba", "Zadejte jiný název!")
    
    Button(win, text="START HRY", font=("Arial", 16, "bold"),
           command=submit, bg="green", fg="white").pack(pady=20)

def player1_screen(root):
    root.withdraw()
    win = Toplevel()
    win.title("Hráč 1")
    win.geometry("400x300")
    
    Label(win, text="Jméno hráče 1:", font=("Arial", 18, "bold"), 
          bg="lightgreen").pack(pady=30)
    
    entry = Entry(win, font=("Arial", 16), width=20)
    entry.pack(pady=10)
    entry.focus()
    
    def submit():
        name = entry.get().strip()
        if name:
            player_names.append(name)
            win.destroy()
            player2_screen(root)
        else:
            messagebox.showerror("Chyba", "Zadejte jméno!")
    
    Button(win, text="Pokračovat", font=("Arial", 16, "bold"),
           command=submit, bg="blue", fg="white").pack(pady=20)

def main_menu():
    global player_names, root
    player_names = []
    
    root = Tk()
    root.title("FARKLE se SCHOPNOSTMI KAŽDÝCH 5 TAHŮ")
    root.geometry("500x400")
    root.resizable(False, False)
    
    Label(root, text="FARKLE", font=("Arial", 36, "bold"), 
          fg="darkred", bg="lightyellow", pady=20).pack(pady=20)
    
    Label(root, text="Pravidla:\n1=100, 5=50, 3 stejné=300+\nNOVÁ SCHOPNOST každých 5 tahů!\nCíl: 10 000 bodů", 
          font=("Arial", 14), bg="lightyellow").pack(pady=20)
    
    Button(root, text="ZAČÍT HRU", font=("Arial", 20, "bold"),
           command=lambda: player1_screen(root),
           bg="#FF4500", fg="white", width=15, height=3).pack(pady=30)
    
    root.mainloop()

if __name__ == "__main__":
    main_menu()
