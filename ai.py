from collections import Counter

AI_PROFILES = {
    "cautious": {"dice_threshold": 3, "score_cap": 800},
    "aggressive": {"dice_threshold": 1, "score_cap": 2500},
}


def pick_scoring_dice_indices(dice):
    """Vrati indexy kostek, ktere AI odlozi z aktualniho hodu (vsechny bodujici)."""
    active = [(i, d.value) for i, d in enumerate(dice) if not d.kept and d.value > 0]
    if not active:
        return []

    values = [v for _, v in active]
    counts = Counter(values)

    if len(active) == 6 and len(counts) == 1:
        return [i for i, _ in active]

    if len(active) == 6 and len(counts) == 6:
        return [i for i, _ in active]

    pair_values = [val for val, c in counts.items() if c == 2]
    if len(active) == 6 and len(pair_values) == 3:
        return [i for i, _ in active]

    chosen = []
    remaining = dict(counts)

    for val in range(1, 7):
        if remaining.get(val, 0) >= 3:
            picked = 0
            for i, v in active:
                if v == val and i not in chosen and picked < 3:
                    chosen.append(i)
                    picked += 1
            remaining[val] -= 3

    for val in (1, 5):
        left = remaining.get(val, 0)
        if left > 0:
            picked = 0
            for i, v in active:
                if v == val and i not in chosen and picked < left:
                    chosen.append(i)
                    picked += 1

    return chosen


def should_bank(player, dice_remaining, bank_minimum, target_score, profile_key):
    profile = AI_PROFILES[profile_key]

    if player.round_score < bank_minimum:
        return False
    if player.total_score + player.round_score >= target_score:
        return True
    if dice_remaining <= profile["dice_threshold"]:
        return True
    if player.round_score >= profile["score_cap"]:
        return True
    return False
