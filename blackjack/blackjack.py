import cards
import curses
import datetime

# Global variables
delay = 100
min_bet = 10
max_bet = 1000
n_options = 5
option_list = []
window_dict = {}
game_log = ["" for x in range(5)]

# Classes
class Hand(list):
    def __init__(self):
        self.is_21 = False
        self.is_blackjack = False
        self.is_bust = False
        self.is_doublable = False
        self.is_doubled = False
        self.is_hittable = False
        self.is_insurable = False
        # self.is_insured = False
        self.is_split = False
        self.is_splittable = False
        self.is_standable = False
        self.is_winning = False
        self.is_push = False
        self.pay_factor = 0

    def get_total(self, first_card_hidden=False):
        total = 0
        for i in range(len(self)):
            if i == 0 and first_card_hidden:
                pass
            elif self[i].rank > 10:
                total += 10
            else:
                total += self[i].rank

        for i in range(len(self)):
            if i == 0 and first_card_hidden:
                pass
            elif self[i].rank == 1:
                total += 10
                if total > 21:
                    total -= 10
        return total

    def reset(self):
        self.__init__()

class Player(object):
    def __init__(self):
        self.name = ""
        self.hand = Hand()
        self.split_hand = Hand()
        self.starting_cash = 0
        self.cash = 0
        self.bet = 0
        self.insurance = 0
        self.is_insured = False
        self.can_claim = False
        self.is_dealer = False
        self.is_playing = True
        self.turn_active = False

# Functions
def init(screen):
    ROWS = curses.LINES
    COLS = curses.COLS
    MID_ROW = int(curses.LINES / 2)
    #                     WINDOW NAME (KEY),        SIZE, POS          COLOR, BORDER
    window_list = [ [        "dealer cards", 5, COLS - 3, 3, 2           , 0, False ],
                    [   "dealer hand total",        1, 4, 8, 2           , 0, False ],
                    [        "player cards", 5, COLS - 3, ROWS - 7, 2    , 0, False ],
                    [ "player hand total 1",        1, 4, ROWS - 8, 2    , 0, False ],
                    [ "player hand total 2",        1, 4, ROWS - 8, 10   , 0, False ],
                    [      "player details",       1, 55, ROWS - 2, 2    , 0, False ],
                    [                "deck",        6, 7, MID_ROW - 2, 2 , 0, False ],
                    [             "options",       6, 12, MID_ROW - 1, 11, 0, False ],
                    [                 "log",       7, 54, MID_ROW - 3, 24, 0, True  ]
                  ]
    
    # Init curses
    curses.curs_set(0)
    curses.use_default_colors()
    curses.init_pair(0, -1, -1)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_CYAN)

    # Init screen
    screen.clear()
    screen.attrset(curses.color_pair(0))

    for y in range(curses.LINES):
        for x in range(curses.COLS):
            screen.insstr(y, x, " ")
            
    title = "~ BlackJack ~"
    mid_y = int(curses.LINES / 2)
    mid_x = int(curses.COLS / 2)    
    screen.addstr(1, mid_x - int(len(title) / 2), title)
    screen.addstr(2, 2, "Dealer:")
    screen.addstr(mid_y - 2, 11, "OPTIONS:")

    screen.border()
    screen.noutrefresh()

    # Create windows
    for i in range(len(window_list)):
        window_dict[window_list[i][0]] = curses.newwin(window_list[i][1], window_list[i][2], window_list[i][3], window_list[i][4])
        window_dict[window_list[i][0]].attrset(curses.color_pair(window_list[i][5]))
        for y in range(window_list[i][1]):
            for x in range(window_list[i][2]):
                window_dict[window_list[i][0]].insstr(y, x, " ")
        if window_list[i][6]:
            window_dict[window_list[i][0]].border()
        window_dict[window_list[i][0]].noutrefresh()

