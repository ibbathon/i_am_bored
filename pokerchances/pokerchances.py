"""
Calculates the percent chance of each type of hand.
"""

class Card:
    NUMS = [i for i in range(2,15)]
    SUITS = [i for i in range(4)]
    def __init__ (self, num, suit):
        self.num = num
        self.suit = suit

class Hand:
    HAND_DESCS = [
        "Royal Flush",
        "Straight Flush",
        "Four of a Kind",
        "Full House",
        "Flush",
        "Straight",
        "Three of a Kind",
        "Two Pair",
        "One Pair",
    ]

    def __init__ (self, cards):
        self.cards = cards
        self.sort_hand()

    def sort_hand():
        self.cards.sort(key=attrgetter('suit','num'))

    def best_set_index (self):
        """Returns the index corresponding to the best possible poker hand
        in this set of cards."""

class ChanceCalculator:
    def __init__ (self, num_players):
        self.num_players = num_players
        self.num_poker_hands = [0 for _ in range(len(Hand.HAND_DESCS))]

    def gather_counts (self):
        cards_in_deck = len(Card.NUMS)*len(Card.SUITS)
        num_cards_low = cards_in_deck//self.num_players
        num_cards_high = num_cards_low
        if num_cards_low * self.num_players != cards_in_deck:
            num_cards_high += 1

    def print_chances (self):
        pass

if __name__ == '__main__':
    num_players = int(input("Number of players: "))+1
    cc = ChanceCalculator(num_players)
    cc.gather_counts()
    cc.print_chances()
