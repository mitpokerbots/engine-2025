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
DISCRETE_ACTIONS = ["k", "bMIN", "bMID", "bMAX", "c", "f"]

class PreflopHistory(base.History):

    def __init__(self, history: List[Action] = [], game_state = None, round_state = None, sample_id=0, terminal_state = None):
        super().__init__(history)
        self.game_state = game_state
        self.round_state = round_state
        self.sample_id = sample_id
        self.terminal_state = terminal_state

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
            assert (
                not self._game_stage_ended()
            )  # game_stage_ended would mean that it is a chance node

            if len(self.history) == 2:
                return ["c", "bMIN", "bMID", "bMAX", "f"]
            elif self.history[-1] == "bMIN":
                return ["bMID", "bMAX", "f", "c"]
            elif self.history[-1] == "bMID":
                return ["bMAX", "f", "c"]
            elif self.history[-1] == "bMAX":
                return ["f", "c"]
            else:
                return ["k", "bMIN", "bMID", "bMAX"]
        else:
            raise Exception("Cannot call actions on a terminal history")

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
        return (
            (self.history[-1] == "c" and len(self.history) > 3)
            or self.history[-1] == "f"
            or self.history[-2:] == ["c", "k"]
        )

    def is_chance(self):
        return super().is_chance()

    def sample_chance_outcome(self):
        assert self.is_chance()

        if len(self.history) == 0:
            player_hand = self.round_state.hands[self.active]
            return "".join(player_hand)
        elif len(self.history) == 1:
            opponent_hand = self.round_state.hands[1-self.active]
            return "".join(opponent_hand)
        elif self.history[-1] != "/":
            return "/"
        else:
            board_cards = self.round_state.deck[:self.round_state.street]
            return "".join(board_cards)

    def terminal_utility(self, i: Player) -> int:
        assert self.is_terminal()  # We can only call the utility for a terminal history
        assert i in [0, 1]  # Only works for 2 player games for now

    def _get_total_pot_size(self, round_state):
        # Pot size is the sum of contributions from both players
        pot_size = round_state.STARTING_STACK - round_state.stacks[0] + \
                round_state.STARTING_STACK - round_state.stacks[1]

        # Latest bet is the maximum contribution in the current round
        latest_bet = max(round_state.pips)

        return pot_size, latest_bet

    def __add__(self, action: Action):
        new_history = PreflopHistory(self.history + [action], self.sample_id)
        return new_history

    def get_infoSet_key(self) -> List[Action]:
        """
        This is where we abstract away cards and bet sizes.
        """
        assert not self.is_chance()
        assert not self.is_terminal()

        player = self.player()
        infoset = []
        # ------- CARD ABSTRACTION -------
        infoset.append(str(get_preflop_cluster_id(self.history[player])))
        for i, action in enumerate(self.history):
            if action in DISCRETE_ACTIONS:
                infoset.append(action)

        return infoset
