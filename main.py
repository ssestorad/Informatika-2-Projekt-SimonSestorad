from tkinter import *
from tkinter import messagebox
from random import *
from random import randint, choice
from player import Player
from dice import Dice
from game import FarkleGame

game = None
root = None
game_window = None
player_names = []

def show_game_screen():
    global game_window, game
    if game_window:
        game_window.destroy()
    
    game_window = Toplevel()
    game_window.title(f"{game.current_player.name} - Farkle se SCHOPNOSTMI")
    game_window.geometry("1100x750")
    game_window.resizable(False, False)
    
    top_frame = Frame(game_window, bg="navy", height=70)
    top_frame.pack(fill=X)
    top_frame.pack_propagate(False)
    
    opponent = game.get_opponent()
    Label(top_frame, text=f"{game.current_player.name}: {game.current_player.total_score:,}", 
          font=("Arial", 16, "bold"), bg="navy", fg="yellow").pack(side=LEFT, padx=20)
    Label(top_frame, text=f"{opponent.name}: {opponent.total_score:,}", 
          font=("Arial", 16, "bold"), bg="navy", fg="white").pack(side=RIGHT, padx=20)
    
    ability = game.current_player.get_active_ability()
    ability_status = f"SCHOPNOST: {ability.upper()}"
    if ability in game.current_player.abilities_used:
        ability_status += " (použito)"
    
    Label(top_frame, text=ability_status, font=("Arial", 12, "bold"), bg="navy", fg="cyan").pack()
    Label(top_frame, text=f"Tah: {game.current_player.turn_count}", font=("Arial", 10), bg="navy", fg="white").pack()

    center_frame = Frame(game_window)
    center_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

    score_frame = Frame(center_frame, bg="#f0f0f0", relief="ridge", bd=2, width=300)
    score_frame.pack(side=LEFT, fill=Y, padx=(0, 20))
    score_frame.pack_propagate(False)

    sel_score, sel_combos = game.current_player.calculate_score(only_selected=True)
    
    score_text = f"VYBRÁNO K ODLOŽENÍ:\n{sel_score} bodů\n\n"
    if sel_combos:
        score_text += "\n".join(f"✓ {c}" for c in sel_combos)
    
    score_text += f"\n\n------------------\nNASBÍRÁNO V KOLE:\n{game.current_player.round_score} bodů"

    Label(score_frame, text=score_text, font=("Consolas", 11), bg="white", 
          justify=LEFT, anchor="nw", padx=10, pady=10).pack(fill=BOTH, expand=True)

    dice_frame = Frame(center_frame, bg="white", relief="ridge", bd=2)
    dice_frame.pack(side=RIGHT, fill=BOTH, expand=True)

    dice_grid = Frame(dice_frame, bg="white")
    dice_grid.pack(pady=40)

    for i in range(6):
        die = game.current_player.dice[i]
        
        if die.kept:
            color, status, state = "#d3d3d3", "ULOŽENO", DISABLED
        elif die.selected:
            color, status, state = "orange", "VYBRÁNO", NORMAL
        else:
            color, status, state = "lightblue", "AKTIVNÍ", NORMAL
            
        btn = Button(dice_grid, text=f"{status}\n\n{die.get_display()}", 
                    font=("Courier", 14, "bold"), width=12, height=5,
                    bg=color, state=state, command=lambda idx=i: select_die(idx))
        btn.grid(row=i//3, column=i%3, padx=10, pady=10)

    btn_frame = Frame(game_window, bg="#c0c0c0", height=100)
    btn_frame.pack(fill=X)
    
    action_frame = Frame(btn_frame, bg="#c0c0c0")
    action_frame.pack(pady=20)

    Button(action_frame, text="HÁZEJ", font=("Arial", 12, "bold"), bg="blue", fg="white",
           width=15, height=2, command=roll_dice_action).pack(side=LEFT, padx=10)

    if sel_score > 0:
        Button(action_frame, text="POTVRĎ VÝBĚR", font=("Arial", 12, "bold"), bg="green", fg="white",
               width=15, height=2, command=keep_dice).pack(side=LEFT, padx=10)

    if game.current_player.round_score >= 750 or (game.current_player.round_score > 0 and any(d.kept for d in game.current_player.dice)):
        Button(action_frame, text="BANK", font=("Arial", 12, "bold"), bg="orange", fg="white",
               width=15, height=2, command=bank_points_action).pack(side=LEFT, padx=10)

def select_die(index):
    die = game.current_player.dice[index]
    if not die.kept and die.value > 0:
        die.selected = not die.selected
        show_game_screen()

def roll_dice_action():
    global game
    
    if any(d.selected for d in game.current_player.dice):
        messagebox.showwarning("Pozor", "Nejdříve potvrď výběr kostek!")
        return

    success = game.current_player.roll_dice()
    
    if not success:
        messagebox.showerror("FARKLE!", f"Smůla! {game.current_player.name} nehodil nic a ztrácí body z tohoto kola.")
        game.current_player.round_score = 0
        next_player()
    else:
        show_game_screen()

def keep_dice():
    global game
    points, is_hot = game.current_player.confirm_selection()
    if is_hot:
        messagebox.showinfo("HORKÉ KOSTKY!", "Házíš znovu všemi šesti!")
    show_game_screen()

def bank_points_action():
    global game, root
    opponent = game.get_opponent()
    banked = game.current_player.bank_points(opponent)
    
    messagebox.showinfo("BANK", f"Hráč {game.current_player.name} uložil {banked} bodů.")
    
    winner = game.check_winner()
    if winner:
        messagebox.showinfo("VÍTĚZ!", f"Gratulujeme! {winner.name} vyhrál!")
        root.destroy()
    else:
        next_player()

def next_player():
    global game
    game.switch_player()
    for die in game.current_player.dice:
        die.reset_full()
    show_game_screen()

def start_game():
    global game, root
    game = FarkleGame()
    p1 = Player(player_names[0])
    p2 = Player(player_names[1])
    game.start_game(p1, p2)
    show_game_screen()

def player2_screen(root_win):
    global player_names
    root_win.withdraw()
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

def player1_screen(root_win):
    global player_names
    root_win.withdraw()
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