# Game functions --------------------------------------------
def deal_card(deck, player, output=True):
    # to do: check for empty deck and shuffle discard_pile
    card = deck.pop()
    player.hand.append(card)
    if output: 
        if card.rank == 1:
            card_output = "an Ace"
        elif card.rank == 8:
            card_output = "an 8"
        elif card.rank == 11:
            card_output = "a Jack"
        elif card.rank == 12:
            card_output = "a Queen"
        elif card.rank == 13:
            card_output = "a King"
        else:
            card_output = "a %d" % card.rank
        log("%s draws %s" % (player.name, card_output))
    update_hand_windows(player)

def get_bet(player):
    message = "Enter bet amount (%d - %d): " % (min_bet, max_bet)
    mid_y = int(curses.LINES / 2)
    mid_x = int(curses.COLS / 2)
    y_size = 3
    x_size = len(message) + len(str(min_bet)) + (len(str(max_bet)) * 2) - 2
    y_pos = mid_y - 1
    x_pos = mid_x - int(x_size / 2)
    popup = curses.newwin(y_size, x_size, y_pos, x_pos)
    
    valid_input = False
    while not valid_input:
        error_msg = ""
        popup.clear()
        popup.border()
        popup.addstr(1, 2, message)
        curses.echo()
        input = popup.getstr(len(str(max_bet)))
        curses.noecho()
        try:
            input = int(input)
            if input == 0:
                popup.clear()
                popup.refresh()
                # log("You must place a bet to play!")
                print_log()
                return False
            elif input < min_bet or input > max_bet:
                error_msg = "Please bet between %d and %d" % (min_bet, max_bet)
                raise ValueError
            elif input > player.cash:
                error_msg = "You don't have that much cash!"
                raise ValueError
            else:
                valid_input = True
        except:
            if error_msg == "":
                error_msg = "Invalid input"
            popup.clear()
            popup.border()
            popup.addstr(1, int(x_size / 2) - int(len(error_msg) / 2), error_msg)
            popup.getkey()
    
    popup.clear()
    popup.refresh()
    player.cash -= input
    player.bet = input
    log("%s bets £%s" % (player.name, "{:,}".format(player.bet)))

    return True

def get_last_bet(player):
    if player.cash >= player.bet:
        player.cash -= player.bet
        log("%s bets £%s" % (player.name, "{:,}".format(player.bet)))
        return True
    else:
        log("You don't have enough cash!")
        return False

def get_max_bet(player):
    if player.cash >= max_bet:
        player.bet = max_bet
        player.cash -= player.bet
        log("%s places max bet of £%s!" % (player.name, "{:,}".format(max_bet)))
        return True
    else:
        player.bet = player.cash
        player.cash = 0
        log("%s goes all in with £%s!" % (player.name, "{:,}".format(player.bet)))
        return False

def assess_hand(player):
    hand = player.hand
    # 21
    if hand.get_total() == 21:
        hand.is_21 = True
    # blackjack
        if cards.count(hand) == 2 and \
           hand[0].rank >= 10 and hand[1].rank == 1 or \
           hand[1].rank >= 10 and hand[0].rank == 1:
            hand.is_blackjack = True
            log("%s has blackjack!" % player.name)
    # splittable
    if not player.is_dealer and cards.count(hand) == 2 and \
       hand[0].rank == hand[1].rank and not hand.is_split:
        hand.is_splittable = True
    # doublable
    if not player.is_dealer and not hand.is_21 and \
       cards.count(hand) == 2 and player.cash >= player.bet and \
       not hand.is_doubled:
        hand.is_doublable = True
    # hittable / standable
    if hand.get_total() < 21 and not hand.is_doubled:
        hand.is_hittable = True
        hand.is_standable = True
    else:
        hand.is_hittable = False
        hand.is_standable = False
    # bust
        if hand.get_total() > 21:
            hand.is_bust = True
            log("%s is bust!" % player.name)

def double_down(player):
    player.bet += player.bet
    player.cash -= player.bet
    player.hand.is_doubled = True
    player.hand.is_doublable = False
    log("%s doubles down" % player.name)

def buy_insurance(player):
    player.insurance = player.bet
    player.cash -= player.insurance
    player.is_insured = True
    log("%s buys £%s insurance" % (player.name, "{:,}".format(player.insurance)))

