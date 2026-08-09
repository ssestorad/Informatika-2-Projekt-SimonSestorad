from random import choice

class FarkleGame:
    def __init__(self):
        self.head_player = None
        self.tail_player = None
        self.current_player = None
        self.target_score = 10000
        self.events = []

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

        self.events.append(("game_start", {"player": self.current_player.name}))
        self.events.append(("primary_abilities", {
            "p1": p1.name, "a1_key": p1.primary_ability,
            "p2": p2.name, "a2_key": p2.primary_ability,
        }))
        self.events.append(("target", {"target": f"{self.target_score:,}"}))

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