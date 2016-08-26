N_SUITS = 4
N_RANKS = 13
N_CARDS = N_SUITS * N_RANKS

class Card(object):
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank