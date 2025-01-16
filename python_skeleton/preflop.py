from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

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
class PreflopHistory(base.History):

    def __init__(self, history: List[Action] = [], sample_id=0, round_state = None):
        super().__init__(history)
        self.round_state = round_state
        self.sample_id = sample_id

    def is_terminal(self):
        if len(self.history) == 0:
            return False
        if len(self.history[-1]) == 10:  # show community cards
            return True
        else:
            return False

    def actions(self):
        if self.is_chance():
            return []
        elif not self.is_terminal():
            legal_action = self.round_state.legal_actions()
            return list(legal_action)
        else:
            raise Exception("Cannot call actions on a terminal history")
