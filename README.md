# 🔍 Bayesian Clue Solver

A real-time probabilistic inference engine designed to beat the game of *Clue* using Bayesian reasoning, soft constraint propagation, and dynamic suggestion tracking. Built to calculate the likelihood of each card being in the murder envelope — and eventually recommend the optimal next move based on current information.

---

## 🧠 Project Overview

This engine models and updates beliefs about the game's hidden state using Bayesian inference. It tracks all player suggestions, responses, and seen cards, then continuously updates the probability that each suspect, weapon, and room card is in the envelope.

Inspired by probabilistic models in finance, AI, and information theory, the system is designed to:
- Infer which cards are in the envelope
- Track certainty over time
- Guide the user toward strategic suggestions
- Win *Clue* consistently in fewer than 7 turns

---

## 🧩 Key Components

### EnvelopeProbabilityEngine
- Tracks and updates probabilities for cards in the solution envelope
- Implements Bayesian inference for solution prediction
- Maintains separate probability distributions for suspects, weapons, and rooms

### PlayerCardTracker
- Tracks probabilities of cards for each player
- Updates beliefs based on suggestions and responses
- Maintains known cards and "cannot have" sets for each player

### ClueGameManager
- Orchestrates game state and player interactions
- Manages suggestion history and global known cards
- Integrates probability engines for comprehensive game analysis

### Streamlit Interface
- Real-time probability visualization
- Interactive suggestion logging
- Player card management
- Beautiful, modern UI with intuitive controls

---

## 📊 How the Bayesian Engine Works

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

## 💡 Example: No One Can Refute a Suggestion

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

## 🧪 Future Work

* 🔄 Monte Carlo simulation of possible world states consistent with history
* 🧭 AI assistant that chooses the optimal next suggestion based on expected entropy reduction
* 📈 Suggestion effectiveness graph (turns vs. confidence curve)
* 👥 Multiplayer interface or Discord bot integration

---

## 🛠️ Tech Stack

* **Python** for core logic
* **Streamlit** for interactive UI
* **Pandas/Numpy** for state management and belief updating
* *(Optional)* Gurobi / PyMC3 for constraint or sampling expansion

---

## 🚀 Running the Project

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

## 📜 License

MIT License

---