def claim_insurance(player):
    player.insurance *= 2
    player.cash += player.insurance 
    log("%s claims £%s insurance" % (player.name, "{:,}".format(player.insurance)))
    player.insurance = 0
    player.is_insured = False
    player.can_claim = False

def calc_outcome(player, dealer): # need insurance
    if dealer.hand.is_bust:
        if not player.hand.is_bust:
            player.hand.is_winning = True
            log_status = "wins"
            if player.hand.is_blackjack:
                player.hand.pay_factor = 2.5
                log_value = "blackjack"
            else:
                player.hand.pay_factor = 2
                log_value = str(player.hand.get_total())
        else:
            player.hand.is_winning = False
            log_status = "loses"
            log_value = str(player.hand.get_total())
    else:
        if not player.hand.is_bust:
            if player.hand.get_total() > dealer.hand.get_total():
                player.hand.is_winning = True
                log_status = "wins"
                if player.hand.is_blackjack:
                    player.hand.pay_factor = 2.5
                    log_value = "blackjack"
                else:
                    player.hand.pay_factor = 2
                    log_value = str(player.hand.get_total())
            elif player.hand.get_total() < dealer.hand.get_total():
                player.hand.is_winning = False
                log_status = "loses"
                log_value = str(player.hand.get_total())
            elif player.hand.get_total() == dealer.hand.get_total():
                player.hand.is_push = True
                player.hand.pay_factor = 1
                log_status = "pushes"
                log_value = str(player.hand.get_total())
        else:
            player.hand.is_winning = False
            log_status = "loses"
            log_value = str(player.hand.get_total())

        if dealer.hand.is_blackjack and player.is_insured:
            player.can_claim = True

    log("%s %s with %s" % (player.name, log_status, log_value ))

def payout(player):
    payout = player.bet * player.hand.pay_factor
    player.cash += payout
    log("Payout: £%s" % "{:,}".format(payout))

    if player.can_claim:
        claim_insurance(player)
    
    if player.hand.is_doubled:
        player.bet = int(player.bet / 2)

# Maintenance functions -------------------------------------
def update_hand_windows(player):
    hide_first_card = False
    if player.is_dealer:
        if not player.turn_active:
            hide_first_card = True
        window_cards = window_dict["dealer cards"]
        window_total = window_dict["dealer hand total"]
    else:
        window_cards = window_dict["player cards"]
        window_total = window_dict["player hand total 1"]
    
    print_hand(player.hand, window_cards, hide_first_card)
    print_hand_total(player.hand, window_total, hide_first_card)

    if not player.is_dealer and player.hand.is_split:
        print_hand_total(player.split_hand, window_dict["player hand total 2"])


def clear_window(window):
    window.clear()
    window.refresh()

def clear_card_windows():
    clear_window(window_dict["player cards"])
    clear_window(window_dict["player hand total 1"])
    clear_window(window_dict["player hand total 2"])
    clear_window(window_dict["dealer cards"])
    clear_window(window_dict["dealer hand total"])

def clear_options():
    global option_list
    option_list = [ "" for x in range(n_options) ]
    print_options()

def log(msg, log_time=True):
    if log_time:
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        time_stamp = "[%02d:%02d]" % (hour, minute)
    else:
        time_stamp = "       "
    msg = "%s %s" % (time_stamp, msg)

    for i in range(len(game_log)):
        if game_log[i] == "":
            game_log[i] = msg
            print_log()
            return 0
    
    for i in range(len(game_log) - 1):
        game_log[i] = game_log[i + 1]
    game_log[len(game_log) - 1] = msg
    
    print_log()

# Print functions -------------------------------------------
def print_card_base(window, y=0, x=0):
    window.addstr(y, x, "┌─────┐")
    for i in range(3): 
        window.addstr((y + 1) + i, x, "│     │")
    window.addstr(y + 4, x, "└─────┘")

def print_card_rear(window, y=0, x=0):
    window.attrset(curses.color_pair(7))
    print_card_base(window, y, x)

    window.addstr(y + 1, x + 1, "()_()")
    window.addstr(y + 2, x + 1, "(o.-)")
    window.addstr(y + 3, x + 2, "O-O")

