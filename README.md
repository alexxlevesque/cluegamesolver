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

## 🧩 Key Features

- ✅ **Bayesian probability engine** that updates card likelihoods in real time  
- ✅ **Dynamic game state tracking** for all players and cards  
- ✅ **Soft and hard evidence inference** from responses and shown cards  
- ✅ **Monte Carlo simulation** for posterior estimation under uncertainty (coming soon)  
- ✅ **Suggestion optimizer** that recommends the next best move based on info gain (planned)  
- ✅ **Streamlit interface** for interactive probability tracking and suggestion logging

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
| No one can refute          | All 3 cards are likely in envelope  | Multiply each $P(C)$ by **IncreaseFactor** (e.g. 2.0) |

### Normalization (per category):

After each update:

$$
P'(C_i) = \frac{P(C_i)}{\sum_{j=1}^{n} P(C_j)}
\quad \text{for all } C_j \text{ in the same category}
$$

This ensures that suspect, weapon, and room probabilities each sum to 1.

---

## 💡 Example: Someone Refutes Suggestion (But You Don’t See the Card)

**Suggestion:** Miss Scarlett, Lead Pipe, Study
**Player B refutes**, but shows the card to someone else (you don’t see it).

**Update strategy:** Multiply each of the 3 suggested cards by `DecreaseFactor = 0.8`, then normalize.

```python
# Before
Scarlett = 0.167
Pipe     = 0.167
Study    = 0.167

# After multiply (DecreaseFactor = 0.8)
Scarlett = 0.133
Pipe     = 0.133
Study    = 0.133

# Assume other 5 suspects still at 0.167 each
Total (Suspects) = 0.133 + (5 × 0.167) = 0.968

# Normalized (Suspects)
Scarlett = 0.133 / 0.968 ≈ 0.137
Others   = 0.167 / 0.968 ≈ 0.172

# Repeat same normalization for Weapons and Rooms
```

The result:

* Suggested cards become slightly **less likely** to be in the envelope
* Non-suggested cards become slightly **more likely** (due to normalization)

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
git clone https://github.com/yourname/clue-bayesian-engine.git
cd clue-bayesian-engine

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch Streamlit UI
streamlit run app.py
```

---

## 📜 License

MIT License

---

## 🧠 Author

Jack Flinton
[LinkedIn]([https://www.linkedin.com](https://github.com/alexxlevesque)) • Queen’s University
