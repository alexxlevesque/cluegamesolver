from collections import defaultdict
from typing import List, Optional
from player_card_tracker import PlayerCardTracker

class RuleBasedInferenceEngine:
    """Engine that applies rule-based inference to track and update card probabilities.
    
    This engine focuses on tracking how often players refute suggestions and uses that
    information to infer card ownership probabilities. The core idea is that if a player
    frequently refutes suggestions containing certain cards, they are more likely to
    have those cards.
    
    Attributes:
        tracker: The PlayerCardTracker instance to update probabilities in
        base_increase: Base amount to increase probability by for each refutation
        growth_factor: Factor to multiply base_increase by for each subsequent refutation
        refutation_history: Tracks number of times each player has refuted each card
    """
    
    def __init__(self, player_card_tracker: PlayerCardTracker, base_increase: float = 0.05, growth_factor: float = 1.5):
        """Initialize the rule-based inference engine.
        
        Args:
            player_card_tracker: PlayerCardTracker instance to update probabilities in
            base_increase: Base amount to increase probability by for each refutation
            growth_factor: Factor to multiply base_increase by for each subsequent refutation
        """
        self.tracker = player_card_tracker
        self.base_increase = base_increase
        self.growth_factor = growth_factor
        self.refutation_history = defaultdict(lambda: defaultdict(int))  # player -> card -> count

    def record_suggestion(self, suggester: str, suggested_cards: List[str], 
                         responder: Optional[str], shown_card: Optional[str]) -> None:
        """Record a suggestion and update refutation history if applicable.
        
        When a player refutes a suggestion but the shown card is unknown, increment
        the refutation count for each suggested card for that player.
        
        Args:
            suggester: Player who made the suggestion
            suggested_cards: List of cards that were suggested
            responder: Player who refuted the suggestion, if any
            shown_card: The specific card shown, if known
        """
        if responder and not shown_card:  # Only track when card shown is unknown
            for card in suggested_cards:
                self.refutation_history[responder][card] += 1

    def apply_inference(self) -> None:
        """Apply inference rules based on refutation history.
        
        For each player and card in the refutation history, increase the probability
        that the player has that card based on how many times they've refuted it.
        The increase amount grows exponentially with the number of refutations.
        """
        for player, card_counts in self.refutation_history.items():
            for card, count in card_counts.items():
                # Calculate probability increase using exponential growth
                increase = self.base_increase * (self.growth_factor ** (count - 1))
                self.tracker.increase_prob(player, card, amount=increase) 