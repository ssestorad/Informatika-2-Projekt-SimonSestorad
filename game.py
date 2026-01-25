from tkinter import *
from random import *
from tkinter import messagebox
from random import choice

class FarkleGame:
    def __init__(self):
        self.head_player = None
        self.tail_player = None
        self.current_player = None
        self.target_score = 10000
    
    def start_game(self, p1, p2):
        self.head_player = p1
        self.tail_player = p2
        self.current_player = choice([self.head_player, self.tail_player])
        
        abilities = [
            "double", "sabotage", "steal", "fast_points", 
            "boost", "eraser", "mirror_shield", "insurance"
        ]
        
        p1.primary_ability = choice(abilities)
        p2.primary_ability = choice([a for a in abilities if a != p1.primary_ability])
        
        messagebox.showinfo("START HRY!",
            f"Začíná hráč: {self.current_player.name}\n\n"
            f"Primární schopnosti:\n"
            f"{p1.name}: {p1.primary_ability.upper()}\n"
            f"{p2.name}: {p2.primary_ability.upper()}\n\n"
            f"Cíl: {self.target_score} bodů.")
        
        self.current_player.new_turn()

    def switch_player(self):
        """Přepne hráče a kompletně zresetuje stůl pro nového hráče"""
        if self.current_player == self.head_player:
            self.current_player = self.tail_player
        else:
            self.current_player = self.head_player
            
        self.current_player.reset_round()
        
        self.current_player.new_turn()

    def get_opponent(self):
        return self.tail_player if self.current_player == self.head_player else self.head_player

    def check_winner(self):
        if self.head_player.total_score >= self.target_score:
            return self.head_player
        if self.tail_player.total_score >= self.target_score:
            return self.tail_player
        return None