def print_card(card, window, y=0, x=0):
    window.attrset(curses.color_pair(2))
    rank = cards.RANKS[card.rank][0]
    suit = cards.SUITS[card.suit][0]
    
    print_card_base(window, y, x)

    if card.suit == 2 or card.suit == 3:
        color = curses.color_pair(4)
    else:
        color = curses.color_pair(2)    
    
    window.addstr(y + 1, x + 1, rank, color)
    window.addstr(y + 2, x + 3, suit, color)

    if card.rank != 10:
        offset = 5
    else:
        offset = 4
    window.addstr(y + 3, x + offset, rank, color)

def print_deck(deck):
    window = window_dict["deck"]
    if cards.count(deck) > 0:
        print_card_rear(window)
    window.refresh()

def print_hand(hand, window, first_card_hidden=False):
    x = 0
    for i in range(len(hand)):
        if i == 0 and first_card_hidden:
            print_card_rear(window, 0, x)
        else:
            print_card(hand[i], window, 0, x)
        x += 3
    curses.delay_output(delay)
    window.refresh()

def print_hand_total(hand, window, first_card_hidden=False):
    window.clear()
    window.insstr(0, 0, "[%d]" % hand.get_total(first_card_hidden))
    window.refresh()

def print_player_details(player):
    window = window_dict["player details"]
    window.clear()
    cash = "{:,}".format(player.cash)
    bet = "{:,}".format(player.bet)
    window.addstr(0, 0, "%s - Bet: £%s (Cash: £%s)" % (player.name, bet, cash))
    window.refresh()

def print_options():
    window = window_dict["options"]
    window.clear()

    y = 0
    for option in option_list:
        if option != "":
            window.addstr(y, 0, option)
            y += 1

    window.refresh()

def print_exit_status(player):
    if player.starting_cash == player.cash:
        status = "broke even"
        amt = 0
    elif player.starting_cash < player.cash:
        status = "won"
        amt = player.cash - player.starting_cash
    else:
        status = "lost"
        amt = player.starting_cash - player.cash

    if amt > 0:
        exit_msg = status + " £{:,}".format(amt)
    else:
        exit_msg = status
    log("You %s!" % (exit_msg), False)

def print_log():
    window = window_dict["log"]
    window.erase()
    window.border()
    y = 1
    for i in range(len(game_log)):
        window.addstr(y, 1, game_log[i])
        y += 1
    window.refresh()

