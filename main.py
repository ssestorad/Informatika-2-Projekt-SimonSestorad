from tkinter import *
from tkinter import messagebox
from random import *
from random import randint, choice

class Dice:
    def __init__(self):
        self.value = 0
        self.kept = False
        self.selected = False
    
    def roll(self):
        self.value = randint(1, 6)
        self.kept = False
        self.selected = False
        return self.value
    
    def reset(self):
        self.value = 0
        self.kept = False
        self.selected = False
    
    def get_display(self):
        displays = {
            1: "  ●  ",
            2: "●    ●",
            3: "● ● ●",
            4: "● ●\n● ●",
            5: "● ● ●\n  ●  ",
            6: "● ● ●\n● ● ●"
        }
        return displays.get(self.value, "  ?  ")

class Player:
    def __init__(self, name):
        self.name = name
        self.total_score = 0
        self.round_score = 0
        self.last_bank = 0

        self.primary_ability = None
        self.secondary_ability = None
        self.abilities_used = {}
        self.turn_count = 0
        self.dice = [Dice() for _ in range(6)]
    
    def new_turn(self):
        self.turn_count += 1
        if self.turn_count % 5 == 0:
            self.secondary_ability = choice(["double", "sabotage", "steal", "fast_points", "boost"])
            messagebox.showinfo("NOVÁ SCHOPNOST!", 
                f"{self.name}: {self.secondary_ability.upper()}!\n(Tah #{self.turn_count})")
    
    def get_active_ability(self):
        return self.secondary_ability or self.primary_ability
    
    def roll_dice(self, num_dice):
        """VŽDY hází přesně num_dice kostek"""
        active_count = 0
        for i in range(6):
            if not self.dice[i].kept and active_count < num_dice:
                self.dice[i].reset()
                self.dice[i].roll()
                active_count += 1
    
    def calculate_score(self):
        active_values = [d.value for d in self.dice if not d.kept and d.value > 0]
        if not active_values: return 0, []

        counts = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
        for val in active_values: counts[val] += 1

        score = 0; combos = []

        for i in range(1, 7):
            if counts[i] >= 3:
                sets = counts[i] // 3
                if i == 1:
                    points = sets * 1000
                    combos.append(f"3x1: {points}")
                else:
                    points = sets * i * 100
                    combos.append(f"{sets}x{i}: {points}")
                score += points
                counts[i] -= sets * 3

        ones = min(counts[1], 3)
        fives = min(counts[5], 3)

        if ones > 0:
            score += ones * 100
            combos.append(f"1ky: {ones}x100={ones*100}")
        if fives > 0:
            score += fives * 50
            combos.append(f"5ky: {fives}x50={fives*50}")

        return score, combos
    
    def has_scoring_dice(self):
        return self.calculate_score()[0] > 0
    
    def get_active_count(self):
        return sum(1 for d in self.dice if not d.kept and d.value > 0)
    
    def keep_selected(self):
        for die in self.dice:
            if die.selected:
                die.kept = True
                die.selected = False
    
    def bank_points(self, opponent):
        final_round = self.round_score
        
        ability = self.get_active_ability()
        if ability == "fast_points" and ability not in self.abilities_used:
            final_round += 500
            self.abilities_used[ability] = True
            messagebox.showinfo("Fast Points!", f"{self.name}: +500 bonus!")
        
        self.total_score += final_round
        self.last_bank = final_round
        self.round_score = 0
        
        if ability == "double" and ability not in self.abilities_used:
            self.total_score += final_round
            self.abilities_used[ability] = True
            messagebox.showinfo("Dvojnásobek!", f"{self.name}: BANK ×2!")
        elif ability == "boost" and ability not in self.abilities_used:
            boost = int(self.total_score * 0.1)
            self.total_score += boost
            self.abilities_used[ability] = True
            messagebox.showinfo("10% Boost!", f"{self.name}: +{boost} bodů!")
        elif ability == "sabotage" and ability not in self.abilities_used:
            penalty = opponent.last_bank // 2
            opponent.total_score = max(0, opponent.total_score - penalty)
            self.abilities_used[ability] = True
            messagebox.showinfo("Sabotáž!", f"{self.name} odebral {penalty} bodů!")
        elif ability == "steal" and ability not in self.abilities_used:
            stolen = opponent.last_bank // 3
            opponent.total_score = max(0, opponent.total_score - stolen)
            self.total_score += stolen
            self.abilities_used[ability] = True
            messagebox.showinfo("Krádež!", f"{self.name} ukradl {stolen} bodů!")
        
        return final_round
    
    def reset_round(self):
        for die in self.dice:
            die.reset()
        self.round_score = 0

class FarkleGame:
    def __init__(self):
        self.head_player = None
        self.tail_player = None
        self.current_player = None
        self.target_score = 10000
    
    def start_game(self, p1, p2):
        self.head_player = p1
        self.tail_player = p2
        self.current_player = p1
        
        abilities = ["double", "sabotage", "steal", "fast_points", "boost"]
        self.head_player.primary_ability = choice(abilities)
        self.tail_player.primary_ability = choice(abilities)
        while self.tail_player.primary_ability == self.head_player.primary_ability:
            self.tail_player.primary_ability = choice(abilities)
        
        messagebox.showinfo("Schopnosti přiřazeny!",
            f"{p1.name}: {p1.primary_ability.upper()}\n"
            f"{p2.name}: {p2.primary_ability.upper()}\n"
            f"NOVÁ SCHOPNOST každých 5 tahů!")
        
        self.current_player.reset_round()

    def switch_player(self):
        self.current_player = self.tail_player if self.current_player == self.head_player else self.head_player
        self.current_player.new_turn()

    def check_winner(self):
        return (self.head_player.total_score >= self.target_score or 
                self.tail_player.total_score >= self.target_score)

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
    game_window.title(f"{game.current_player.name} - Farkle s SCHOPNOSMĚ")
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
          bg="navy", fg="purple").pack()
    Label(top_frame, text=f"Tahy: {game.current_player.turn_count}", 
          font=("Arial", 10), bg="navy", fg="lightblue").pack()
    
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
        Label(btn_frame, text="BONUS! Hráč hází 6 kostkami znovu", 
              font=("Arial", 12, "bold"), bg="yellow", fg="green").pack(pady=10)
    elif not has_score:
        Label(btn_frame, text="BUST! Žádné bodovací kostky", 
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
    root.title("FARKLE - SCHOPNOSTI KAŽDÝCH 5 TAHŮ")
    root.geometry("500x400")
    root.resizable(False, False)
    
    Label(root, text="FARKLE", font=("Arial", 36, "bold"), 
          fg="darkred", bg="gold", pady=20).pack(pady=20)
    
    Label(root, text="Pravidla:\n1=100, 5=50, 3 stejné=300+\nNOVÁ SCHOPNOST každých 5 tahů!\nCíl: 10 000 bodů", 
          font=("Arial", 14), bg="lightyellow").pack(pady=20)
    
    Button(root, text="ZAČÍT HRU", font=("Arial", 20, "bold"),
           command=lambda: player1_screen(root),
           bg="#FF4500", fg="white", width=15, height=3).pack(pady=30)
    
    root.mainloop()

if __name__ == "__main__":
    main_menu()
