#import necessary libraries
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from engines.envelope_probability_engine import EnvelopeProbabilityEngine
from engines.rule_based_inference_engine import RuleBasedInferenceEngine
from player_card_tracker import PlayerCardTracker
from clue_constants import SUSPECTS, WEAPONS, ROOMS

#define suggestion dataclass (list of strings)
@dataclass
class Suggestion:
    timestamp: datetime
    suggester: str
    suspect: str
    weapon: str
    room: str
    responder: Optional[str]
    shown_card: Optional[str]

#create initial game state
class ClueGameManager:
    
    #initialize game state
    def __init__(self, players: List[str]):
        # Ensure Player 1 is always named "You"
        if players[0] != "You":
            players[0] = "You"
        
        #initialize players, known cards, cannot have, suggestions, and soft beliefs
        self.players = players
        self.known_cards: Dict[str, Set[str]] = {player: set() for player in players}
        self.cannot_have: Dict[str, Set[str]] = {player: set() for player in players}
        self.suggestions: List[Suggestion] = []
        self.soft_beliefs: Dict[str, Dict[str, float]] = {player: {} for player in players}
        
        # Initialize player card tracker
        all_cards = SUSPECTS + WEAPONS + ROOMS
        hand_sizes = {player: 3 for player in players}  # Each player starts with 3 cards
        self.player_card_tracker = PlayerCardTracker(players, all_cards, hand_sizes)
        
        # Initialize inference engines
        self.probability_engine = EnvelopeProbabilityEngine()
        self.rule_engine = RuleBasedInferenceEngine(self.player_card_tracker)
        
        self.remainder_cards: Set[str] = set()
        self.global_known_cards: Set[str] = set()  # Track all known cards globally

        # Initialize all cards as possible for each player
        all_cards = set(SUSPECTS + WEAPONS + ROOMS)
        for player in players:
            self.soft_beliefs[player] = {card: 1.0 for card in all_cards}

    # calculate the number of remainder cards after dealing 3 to each player and setting aside solution cards
    @staticmethod
    def calculate_remainder_cards(num_players: int) -> int:
        total_cards = len(SUSPECTS) + len(WEAPONS) + len(ROOMS)  # 21 cards total
        solution_cards = 3  # 1 suspect, 1 weapon, 1 room
        dealt_cards = num_players * 3  # Each player gets exactly 3 cards
        remainder = total_cards - solution_cards - dealt_cards
        return max(0, remainder)  # Ensure we don't return a negative number
    
    # update the global known cards list and probability engine
    def _update_global_known_cards(self, card: str) -> None:
        self.global_known_cards.add(card)
        self.probability_engine._update_known_card(card)
    
    def set_remainder_cards(self, cards: Set[str]) -> None:
        self.remainder_cards = cards
        for card in cards:
            self._update_global_known_cards(card)

    # add suggestion logic, called every time a suggestion is made
    def add_suggestion(self, suggester: str, suspect: str, weapon: str, room: str,
                      responder: Optional[str], shown_card: Optional[str]) -> None:
        suggestion = Suggestion(
            timestamp=datetime.now(),
            suggester=suggester,
            suspect=suspect,
            weapon=weapon,
            room=room,
            responder=responder,
            shown_card=shown_card
        )
        self.suggestions.append(suggestion)
        
        # Create list of suggested cards
        suggested_cards = [suspect, weapon, room]
        
        # Update player card tracker
        self.player_card_tracker.update_from_suggestion(
            suggested_cards=suggested_cards,
            suggesting_player=suggester,
            responder=responder,
            shown_card=shown_card,
            players_in_order=self.players
        )
        
        # Update rule-based inference engine
        self.rule_engine.record_suggestion(
            suggester=suggester,
            suggested_cards=suggested_cards,
            responder=responder,
            shown_card=shown_card
        )
        # Apply rule-based inference after recording
        self.rule_engine.apply_inference()
        
        # Get the order of players after the suggester
        suggester_index = self.players.index(suggester)
        response_order = self.players[suggester_index + 1:] + self.players[:suggester_index]
        
        # Special case: If Player 1 is the responder, we always know the shown card
        if responder == self.players[0] and shown_card:
            self.known_cards[responder].add(shown_card)
            self._update_global_known_cards(shown_card)
            # Update soft beliefs for other players
            for player in self.players:
                if player != responder:
                    self.soft_beliefs[player][shown_card] = 0.0
        
        # If someone else shows a card to Player 1
        elif responder and shown_card and suggester == self.players[0]:
            self.known_cards[responder].add(shown_card)
            self._update_global_known_cards(shown_card)
            # Update soft beliefs for other players
            for player in self.players:
                if player != responder:
                    self.soft_beliefs[player][shown_card] = 0.0
        
        # Handle players who couldn't respond (only those who had a chance to respond)
        elif responder:
            # Find the index of the responder in the response order
            responder_index = response_order.index(responder)
            # Only players before the responder in the order couldn't have any of the cards
            players_who_couldnt_respond = response_order[:responder_index]
            
            # Update cannot_have for players who had a chance to respond but couldn't
            for player in players_who_couldnt_respond:
                for card in [suspect, weapon, room]:
                    self.cannot_have[player].add(card)
            
            # Update soft beliefs for the responder
            shown_cards = {suspect, weapon, room}
            for card in shown_cards:
                if card not in self.known_cards[responder]:
                    self.soft_beliefs[responder][card] += 0.1  # Small increase in probability
        
        # Update probability engine
        self.probability_engine.update_probabilities(
            suggested_cards=[suspect, weapon, room],
            responder=responder,
            shown_card=shown_card
        )

    # returns the set of known cards and known not-held cards for a player    
    def get_player_cards(self, player:str) -> Tuple[Set[str], Set[str]]:
        return self.known_cards[player], self.cannot_have[player]
    
    # returns the list of suggestions made  
    def get_suggestions(self) -> List[Suggestion]:
        return self.suggestions
    
    # returns the soft beliefs for a player
    def get_soft_beliefs(self, player: str) -> Dict[str, float]:
        return self.soft_beliefs[player]
    
    # returns the current probabilities for each category
    def get_solution_probabilities(self) -> Dict[str, Dict[str, float]]:
        return self.probability_engine.get_solution_probabilities()
    
    # returns the most likely solution based on current probabilities
    def get_most_likely_solution(self) -> Dict[str, str]:
        return self.probability_engine.get_most_likely_solution()
    
    # returns true if the solution is confident
    def is_solution_confident(self, threshold: float = 0.9) -> bool:
        return self.probability_engine.is_solution_confident(threshold)

    # returns the set of all known cards in the game
    def get_global_known_cards(self) -> Set[str]:
        return self.global_known_cards

