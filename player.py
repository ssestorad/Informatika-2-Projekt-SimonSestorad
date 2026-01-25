from tkinter import *
from tkinter import messagebox
from random import *
from random import randint, choice
from collections import Counter
from dice import Dice

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
        if not active_values: 
            return 0, []

        counts = Counter(active_values)
        num_dice = len(active_values)
        score = 0
        combos = []

        for val, count in counts.items():
            if count == 6:
                return 5000, ["6 stejných: 5000"]

        if num_dice == 6 and len(counts) == 6:
            return 2000, ["Postupka: 2000"]

        pairs = 0
        for count in counts.values():
            pairs += count // 2
        if pairs == 3 and num_dice == 6:
            return 1000, ["3x dvojice: 1000"]

        temp_counts = dict(counts)
        for i in range(1, 7):
            if temp_counts.get(i, 0) >= 3:
                if i == 1:
                    points = 1000
                else:
                    points = i * 100
            
                score += points
                combos.append(f"3x {i}: {points}")
                temp_counts[i] -= 3

        if temp_counts.get(1, 0) > 0:
            p = temp_counts[1] * 100
            score += p
            combos.append(f"{temp_counts[1]}x 1: {p}")
        
        if temp_counts.get(5, 0) > 0:
            p = temp_counts[5] * 50
            score += p
            combos.append(f"{temp_counts[5]}x 5: {p}")

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