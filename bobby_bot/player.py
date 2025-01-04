'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import math
import eval7

import random


class Player(Bot):
    '''
    A super-basic heads-up pokerbot with if-else logic and randomization.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.
        '''
        pass

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.
        '''
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.
        '''
        print(terminal_state.bounty_hits)

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        '''
        legal_actions = round_state.legal_actions()
        street = round_state.street
        my_pip = round_state.pips[active]   # chips contributed by me in this betting round
        opp_pip = round_state.pips[1-active]
        my_stack = round_state.stacks[active]
        opp_stack = round_state.stacks[1-active]
        bounty = round_state.bounties[active]
        continue_cost = opp_pip - my_pip

        # If raise is allowed, figure out min and max raise
        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()
            min_cost = min_raise - my_pip
            max_cost = max_raise - my_pip
        else:
            min_cost = None
            max_cost = None

        # 1) Preflop logic
        if street == 0:
            hand_rankings = {
    "AA": 1, "AKs": 2, "AQs": 2, "AJs": 3, "ATs": 5, "A9s": 8, "A8s": 10, "A7s": 13, "A6s": 14,
    "A5s": 12, "A4s": 14, "A3s": 14, "A2s": 17, "AKo": 5, "KK": 1, "KQs": 3, "KJs": 3, "KTs": 6,
    "K9s": 10, "K8s": 16, "K7s": 19, "K6s": 24, "K5s": 25, "K4s": 25, "K3s": 26, "K2s": 26,
    "AQo": 8, "KQo": 9, "QQ": 1, "QJs": 5, "QTs": 6, "Q9s": 10, "Q8s": 19, "Q7s": 26, "Q6s": 28,
    "Q5s": 29, "Q4s": 29, "Q3s": 30, "Q2s": 31, "AJo": 12, "KJo": 14, "QJo": 15, "JJ": 2, "JTs": 6,
    "J9s": 11, "J8s": 17, "J7s": 27, "J6s": 33, "J5s": 35, "J4s": 37, "J3s": 37, "J2s": 38,
    "ATo": 18, "KTo": 20, "QTo": 22, "JTo": 21, "TT": 4, "T9s": 10, "T8s": 16, "T7s": 25, "T6s": 31,
    "T5s": 40, "T4s": 40, "T3s": 41, "T2s": 41, "A9o": 32, "K9o": 35, "Q9o": 36, "J9o": 34,
    "T9o": 31, "99": 7, "98s": 17, "97s": 24, "96s": 29, "95s": 38, "94s": 47, "93s": 47,
    "92s": 49, "A8o": 39, "K8o": 50, "Q8o": 53, "J8o": 48, "T8o": 43, "98o": 42, "88": 9,
    "87s": 21, "86s": 27, "85s": 33, "84s": 40, "83s": 53, "82s": 54, "A7o": 45, "K7o": 57,
    "Q7o": 66, "J7o": 64, "T7o": 59, "97o": 55, "87o": 52, "77": 12, "76s": 25, "75s": 28,
    "74s": 37, "73s": 45, "72s": 56, "A6o": 51, "K6o": 60, "Q6o": 71, "J6o": 80, "T6o": 74,
    "96o": 68, "86o": 61, "76o": 57, "66": 16, "65s": 27, "64s": 29, "63s": 38, "62s": 49,
    "A5o": 44, "K5o": 63, "Q5o": 75, "J5o": 82, "T5o": 89, "95o": 83, "85o": 73, "75o": 65,
    "65o": 58, "55": 20, "54s": 28, "53s": 32, "52s": 39, "A4o": 46, "K4o": 67, "Q4o": 76,
    "J4o": 85, "T4o": 90, "94o": 95, "84o": 88, "74o": 78, "64o": 70, "54o": 62, "44": 23,
    "43s": 36, "42s": 41, "A3o": 49, "K3o": 67, "Q3o": 77, "J3o": 86, "T3o": 92, "93o": 96,
    "83o": 98, "73o": 93, "63o": 81, "53o": 72, "43o": 76, "33": 23, "32s": 46, "A2o": 54,
    "K2o": 69, "Q2o": 79, "J2o": 87, "T2o": 94, "92o": 97, "82o": 99, "72o": 100, "62o": 95,
    "52o": 84, "42o": 86, "32o": 91, "22": 24}
            # put our hand in a nice format (e.g. [Ac, Ks] -> AKo), make sure to keep track of rank ordering
            hand = round_state.hands[active]
            ordd = 'AKQJT98765432'
            hand = sorted(hand, key=lambda x: ordd.index(x[0]))
            hand_str = ''
            if hand[0][0] == hand[1][0]:
                hand_str = hand[0][0] + hand[1][0]
            elif hand[0][1] == hand[1][1]:
                hand_str = hand[0][0] + hand[1][0] + 's'
            else:
                hand_str = hand[0][0] + hand[1][0] + 'o'
            # get the rank of our hand
            strength = hand_rankings[hand_str]
            if hand_str[0] == bounty or hand_str[1] == bounty:
                strength /= 2
            
            # add a random factor to our decision (so we're not completely deterministic)
            rand_val = random.random()
            strength += (continue_cost/4)*random.random()

            # if we have a strong hand, we'll raise (most of the time, but not always)
            if RaiseAction in legal_actions:
                if rand_val < 1-math.sqrt(strength/100):
                    return RaiseAction(max(min_raise, min(max_raise, int(min_raise*math.sqrt(30)/math.sqrt(math.sqrt(strength))*(0.5+random.random())))))
                elif CheckAction in legal_actions:
                    return CheckAction()
                elif random.random() < math.sqrt(strength/100):
                    return FoldAction()
                else:
                    return CallAction()

        # 2) Postflop logic (streets 3,4,5)
        else:
            allcards = [eval7.Card(s) for s in round_state.deck[:street] + round_state.hands[active]]
            strength = eval7.evaluate(allcards)
            
            # make strength go to 0-100 scale
            strength = math.sqrt(math.sqrt((strength/100000000)*0.66))*100
            
            # add a random factor to our decision (so we're not completely deterministic)
            rand_val = random.random()
            strength -= (continue_cost/8)*random.random()

            strength = 100-strength
            print(strength)
            if RaiseAction in legal_actions:
                if rand_val < 1-math.sqrt(strength/100):
                    return RaiseAction(max(min_raise, min(max_raise, int(min_raise*30/math.sqrt(math.sqrt(strength))*(0.5+random.random())))))
                elif CheckAction in legal_actions:
                    return CheckAction()
                elif random.random() < math.sqrt(strength/100):
                    return FoldAction()
                else:
                    return CallAction()

if __name__ == '__main__':
    run_bot(Player(), parse_args())