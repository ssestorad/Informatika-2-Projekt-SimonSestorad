from tkinter import *
from tkinter import messagebox
from random import *
from random import randint, choice

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