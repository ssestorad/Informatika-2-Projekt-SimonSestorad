import threading
import queue

try:
    import winsound
except ImportError:
    winsound = None

# Tony se prehravaji na jednom vyhrazenem vlakne z fronty, aby se nikdy
# nepřekryvaly a aby volani z Tkinter hlavniho vlakna nikdy neblokovalo UI
# (winsound.Beep je synchronni/blokujici volani).
_queue = queue.Queue()

SOUND_ROLL = [(700, 60)]
SOUND_FARKLE = [(420, 140), (280, 180)]
SOUND_BANK = [(760, 70), (1100, 110)]
SOUND_WIN = [(660, 90), (880, 90), (1046, 160)]
SOUND_ABILITY = [(950, 60), (1300, 70)]
SOUND_WARNING = [(320, 90)]


def _worker():
    while True:
        sequence = _queue.get()
        for freq, duration in sequence:
            try:
                winsound.Beep(freq, duration)
            except RuntimeError:
                pass


if winsound is not None:
    threading.Thread(target=_worker, daemon=True).start()


def play(sequence):
    if winsound is not None:
        _queue.put(sequence)


def play_roll():
    play(SOUND_ROLL)


def play_farkle():
    play(SOUND_FARKLE)


def play_bank():
    play(SOUND_BANK)


def play_win():
    play(SOUND_WIN)


def play_ability():
    play(SOUND_ABILITY)


def play_warning():
    play(SOUND_WARNING)
