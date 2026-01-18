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
