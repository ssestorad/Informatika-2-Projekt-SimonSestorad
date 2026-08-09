from random import randint

class Dice:
    def __init__(self):
        self.value = 0
        self.kept = False
        self.selected = False

    def roll(self):
        if not self.kept:
            self.value = randint(1, 6)
            self.selected = False 
        return self.value

    def reset_full(self):
        self.value = 0
        self.kept = False
        self.selected = False

    def reset_selection(self):
        self.selected = False

    def get_display(self):
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
