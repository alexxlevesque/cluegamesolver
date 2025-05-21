from typing import Dict, List, Set, Optional
import numpy as np
from clue_constants import SUSPECTS, WEAPONS, ROOMS

class ClueProbabilityEngine:
    def __init__(self):
        # Initialize probabilities for each category
        self.suspect_probs = self._initialize_category_probs(SUSPECTS)
        self.weapon_probs = self._initialize_category_probs(WEAPONS)
        self.room_probs = self._initialize_category_probs(ROOMS)
        
        # Constants for probability updates
        self.DECREASE_FACTOR = 0.5  # When a card is shown
        self.INCREASE_FACTOR = 2.0  # When no one can refute
        
        # Track known cards (cards we've seen)
        self.known_cards: Set[str] = set()
    
    def _initialize_category_probs(self, cards: List[str]) -> Dict[str, float]:
        """Initialize uniform probabilities for a category."""
        initial_prob = 1.0 / len(cards)
        return {card: initial_prob for card in cards}
    
    def update_probabilities(self, 
                           suggested_cards: List[str],
                           responder: Optional[str],
                           shown_card: Optional[str]) -> None:
        """Update probabilities based on a new suggestion and response."""
        # If a specific card was shown
        if responder and shown_card:
            # The shown card is definitely in someone's hand
            self._update_known_card(shown_card)
            # Decrease probability of other suggested cards
            for card in suggested_cards:
                if card != shown_card:
                    self._decrease_probability(card)
        
        # If no one could refute the suggestion
        elif not responder:
            # If no one could refute, these cards MUST be in the solution
            for card in suggested_cards:
                if card in SUSPECTS:
                    # Set this suspect to 1.0 and all others to 0.0
                    for suspect in SUSPECTS:
                        self.suspect_probs[suspect] = 1.0 if suspect == card else 0.0
                elif card in WEAPONS:
                    # Set this weapon to 1.0 and all others to 0.0
                    for weapon in WEAPONS:
                        self.weapon_probs[weapon] = 1.0 if weapon == card else 0.0
                elif card in ROOMS:
                    # Set this room to 1.0 and all others to 0.0
                    for room in ROOMS:
                        self.room_probs[room] = 1.0 if room == card else 0.0
        
        # Normalize probabilities within each category
        self._normalize_category(self.suspect_probs)
        self._normalize_category(self.weapon_probs)
        self._normalize_category(self.room_probs)
    
    def _update_known_card(self, card: str) -> None:
        """Mark a card as known and update its probability."""
        self.known_cards.add(card)
        
        # Set probability to 0 for the known card and redistribute among others
        if card in SUSPECTS:
            self.suspect_probs[card] = 0.0
            # Redistribute probability among remaining cards
            remaining_cards = [c for c in SUSPECTS if c not in self.known_cards]
            if remaining_cards:
                prob_per_card = 1.0 / len(remaining_cards)
                for c in remaining_cards:
                    self.suspect_probs[c] = prob_per_card
        elif card in WEAPONS:
            self.weapon_probs[card] = 0.0
            # Redistribute probability among remaining cards
            remaining_cards = [c for c in WEAPONS if c not in self.known_cards]
            if remaining_cards:
                prob_per_card = 1.0 / len(remaining_cards)
                for c in remaining_cards:
                    self.weapon_probs[c] = prob_per_card
        elif card in ROOMS:
            self.room_probs[card] = 0.0
            # Redistribute probability among remaining cards
            remaining_cards = [c for c in ROOMS if c not in self.known_cards]
            if remaining_cards:
                prob_per_card = 1.0 / len(remaining_cards)
                for c in remaining_cards:
                    self.room_probs[c] = prob_per_card
    
    def _decrease_probability(self, card: str) -> None:
        """Decrease the probability of a card being in the envelope."""
        if card in SUSPECTS:
            self.suspect_probs[card] *= self.DECREASE_FACTOR
        elif card in WEAPONS:
            self.weapon_probs[card] *= self.DECREASE_FACTOR
        elif card in ROOMS:
            self.room_probs[card] *= self.DECREASE_FACTOR
    
    def _increase_probability(self, card: str) -> None:
        """Increase the probability of a card being in the envelope."""
        if card in SUSPECTS:
            self.suspect_probs[card] *= self.INCREASE_FACTOR
        elif card in WEAPONS:
            self.weapon_probs[card] *= self.INCREASE_FACTOR
        elif card in ROOMS:
            self.room_probs[card] *= self.INCREASE_FACTOR
    
    def _normalize_category(self, probs: Dict[str, float]) -> None:
        """Normalize probabilities within a category to sum to 1."""
        total = sum(probs.values())
        if total > 0:  # Avoid division by zero
            for card in probs:
                probs[card] /= total
    
    def get_solution_probabilities(self) -> Dict[str, Dict[str, float]]:
        """Get current probabilities for each category."""
        return {
            "Suspects": self.suspect_probs,
            "Weapons": self.weapon_probs,
            "Rooms": self.room_probs
        }
    
    def get_most_likely_solution(self) -> Dict[str, str]:
        """Get the most likely solution based on current probabilities."""
        return {
            "Suspect": max(self.suspect_probs.items(), key=lambda x: x[1])[0],
            "Weapon": max(self.weapon_probs.items(), key=lambda x: x[1])[0],
            "Room": max(self.room_probs.items(), key=lambda x: x[1])[0]
        }
    
    def is_solution_confident(self, threshold: float = 0.9) -> bool:
        """Check if we have a confident solution."""
        return all(
            max(probs.values()) > threshold
            for probs in [self.suspect_probs, self.weapon_probs, self.room_probs]
        ) 