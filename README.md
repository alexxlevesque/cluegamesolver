# 🔍 Bayesian Clue Solver

A sophisticated Clue game assistant that uses Bayesian reasoning and probabilistic inference to help players track game state, calculate probabilities, and make optimal suggestions. The system provides real-time probability updates for cards in the murder envelope and player hands, helping you solve the mystery faster and more effectively.

---

## Main Engine Overview (envelope_probability_engine)

This engine models and updates beliefs about the game's hidden state using Bayesian inference. It tracks all player suggestions, responses, and seen cards, then continuously updates the probability that each suspect, weapon, and room card is in the envelope.

Inspired by probabilistic models in finance, AI, and information theory, the system is designed to:
- Infer which cards are in the envelope
- Track certainty over time
- Maintain separate probability distributions for suspects, weapons, and rooms
- Guide the user toward strategic suggestions
- Win *Clue* consistently in fewer than 7 turns

---

## Project Structure

- `clue_game.py`  
  Main game loop and orchestrator. Integrates all logic engines and trackers.

- `engines/`  
  Logic engines that analyze game events and generate inferences:
  
  - `envelope_probability_engine.py`  
    Maintains probability distribution over cards in the envelope.
  
  - `rule_based_inference_engine.py`  
    Applies rules like repeated refutations implying ownership.

- `trackers/`  
  Components that maintain and update probabilistic knowledge:
  
  - `player_card_tracker.py`  
    Tracks probability distribution of each player holding each card.

---

## Other Key Components

## How It Works

The system uses Bayesian inference to update probabilities based on game events:

1. **Initial Setup**
   - Enter number of players (3-6)
   - Select your cards
   - System calculates initial probabilities

2. **During Gameplay**
   - Log suggestions and responses
   - System updates probabilities in real-time
   - View probability distributions for envelope and player cards
   - Get probability-based suggestions for optimal next moves

3. **Probability Updates**
   - When a card is shown: Eliminates it from envelope possibilities
   - When no one can refute: Increases probability of suggested cards
   - When a player shows a card: Updates player card probabilities
   - All probabilities are normalized within their categories (suspects, weapons, rooms)

## How It Works:

For each card $C$, we estimate:

$$
P(C \in \text{Envelope} \mid \text{History}) \propto P(C) \times P(\text{Observed Evidence} \mid C \in \text{Envelope})
$$

### Evidence Types & Bayesian Update Rules

| Event Type                 | What It Tells You                   | Update Rule                                           |
| -------------------------- | ----------------------------------- | ----------------------------------------------------- |
| Player shows a known card  | Card is not in the envelope         | Set $P(C) = 0$, renormalize                           |
| Player shows a hidden card | One of 3 suggested cards is in hand | Multiply each $P(C)$ by **DecreaseFactor** (e.g. 0.8) |
| No one can refute          | All 3 cards MUST be in envelope     | Set $P(C) = 1.0$ for suggested cards, $0.0$ for others |

### Normalization (per category):

After each update:

$$
P'(C_i) = \frac{P(C_i)}{\sum_{j=1}^{n} P(C_j)}
\quad \text{for all } C_j \text{ in the same category}
$$

This ensures that suspect, weapon, and room probabilities each sum to 1.

---

## Example: No One Can Refute a Suggestion

**Suggestion:** Miss Scarlett, Lead Pipe, Study

**No one can refute** - this means these cards MUST be in the envelope!

**Update strategy:** Set probability to 1.0 for suggested cards, 0.0 for all others

```python
# Before
Scarlett = 0.167  # Equal probability for all cards
Pipe     = 0.167
Study    = 0.167

# After (100% certainty)
Scarlett = 1.0    # Must be in envelope
Pipe     = 1.0    # Must be in envelope
Study    = 1.0    # Must be in envelope

# All other cards in each category
Others   = 0.0    # Cannot be in envelope
```

The result:
* Suggested cards are now **certain** to be in the envelope
* All other cards are **certain** to not be in the envelope
* Game is effectively solved!

---

## Tech Stack

* **Python** for core logic
* **Streamlit** for interactive UI
* **Pandas/Numpy** for state management and belief updating

---

## Running the Project

```bash
# 1. Clone the repo
git clone https://github.com/alexxlevesque/cluegamesolver.git
cd cluegamesolver

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch Streamlit UI
streamlit run app.py
```

---

## License

MIT License

---

*Built with ❤️ for Clue enthusiasts everywhere*
