from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
from typing import NewType, List

''' Game Reference
my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
my_cards = round_state.hands[active]  # your cards
big_blind = bool(active)  # True if you are the big blind
my_bounty = round_state.bounties[active]  # your current bounty rank

my_delta = terminal_state.deltas[active]  # your bankroll change from this round
previous_state = terminal_state.previous_state  # RoundState before payoffs
street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
my_cards = previous_state.hands[active]  # your cards
opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed

my_bounty_hit = terminal_state.bounty_hits[active]  # True if you hit bounty
opponent_bounty_hit = terminal_state.bounty_hits[1-active] # True if opponent hit bounty
bounty_rank = previous_state.bounties[active]  # your bounty rank

# The following is a demonstration of accessing illegal information (will not work)
opponent_bounty_rank = previous_state.bounties[1-active]  # attempting to grab opponent's bounty rank
'''
DISCRETE_ACTIONS = ["k", "bMIN", "bMID", "bMAX", "c", "f"]

Action = NewType("Action", str)

class PreflopHistory():

    def __init__(self, history: List[Action] = [], sample_id = 0):
        self.history = history
        self.sample_id = sample_id

    def is_terminal(self):
        num_round = len(self.history)
        street = len(self.history[-1])

        return num_round > 0 and street == 10

    def player(self):
        """
        1. ['AkTh', 'QdKd', 'bMID', 'c', '/', 'Qh2d3s4h5s']
        """
        if len(self.history) < 2:
            return -1
        elif self._game_stage_ended():
            return -1
        elif self.history[-1] == "/":
            return -1
        else:
            return (len(self.history) + 1) % 2

    def _game_stage_ended(self):
        last_action = self.history[-1]
        opp_action = self.history[-2]

        if last_action == "f":
            return True
        elif last_action == "c" and len(self.history) > 3:
            return True
        elif opp_action == "c" and last_action == "k":
            return True
        else:
            return False

    def is_chance(self):
        return self.player() == -1

    def get_infoSet_key(self) -> List[Action]:
        """
        Abstract cards and bet sizes
        """

        if self.is_chance() or self.is_terminal():
            raise Exception

        infoset = []
        cluster_id = str(get_preflop_cluster_id(self.history[self.player()]))

        # ------- CARD ABSTRACTION -------
        infoset.append(cluster_id)

        for action in self.history:
            if action in DISCRETE_ACTIONS:
                infoset.append(action)

        return infoset
