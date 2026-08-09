import unittest

from player import Player


def score_of(values):
    """Vytvori hrace a nastavi hodnoty kostek podle `values` (chybejici kostky zustanou 0)."""
    player = Player("Test")
    for die, value in zip(player.dice, values):
        die.value = value
    return player.calculate_score()


class CalculateScoreTests(unittest.TestCase):
    def test_single_one(self):
        self.assertEqual(score_of([1]), (100, []))

    def test_single_five(self):
        self.assertEqual(score_of([5]), (50, []))

    def test_triple_two(self):
        self.assertEqual(score_of([2, 2, 2]), (200, ["3x 2: 200"]))

    def test_triple_three(self):
        self.assertEqual(score_of([3, 3, 3]), (300, ["3x 3: 300"]))

    def test_triple_four(self):
        self.assertEqual(score_of([4, 4, 4]), (400, ["3x 4: 400"]))

    def test_triple_five(self):
        self.assertEqual(score_of([5, 5, 5]), (500, ["3x 5: 500"]))

    def test_triple_six(self):
        self.assertEqual(score_of([6, 6, 6]), (600, ["3x 6: 600"]))

    def test_triple_one(self):
        self.assertEqual(score_of([1, 1, 1]), (1000, ["3x 1: 1000"]))

    def test_straight(self):
        self.assertEqual(score_of([1, 2, 3, 4, 5, 6]), (2000, ["Postupka: 2000"]))

    def test_six_of_a_kind(self):
        self.assertEqual(score_of([3, 3, 3, 3, 3, 3]), (5000, ["6 stejných: 5000"]))

    def test_three_pairs(self):
        self.assertEqual(score_of([2, 2, 3, 3, 4, 4]), (1000, ["3x dvojice: 1000"]))

    def test_four_of_a_kind_plus_pair_is_not_three_pairs(self):
        # Regrese: ctyri jednicky + dva dvojky driv chybne vysly jako "3x dvojice".
        score, combos = score_of([1, 1, 1, 1, 2, 2])
        self.assertEqual(score, 1100)
        self.assertEqual(combos, ["3x 1: 1000"])

    def test_farkle_no_score(self):
        self.assertEqual(score_of([2, 2, 3, 3, 4, 6]), (0, []))


if __name__ == "__main__":
    unittest.main()
