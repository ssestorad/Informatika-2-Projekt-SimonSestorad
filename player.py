from tkinter import *
from random import *
from dice import Dice
from collections import Counter
from tkinter import messagebox
from random import choice

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
        """Příprava na nový tah hráče"""
        self.turn_count += 1
        for d in self.dice:
            d.reset_full()

        if self.turn_count % 5 == 0:
            self.secondary_ability = choice(["double", "sabotage", "steal", "fast_points", "boost"])
            if self.secondary_ability in self.abilities_used:
                del self.abilities_used[self.secondary_ability]
            
            messagebox.showinfo("NOVÁ SCHOPNOST!", 
                f"{self.name}: {self.secondary_ability.upper()}!\n(Tah #{self.turn_count})")

    def roll_dice(self):
        """Hází pouze těmi kostkami, které nejsou odložené (kept)"""
        for d in self.dice:
            if not d.kept:
                d.roll()
        
        score, _ = self.calculate_score()
        if score == 0:
            self.round_score = 0
            return False
        return True

    def calculate_score(self, only_selected=False):
        """
        Vypočítá skóre. 
        Pokud only_selected=True, počítá jen ty, co hráč právě označil k odložení.
        """
        if only_selected:
            active_values = [d.value for d in self.dice if d.selected and not d.kept]
        else:
            active_values = [d.value for d in self.dice if not d.kept and d.value > 0]

        if not active_values: return 0, []

        counts = Counter(active_values)
        num_dice = len(active_values)
        score = 0
        combos = []

        for val, count in counts.items():
            if count == 6: return 5000, ["6 stejných: 5000"]

        if num_dice == 6 and len(counts) == 6: return 2000, ["Postupka: 2000"]

        pairs = sum(count // 2 for count in counts.values())
        if pairs == 3 and num_dice == 6: return 1000, ["3x dvojice: 1000"]

        temp_counts = dict(counts)
        for i in range(1, 7):
            if temp_counts.get(i, 0) >= 3:
                points = 1000 if i == 1 else i * 100
                score += points
                combos.append(f"3x {i}: {points}")
                temp_counts[i] -= 3

        score += temp_counts.get(1, 0) * 100
        score += temp_counts.get(5, 0) * 50
        
        return score, combos

    def confirm_selection(self):
        """
        Potvrdí vybrané kostky, přičte jejich body a zkontroluje 'Horké kostky'.
        Vrací (získané_body, horké_kostky_boolean)
        """
        points, _ = self.calculate_score(only_selected=True)
        
        if points == 0:
            return 0, False

        self.round_score += points
        
        for d in self.dice:
            if d.selected:
                d.kept = True
                d.selected = False
        
        is_hot = all(d.kept for d in self.dice)
        if is_hot:
            for d in self.dice:
                d.kept = False
                d.value = 0
        
        return points, is_hot

    def bank_points(self, opponent):
        """Uloží round_score do total_score a aplikuje schopnosti"""
        if self.round_score == 0: return 0
        
        final_gain = self.round_score
        ability = self.get_active_ability()

        if ability == "fast_points" and ability not in self.abilities_used:
            final_gain += 500
            self.abilities_used[ability] = True

        self.total_score += final_gain
        
        if ability == "double" and ability not in self.abilities_used:
            self.total_score += final_gain
            self.abilities_used[ability] = True
        elif ability == "boost" and ability not in self.abilities_used:
            boost = int(self.total_score * 0.1)
            self.total_score += boost
            self.abilities_used[ability] = True
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

        self.last_bank = final_gain
        self.round_score = 0
        return final_gain

    def get_active_ability(self):
        return self.secondary_ability or self.primary_ability

    def reset_round(self):
        """Resetuje kostky a body za aktuální kolo (tah)"""
        for d in self.dice:
            d.reset_full()
        self.round_score = 0

    def get_active_count(self):
        """Vrací počet kostek, které nejsou odložené (kept)"""
        return sum(1 for d in self.dice if not d.kept)