# Main function ----------------------------------------------
def main(stdscr):
    init(stdscr)

    n_players = 1
    game_over = False

    players = [ Player() for x in range(n_players) ]
    dealer = Player()
    dealer.is_dealer = True
    dealer.name = "Dealer"

    players[0].name = "Player 1"
    players[0].starting_cash = 100000
    players[0].cash = players[0].starting_cash
    # players[1].name = "Player 2"
    # players[1].starting_cash = 5000
    # players[1].cash = players[1].starting_cash

    deck = cards.Deck()
    cards.shuffle(deck)
    discard_pile = []

    # Tests --------------------------------------------------------- |

    # deck[51] = cards.Card(10, 1)    # player 1
    # deck[50] = cards.Card(8, 2)     # player 2
    # deck[49] = cards.Card(11, 3)    # dealer
    # deck[48] = cards.Card(5, 1)     # player 1
    # deck[47] = cards.Card(8, 2)     # player 2
    # deck[46] = cards.Card(1, 3)     # dealer

    # ----------------------------------------------------------------|

    while not game_over:

        round_over = False
        print_deck(deck)
        
        # Get bets
        for player in players:

            clear_options()
            
            if player.cash > 0:
                option_list[0] = "(B)et"
                if player.bet > 0:
                    option_list[0] = "(N)ew Bet"
                    option_list[1] = "(B)et Again"
                if player.bet != max_bet and player.bet != player.cash:
                    option_list[2] = "(M)ax Bet"
                option_list[3] = "(C)ash Out"
                print_options()

                print_player_details(player)
                log("%s, place a bet or cash out:" % player.name)
                log("(Table limits: £%s to £%s)" % ("{:,}".format(min_bet), "{:,}".format(max_bet)), False)

                valid_input = False
                while not valid_input:
                    input = stdscr.getkey()
                    if input == "B" or input == "b" and player.bet == 0:
                        valid_input = get_bet(player)
                    elif input == "N" or input == "n" and player.bet > 0:
                        valid_input = get_bet(player)
                    elif input == "B" or input == "b" and player.bet > 0:
                        valid_input = get_last_bet(player)
                    elif input == "M" or input == "m" and player.bet != max_bet:
                        valid_input = get_max_bet(player)
                    elif input == "C" or input == "c":
                        log("%s cashes out" % player.name)
                        print_exit_status(player)
                        player.is_playing = False
                        valid_input = True
                        stdscr.getkey()
            else:
                log("Thanks for playing, %s!" % player.name)
                print_exit_status(player)
                player.is_playing = False

        # End game if all cashed out
        playing_count = 0
        for player in players:
            if player.is_playing:
                playing_count += 1
        if playing_count == 0:
            game_over = True

        # Play round
        if not game_over:

            clear_card_windows()
            # Deal initial cards
            log("Dealing cards...")
            for i in range(2):
                for player in players:
                    deal_card(deck, player, False)
                    print_player_details(player)
                deal_card(deck, dealer, False)
            
            if dealer.hand[1].rank == 1:
                dealer.hand.is_insurable = True
    
            while not round_over:

                for player in players:
                    
                    print_player_details(player)
                    update_hand_windows(player)
                    player.turn_active = True
                    log("Waiting on %s" % player.name)

                    while player.turn_active:

                        assess_hand(player)

                        clear_options()
                        if player.hand.is_hittable:
                            option_list[0] = "(H)it"
                            option_list[1] = "(S)tand"
                            if player.hand.is_doublable:
                                option_list[2] = "(D)ouble"
                            if player.hand.is_splittable:
                                option_list[3] = "S(p)lit"
                            if dealer.hand.is_insurable and not player.is_insured and \
                               player.cash >= player.bet and cards.count(player.hand) == 2:
                                option_list[4] = "(I)nsurance"
                            print_options()

                            valid_input = False
                            while not valid_input:
                                input = stdscr.getkey()

                                if input == "H" or input == "h" and player.hand.is_hittable:
                                    deal_card(deck, player)
                                    valid_input = True
                                elif input == "S" or input == "s" and player.hand.is_standable:
                                    log("%s stands on %d" % (player.name, player.hand.get_total()))
                                    player.turn_active = False
                                    valid_input = True
                                elif input == "D" or input == "d" and player.hand.is_doublable:
                                    double_down(player)
                                    deal_card(deck, player)
                                    valid_input = True
                                elif input == "P" or input == "p" and player.hand.is_splittable:
                                    pass
                                elif input == "I" or input == "i" and dealer.hand.is_insurable and \
                                   not player.is_insured and player.cash >= player.bet:
                                    buy_insurance(player)
                                    valid_input = True
                        else:
                            if not player.hand.is_blackjack and not player.hand.is_bust:
                                log("%s has %d" % (player.name, player.hand.get_total()))
                            player.turn_active = False
                    
                dealer.turn_active = True
                update_hand_windows(dealer)

                while dealer.turn_active:

                    assess_hand(dealer)

                    if dealer.hand.get_total() < 17:
                        deal_card(deck, dealer)
                    else:
                        if not dealer.hand.is_blackjack and not dealer.hand.is_bust:
                            log("Dealer has %d" % dealer.hand.get_total())
                        dealer.turn_active = False

                round_over = True

            # Calculate outcome and payout bets
            for player in players:
                calc_outcome(player, dealer)
                payout(player)

            # Discard and reset hands
            for player in players:
                for i in range(cards.count(player.hand)):
                    discard_pile.append(player.hand.pop())
                player.hand.reset()
            for i in range(cards.count(dealer.hand)):
                discard_pile.append(dealer.hand.pop())
            dealer.hand.reset()


if __name__ == "__main__":
    curses.wrapper(main)
