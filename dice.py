from random import *
from random import randint

class Dice:
    def __init__(self):
        self.value = 0
        self.kept = False
        self.selected = False

    def roll(self):
        """
        Hází kostkou pouze pokud není 'kept'. 
        Selected se musí resetovat při každém hodu.
        """
        if not self.kept:
            self.value = randint(1, 6)
            self.selected = False 
        return self.value

    def reset_full(self):
        """Úplný reset kostky (používá se při Farkle nebo novém tahu)"""
        self.value = 0
        self.kept = False
        self.selected = False

    def reset_selection(self):
        """Pouze odznačí výběr (pokud hráč změní názor před hodem)"""
        self.selected = False

    def get_display(self):
        """Vrací vizuální reprezentaci kostky"""
        if self.value == 0:
            return "  ?  "
        
        displays = {
            1: "  ●  ",
            2: "●   ●",
            3: "● ● ●",
            4: "● ●\n● ●",
            5: "● ● ●\n● ●  ",
            6: "● ● ●\n● ● ●"
        }
        return displays.get(self.value, "  ?  ")
    
    def reset_full(self):
        self.value = 0
        self.kept = False
        self.selected = False
