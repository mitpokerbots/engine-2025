#include "skeleton/states.h"

#include <algorithm>
#include <numeric>

#include "skeleton/util.h"

namespace pokerbots::skeleton {

StatePtr RoundState::showdown() const {
  return std::make_shared<TerminalState>(std::array<int, 2>{0, 0}, std::array<bool, 2>{false, false}, getShared());
}

std::unordered_set<Action::Type> RoundState::legalActions() const {
  auto active = getActive(button);
  auto continueCost = pips[1-active] - pips[active];
  if (continueCost == 0) {
    // we can only raise the stakes if both players can afford it
    auto betsForbidden = stacks[0] == 0 || stacks[1] == 0;
    return betsForbidden ? std::unordered_set<Action::Type>{Action::Type::CHECK, Action::Type::FOLD}
                         : std::unordered_set<Action::Type>{
                               Action::Type::CHECK, Action::Type::RAISE, Action::Type::FOLD};
  }
  // continueCost > 0
  // similarly, re-raising is only allowed if both players can afford it
  auto raisesForbidden = continueCost == stacks[active] || stacks[1-active] == 0;
  return raisesForbidden
             ? std::unordered_set<Action::Type>{Action::Type::FOLD,
                                                Action::Type::CALL}
             : std::unordered_set<Action::Type>{
                   Action::Type::FOLD, Action::Type::CALL, Action::Type::RAISE};
}

std::array<int, 2> RoundState::raiseBounds() const {
  auto active = getActive(button);
  auto continueCost = pips[1-active] - pips[active];
  auto maxContribution = std::min(stacks[active], stacks[1-active] + continueCost);
  auto minContribution = std::min(maxContribution, continueCost + std::max(continueCost, BIG_BLIND));
  return {pips[active] + minContribution, pips[active] + maxContribution};
}

StatePtr RoundState::proceedStreet() const {
  if (street == 5) {
    return this->showdown();
  }
  auto newStreet = street == 0 ? 3 : street + 1;
  return std::make_shared<RoundState>(1, newStreet, std::array<int, 2>{0, 0}, stacks, hands, bounties, deck, getShared());
}

StatePtr RoundState::proceed(Action action) const {
  auto active = getActive(button);
  switch (action.actionType) {
    case Action::Type::FOLD: {
      auto delta = active == 0 ? stacks[0] - STARTING_STACK : STARTING_STACK - stacks[1];
      return std::make_shared<TerminalState>(std::array<int, 2>{delta, -1 * delta}, get_bounty_hits(), getShared());
    }
    case Action::Type::CALL: {
      if (button == 0) {  // sb calls bb
        return std::make_shared<RoundState>(
            1, 0, std::array<int, 2>{BIG_BLIND, BIG_BLIND},
            std::array<int, 2>{STARTING_STACK - BIG_BLIND,
                               STARTING_STACK - BIG_BLIND},
            hands, bounties, deck, getShared());
      }
      // both players acted
      auto newPips = pips;
      auto newStacks = stacks;
      auto contribution = newPips[1-active] - newPips[active];
      newStacks[active] = newStacks[active] - contribution;
      newPips[active] = newPips[active] + contribution;
      auto state = std::make_shared<RoundState>(button + 1, street, std::move(newPips), std::move(newStacks),
                                                hands, bounties, deck, getShared());
      return state->proceedStreet();
    }
    case Action::Type::CHECK: {
      if ((street == 0 && button > 0) || button > 1) {
        return this->proceedStreet();
      }
      // let opponent act
      return std::make_shared<RoundState>(button + 1, street, pips, stacks, hands, bounties, deck, getShared());
    }
    default: {  // Action::Type::RAISE
      auto newPips = pips;
      auto newStacks = stacks;
      auto contribution = action.amount - newPips[active];
      newStacks[active] = newStacks[active] - contribution;
      newPips[active] = newPips[active] + contribution;
      return std::make_shared<RoundState>(button + 1, street, std::move(newPips), std::move(newStacks), hands, bounties, deck, getShared());
    }
  }
}

std::array<bool, 2> RoundState::get_bounty_hits() const
{
    /*
    Determines if each player hit their bounty card during the round.

    A bounty is hit if the player's bounty card rank appears in either:
    - Their hole cards
    - The community cards dealt so far

    Returns:
        std::array<bool, 2>: An array containing two booleans where:
            - First boolean indicates if Player 1's bounty was hit
            - Second boolean indicates if Player 2's bounty was hit
    */
    std::vector<char> cards0, cards1;
    try
    {
        for(int i = 0; i < 2; i ++)
            cards0.push_back(this->hands[0][i][0]);
    }
    catch(const std::exception &e) {}
    try
    {
        for(int i = 0; i < 2; i ++)
            cards1.push_back(this->hands[1][i][0]);
    }
    catch(const std::exception &e) {}
    for(int i = 0; i < this->street; i ++)
    {
        cards0.push_back(this->deck[i][0]);
        cards1.push_back(this->deck[i][0]);
    }
    std::array<bool, 2> bounty_hits = {
        std::find(cards0.begin(), cards0.end(), this->bounties[0]) != cards0.end(), 
        std::find(cards1.begin(), cards1.end(), this->bounties[1]) != cards1.end() 
    };
    return bounty_hits;
}

std::ostream &RoundState::doFormat(std::ostream &os) const {
  std::array<std::string, 2> formattedHands = {
    join(hands[0].begin(), hands[0].end(), ""),
    join(hands[1].begin(), hands[1].end(), "")};

  os << "round(button=" << button << ", street=" << street << ", "
        << "pips=[" << join(pips.begin(), pips.end(), ", ") << "], "
        << "stacks=[" << join(stacks.begin(), stacks.end(), ", ") << "], "
        << "hands=[" << join(formattedHands.begin(), formattedHands.end(), ",") << "], "
        << "bounties=[" << join(bounties.begin(), bounties.end(), ",") << "], "
        << "deck=[" << join(deck.begin(), deck.end(), ", ") << "])";
  return os;
}

std::ostream &TerminalState::doFormat(std::ostream &os) const {
  os << "terminal(deltas=[" << join(deltas.begin(), deltas.end(), ", ") << "], "
  << "bounty_hits=[" << join(bounty_hits.begin(), bounty_hits.end(), ", ") << "])";
  return os;
}

} // namespace pokerbots::skeleton
