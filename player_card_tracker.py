from typing import Dict, List, Optional, Set
import numpy as np
from clue_constants import SUSPECTS, WEAPONS, ROOMS

# track the probability of each card for each player
class PlayerCardTracker:
    def __init__(self, players: List[str], cards: List[str], hand_sizes: Dict[str, int]):
        self.players = players
        self.cards = cards
        self.hand_sizes = hand_sizes
        
        # Initialize probability matrix with uniform distribution
        # For each card, divide 1.0 evenly among all players
        self.player_card_probs: Dict[str, Dict[str, float]] = {
            player: {card: 1.0 / len(players) for card in cards}
            for player in players
        }
        
        # Constants for probability adjustments
        self.INCREASE_FACTOR = 1.5  # When a player likely has a card
        self.DECREASE_FACTOR = 0.5  # When a player likely doesn't have a card
        
        # Track known cards (100% certainty)
        self.known_cards: Dict[str, Set[str]] = {player: set() for player in players}
        
        # Track cards that players definitely don't have
        self.cannot_have: Dict[str, Set[str]] = {player: set() for player in players}

    # normalize the probabilities to ensure constraints are met:
    # 1. For each card, sum of probabilities across players <= 1.0
    # 2. For each player, weighted sum of probabilities <= hand_size
    def _normalize_probabilities(self) -> None:
        # First normalize each card's probabilities across players
        for card in self.cards:
            total = sum(self.player_card_probs[player][card] for player in self.players)
            if total > 0:  # Avoid division by zero
                for player in self.players:
                    self.player_card_probs[player][card] /= total
        
        # Then ensure hand size constraints
        for player in self.players:
            total_prob = sum(self.player_card_probs[player].values())
            if total_prob > self.hand_sizes[player]:
                # Scale down probabilities to meet hand size constraint
                scale_factor = self.hand_sizes[player] / total_prob
                for card in self.cards:
                    if card not in self.known_cards[player]:  # Don't scale known cards
                        self.player_card_probs[player][card] *= scale_factor

    def update_from_suggestion(self, 
                             suggested_cards: List[str],
                             suggesting_player: str,
                             responder: Optional[str],
                             shown_card: Optional[str],
                             players_in_order: List[str]) -> None:
        # Case 1: Known card was shown
        if responder and shown_card:
            # Set probability to 1.0 for responder, 0.0 for others
            for player in self.players:
                if player == responder:
                    self.player_card_probs[player][shown_card] = 1.0
                    self.known_cards[player].add(shown_card)
                else:
                    self.player_card_probs[player][shown_card] = 0.0
                    self.cannot_have[player].add(shown_card)
        
        # Case 2: Unknown card was shown
        elif responder:
            # Get players who passed before the responder
            suggester_idx = players_in_order.index(suggesting_player)
            responder_idx = players_in_order.index(responder)
            
            # Handle wrap-around in circular player order
            if responder_idx < suggester_idx:
                responder_idx += len(players_in_order)
            
            # Players who passed definitely don't have any of the suggested cards
            passed_players = players_in_order[suggester_idx+1:responder_idx]
            for player in passed_players:
                for card in suggested_cards:
                    self.player_card_probs[player][card] = 0.0
                    self.cannot_have[player].add(card)
            
            # Responder must have at least one of the suggested cards
            # Increase probability uniformly for suggested cards
            for card in suggested_cards:
                if card not in self.known_cards[responder]:
                    self.player_card_probs[responder][card] *= self.INCREASE_FACTOR
        
        # Case 3: No one could refute
        else:
            # If no one could refute, these cards MUST be in the envelope
            # Set probability to 0.0 for all players for these cards
            for player in self.players:
                for card in suggested_cards:
                    if card not in self.known_cards[player]:
                        self.player_card_probs[player][card] = 0.0
                        self.cannot_have[player].add(card)
        
        # Normalize probabilities after updates
        self._normalize_probabilities()

    # returns the current probability matrix
    def get_prob_matrix(self) -> Dict[str, Dict[str, float]]:
        return self.player_card_probs

    # returns the probability of each card being in the envelope
    def get_envelope_probabilities(self) -> Dict[str, float]:
        envelope_probs = {}
        for card in self.cards:
            # P(envelope) = 1 - sum(P(player_i has card))
            total_player_prob = sum(self.player_card_probs[player][card] 
                                  for player in self.players)
            envelope_probs[card] = max(0.0, 1.0 - total_player_prob)
        return envelope_probs

    # returns the probability of a specific player having a specific card
    def get_player_card_probability(self, player: str, card: str) -> float:
        return self.player_card_probs[player][card]
    
    # marks a card as definitely held by a player
    def mark_known_card(self, player: str, card: str) -> None:
        # Set probability to 1.0 for this player, 0.0 for others
        for p in self.players:
            if p == player:
                self.player_card_probs[p][card] = 1.0
                self.known_cards[p].add(card)
            else:
                self.player_card_probs[p][card] = 0.0
                self.cannot_have[p].add(card)
        
        self._normalize_probabilities()

    # returns the n most likely cards for a player
    def get_most_likely_cards(self, player: str, n: int = 3) -> List[tuple[str, float]]:
        probs = self.player_card_probs[player]
        return sorted(probs.items(), key=lambda x: x[1], reverse=True)[:n]

    # returns the set of cards that a player definitely doesn't have
    def get_cannot_have_cards(self, player: str) -> Set[str]:
        return self.cannot_have[player]

    # returns the cards that have probability above the threshold for a player
    def get_high_probability_cards(self, player: str, threshold: float = 0.9) -> List[tuple[str, float]]:
        high_prob_cards = []
        for card, prob in self.player_card_probs[player].items():
            if prob >= threshold:
                high_prob_cards.append((card, prob))
        return sorted(high_prob_cards, key=lambda x: x[1], reverse=True)

    # increases the probability of a player having a card by a specified amount
    def increase_prob(self, player: str, card: str, amount: float) -> None:
        current = self.player_card_probs[player][card]
        self.player_card_probs[player][card] = min(current + amount, 1.0)
        self._normalize_probabilities() 