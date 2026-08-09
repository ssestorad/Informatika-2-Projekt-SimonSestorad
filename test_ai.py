import unittest

from dice import Dice
from ai import pick_scoring_dice_indices, should_bank
from player import Player


def dice_with_values(values, kept_indices=()):
    dice = [Dice() for _ in range(6)]
    for i, v in enumerate(values):
        dice[i].value = v
        if i in kept_indices:
            dice[i].kept = True
    return dice


class PickScoringDiceTests(unittest.TestCase):
    def test_six_of_a_kind_selects_all(self):
        dice = dice_with_values([4, 4, 4, 4, 4, 4])
        self.assertEqual(sorted(pick_scoring_dice_indices(dice)), [0, 1, 2, 3, 4, 5])

    def test_straight_selects_all(self):
        dice = dice_with_values([1, 2, 3, 4, 5, 6])
        self.assertEqual(sorted(pick_scoring_dice_indices(dice)), [0, 1, 2, 3, 4, 5])

    def test_three_pairs_selects_all(self):
        dice = dice_with_values([2, 2, 3, 3, 4, 4])
        self.assertEqual(sorted(pick_scoring_dice_indices(dice)), [0, 1, 2, 3, 4, 5])

    def test_triple_ignores_non_scoring_dice(self):
        dice = dice_with_values([1, 1, 1, 2, 2, 3])
        self.assertEqual(sorted(pick_scoring_dice_indices(dice)), [0, 1, 2])

    def test_triple_plus_single_five(self):
        dice = dice_with_values([2, 2, 2, 5, 3, 4])
        self.assertEqual(sorted(pick_scoring_dice_indices(dice)), [0, 1, 2, 3])

    def test_no_scoring_dice(self):
        dice = dice_with_values([2, 3, 4, 6, 2, 3])
        self.assertEqual(pick_scoring_dice_indices(dice), [])

    def test_kept_dice_are_ignored(self):
        dice = dice_with_values([1, 1, 1, 0, 0, 0], kept_indices=(0,))
        # kostka 0 uz je odlozena, zbyvaji jen dve jednicky - nebodujici trojice
        self.assertEqual(sorted(pick_scoring_dice_indices(dice)), [1, 2])


class ShouldBankTests(unittest.TestCase):
    def test_below_minimum_never_banks(self):
        p = Player("Test")
        p.round_score = 100
        p.total_score = 0
        self.assertFalse(should_bank(p, dice_remaining=1, bank_minimum=500, target_score=10000, profile_key="cautious"))

    def test_banks_when_it_would_win(self):
        p = Player("Test")
        p.round_score = 600
        p.total_score = 9500
        self.assertTrue(should_bank(p, dice_remaining=5, bank_minimum=500, target_score=10000, profile_key="cautious"))

    def test_cautious_banks_with_few_dice_left(self):
        p = Player("Test")
        p.round_score = 550
        p.total_score = 0
        self.assertTrue(should_bank(p, dice_remaining=3, bank_minimum=500, target_score=10000, profile_key="cautious"))

    def test_aggressive_keeps_rolling_with_few_dice_left(self):
        p = Player("Test")
        p.round_score = 550
        p.total_score = 0
        self.assertFalse(should_bank(p, dice_remaining=3, bank_minimum=500, target_score=10000, profile_key="aggressive"))

    def test_score_cap_forces_bank(self):
        p = Player("Test")
        p.round_score = 900
        p.total_score = 0
        self.assertTrue(should_bank(p, dice_remaining=5, bank_minimum=500, target_score=10000, profile_key="cautious"))


if __name__ == "__main__":
    unittest.main()
