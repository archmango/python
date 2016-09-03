import random

# Constants

N_RANKS = 13
N_SUITS = 4

RANKS = { 1 : ("A", "Ace"),
          2 : ("2", "Two"),
          3 : ("3", "Three"),
          4 : ("4", "Four"),
          5 : ("5", "Five"),
          6 : ("6", "Six"),
          7 : ("7", "Seven"),
          8 : ("8", "Eight"),
          9 : ("9", "Nine"),
          10 : ("10", "Ten"),
          11 : ("J", "Jack"),
          12 : ("Q", "Queen"),
          13 : ("K" "King")
        }

SUITS = { 1 : ("♣", "Clubs"),
          2 : ("♦", "Diamonds"),
          3 : ("♥", "Hearts"),
          4 : ("♠", "Spades")
        }

# Classes

class Card(object):
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

class Deck(list):
    def __init__(self, n_packs=1):
        for deck in range(n_packs):
            for suit in range(N_SUITS):
                for rank in range(N_RANKS):
                    self.append( Card(rank + 1, suit + 1) )

# Functions

def assert_list(lst):
    assert isinstance(lst, list), "List expected"

def count(cards):
    assert_list(cards)
    return len(cards)

def sort(cards):
    assert_list(cards)
    cards.sort(key=lambda card: (card.suit, card.rank))

def shuffle(cards):
    assert_list(cards)
    random.shuffle(cards)
