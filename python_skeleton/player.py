'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        pass

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        my_bounty = round_state.bounties[active]  # your current bounty rank
        #pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
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

        if my_bounty_hit:
            print("I hit my bounty of " + bounty_rank + "!")
        if opponent_bounty_hit:
            print("Opponent hit their bounty of " + opponent_bounty_rank + "!")

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        my_bounty = round_state.bounties[active]  # your current bounty rank
        #pass
    
    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
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

        if my_bounty_hit:
            print("I hit my bounty of " + bounty_rank + "!")
        if opponent_bounty_hit:
            print("Opponent hit their bounty of " + opponent_bounty_rank + "!")


    def check_Quads(self, game_state, round_state, active):
        street = round_state.street
        my_cards = round_state.hands[active]
        board_cards = round_state.deck[:street]

        all_cards = my_cards + board_cards
        all_cards.sort()

        for i in range(0, len(all_cards)-3):
            if all_cards[i][0] == all_cards[i+1][0] and all_cards[i+1][0] == all_cards[i+2][0] and all_cards[i+2][0] == all_cards[i+3][0]:
                print("There's a Quads")
                return True
            
        return False
    
    def check_FullHouse(self, game_state, round_state, active):
        street = round_state.street
        my_cards = round_state.hands[active]
        board_cards = round_state.deck[:street]
        all_cards = my_cards + board_cards
        all_cards.sort()

        isTriple = False
        triple = None

        for i in range(0, len(all_cards)-2):
            if all_cards[i][0] == all_cards[i+1][0] and all_cards[i+1][0] == all_cards[i+2][0]:
                print("There's a Triples")
                isTriple = True
                triple = all_cards[i][0]
        
        if isTriple == False:
            return False

        for i in range(len(all_cards)):
            for j in range(i+1, len(all_cards)):
                if all_cards[i][0] == all_cards[j][0] and all_cards[i][0] != triple:
                    return True

        return False
    
    def check_Straight(self, game_state, round_state, active):
        street = round_state.street
        my_cards = round_state.hands[active]
        board_cards = round_state.deck[:street]
        all_cards = my_cards + board_cards
        
        if street == 0:
            return False
        
        ranks = '23456789TJQKA'
        rank_values = {rank: index for index, rank in enumerate(ranks)}
        card_ranks = sorted([rank_values[card[0]] for card in all_cards])

        straight = False
        for i in range(len(card_ranks)-4):
            if card_ranks[i] == card_ranks[i+1]-1 and card_ranks[i+1] == card_ranks[i+2]-1 and card_ranks[i+2] == card_ranks[i+3]-1 and card_ranks[i+3] == card_ranks[i+4]-1:
                return True
        
        return False
    
    def check_flush(self,game_state,round_state, active):
        street = round_state.street
        my_cards = round_state.hands[active]
        board_cards = round_state.deck[:street]
        all_cards = my_cards + board_cards

        suits = [card[1] for card in all_cards]
        suit_counts = {}

        for suit in set(suits):
            count = suits.count(suit)
            suit_counts[suit] = count
        
        if max(suit_counts.values()) == 5:
            return True
        else:
            return False
        
    def check_fourSameSuit(self,game_state,round_state, active):
        street = round_state.street
        my_cards = round_state.hands[active]
        board_cards = round_state.deck[:street]
        all_cards = my_cards + board_cards

        suits = [card[1] for card in all_cards]
        suit_counts = {}

        for suit in set(suits):
            count = suits.count(suit)
            suit_counts[suit] = count
        
        if max(suit_counts.values()) == 4:
            return True
        else:
            return False
        
    def check_triples(self, game_state, round_state, active):
            street = round_state.street
            my_cards = round_state.hands[active]
            board_cards = round_state.deck[:street]
            current_cards = my_cards + board_cards

            # Create a dictionary to count occurrences of each rank
            rank_counts = {}

            for card in current_cards:
                rank = card[0]
                if rank not in rank_counts:
                    rank_counts[rank] = 0
                rank_counts[rank] += 1

            # Check if any rank has a count of exactly 3
            for count in rank_counts.values():
                if count == 3:
                    return True

            return False

    def check_2_pairs(self, game_state, round_state, active):
        street = round_state.street
        my_cards = round_state.hands[active]
        board_cards = round_state.deck[:street]
        current_cards = my_cards + board_cards

        # Create a dictionary to count occurrences of each rank
        rank_counts = {}
        for card in current_cards:
            rank = card[0]
            if rank not in rank_counts:
                rank_counts[rank] = 0
            rank_counts[rank] += 1

        # Count the number of pairs
        num_pairs = 0
        for count in rank_counts.values():
            if count == 2:
                num_pairs += 1

        # Check if there are exactly two pairs
        return num_pairs == 2
    
    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_bounty = round_state.bounties[active]  # your current bounty rank
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot

        #Version 1 - Logic Bot
        my_cards = round_state.hands[active]
        card1 = my_cards[0]
        card2 = my_cards[1]

        rank1 = card1[0]
        suit1 = card1[1]
        rank2 = card2[0]
        suit2 = card2[1]

        card_type = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "k", "A"]

        big_blind = bool(active)  # True if you are the big blind

        if street == 0:
            if RaiseAction in legal_actions:
                min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
                min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
                max_cost = max_raise - my_pip  # the cost of a maximum bet/raise

                if rank1  == "A" and rank2 == "A":
                    return RaiseAction(min(max(min_cost, 85), max_cost))
                if rank1  == "K" and rank2 == "K":
                    return RaiseAction(min(max(min_cost, 82), max_cost))
                if rank1  == "Q" and rank2 == "Q":
                    return RaiseAction(min(max(min_cost, 80), max_cost))
                if rank1  == "J" and rank2 == "J":
                    return RaiseAction(min(max(min_cost, 77), max_cost))
                if rank1  == "10" and rank2 == "10":
                    return RaiseAction(min(max(min_cost, 75), max_cost))
                if rank1  == "9" and rank2 == "9":
                    return RaiseAction(min(max(min_cost, 72), max_cost))

            if CallAction in legal_actions:
                if rank1 == rank2:
                    if rank1 == "4" or rank1 == "5" or rank1 == "6" or rank1 == "7" or rank1 == "8": #Pairs 4-8
                        return CallAction()
                    else:
                        if opp_pip <= 75:
                            return CallAction()

                if rank1 == "A" or rank2 == "A": #Has a A (2-K suited, 6-K unsuited)
                    if suit1 == suit2:
                        return CallAction()
                    else:
                        for i in range(4, len(card_type)-1):
                            if rank1 == card_type[i]:
                                return CallAction()
                            if rank2 == card_type[i]:
                                return CallAction()

                        if opp_pip <= 75:
                            return CallAction()

                if rank1 == "K" or rank2 == "K": #Has a K (7-Q suited, 9-Q unsuited)
                    if suit1 == suit2:
                        for i in range(5, len(card_type)-2):
                            if rank1 == card_type[i]:
                                return CallAction()
                            if rank2 == card_type[i]:
                                return CallAction()

                        if opp_pip <= 75:
                            return CallAction()
                    else:
                        for i in range(7, len(card_type)-2):
                            if rank1 == card_type[i]:
                                return CallAction()
                            if rank2 == card_type[i]:
                                return CallAction()

                        if opp_pip <= 75:
                            return CallAction()

                if rank1 == "Q" or rank2 == "Q": #Has a Q (9-J suited, 10-J unsuited)
                    if suit1 == suit2:
                        for i in range(7, len(card_type)-3):
                            if rank1 == card_type[i]:
                                return CallAction()
                            if rank2 == card_type[i]:
                                return CallAction()

                        if opp_pip <= 75:
                            return CallAction()
                    else:
                        for i in range(8, len(card_type)-3):
                            if rank1 == card_type[i]:
                                return CallAction()
                            if rank2 == card_type[i]:
                                return CallAction()

                        if opp_pip <= 75:
                            return CallAction()

                if rank1 == "J" or rank2 == "J": #Has a J (10 suited)
                    if suit1 == suit2 and suit1 == "10":
                        return CallAction()
                    if opp_pip <= 75:
                            return CallAction()

                if rank1 == "10" or rank2 == "10": #Has a 10 (7-9 suited, 9 unsuited)
                    if suit1 == suit2 and opp_pip <= 75:
                        for i in range(5, 8):
                            if rank1 == card_type[i]:
                                return CallAction()
                            if rank2 == card_type[i]:
                                return CallAction()

                    if suit1 != suit2 and opp_pip <= 75:
                        if suit1 == "9":
                            return CallAction()

                if rank1 == "9" or rank2 == "9": #Has a 9 (8-9 suited)
                    if suit1 == suit2 and opp_pip <= 75:
                        for i in range(6, 8):
                            if rank1 == card_type[i]:
                                return CallAction()
                            if rank2 == card_type[i]:
                                return CallAction()


            if CheckAction in legal_actions:
                return CheckAction()

            if FoldAction in legal_actions:
                return FoldAction()







        if RaiseAction in legal_actions:
           min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
           min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
           max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        if RaiseAction in legal_actions:
            if random.random() < 0.5:
                return RaiseAction(min_raise)
        if CheckAction in legal_actions:  # check-call
            return CheckAction()
        if random.random() < 0.25:
            return FoldAction()
        return CallAction()

    def check_suits_equal(self, card1, card2):
        if card1[1] == card2[1]:
            return True
        return False

    def check_ranks_equal(self, card1, card2):
        if card1[0] == card2[0]:
            return True
        return False

    def check_pair(self, cards): ##returns the rank of pair if there exists a pair, 0 otherwise
        for card1_index in range(cards.len()-1):
            for card2_index in range (card1_index + 1, cards.len()):
                if check_suits_equal(cards[card1_index], cards[card2_index]) and check_ranks_equal(cards[card1_index], my_cards[card2_index]):
                    return cards[card1_index][0]
        return '0'

    def check_2_pairs(my_cards, street):
        num_pair = 0
        pairs = []
        for i in range(0, street+1):
            for j in range(i+1, street+2):
                if check_ranks_equal(my_cards[i], my_cards[j]):
                    num_pair += 1
                    pairs.append([my_cards[i], my_cards[j]])
        if num_pair == 2:
            return pairs
        else:
            return None









if __name__ == '__main__':
    run_bot(Player(), parse_args())
