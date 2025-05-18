#import necessary libraries
import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from pathlib import Path
from clue_game import ClueGameState
from clue_constants import SUSPECTS, WEAPONS, ROOMS

def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Set page config
st.set_page_config(
    page_title="Clue Solver",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and encode background image
background_image = get_base64_encoded_image("app_background.png")

# Add custom CSS
st.markdown(f"""
<style>
    /* Remove sidebar collapse button */
    [data-testid="collapsedControl"] {{
        display: none !important;
    }}

    /* Ensure sidebar is always visible */
    section[data-testid="stSidebar"][aria-expanded="true"] {{
        min-width: 300px !important;
        max-width: 300px !important;
        width: 300px !important;
    }}

    /* Main container */
    .main {{
        position: relative;
    }}

    /* Background and overlay */
    .stApp {{
        background-image: url("data:image/png;base64,{background_image}");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        position: relative;
    }}
    
    /* Dark overlay */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        background-color: rgba(0, 0, 0, 0.95);
        z-index: 1;
        pointer-events: none;
    }}
    
    /* Content styling */
    .stApp > * {{
        position: relative;
        z-index: 2;
    }}
    
    /* Dataframe styling */
    .dataframe {{
        background-color: rgba(0, 0, 0, 0.2);
        color: white !important;
    }}
    
    .dataframe th {{
        background-color: rgba(31, 97, 141, 0.5);
        color: white !important;
    }}
    
    .dataframe td {{
        background-color: rgba(0, 0, 0, 0.3);
        color: white !important;
    }}
    
    /* Text styling */
    .css-1fv8s86 {{
        color: #ffffff;
    }}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 3;
    }}
    
    /* Button styling */
    .stButton>button {{
        background-color: #1f618d;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        transition: background-color 0.3s;
    }}
    
    .stButton>button:hover {{
        background-color: #2980b9;
    }}
    
    /* Select box styling */
    .stSelectbox {{
        background-color: rgba(255, 255, 255, 0.1);
    }}

    /* Make sure all content is scrollable */
    [data-testid="stAppViewContainer"] {{
        position: relative;
        z-index: 2;
    }}

    /* Ensure proper stacking of elements */
    .stApp > header {{
        z-index: 4;
    }}

    /* Bar chart styling */
    [data-testid="stArrowVegaLiteChart"] {{
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        padding: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = None
if 'remainder_cards' not in st.session_state:
    st.session_state.remainder_cards = set()
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False

# Game setup in main area
st.title("Clue Game Setup")

# Player setup
col1, col2 = st.columns([2, 1])

with col1:
    num_players = st.number_input("Number of Players", min_value=3, max_value=6, value=3)
    players = []
    # First player is always "You"
    players.append("You")
    st.write("**Player 1:** You")
    
    # Get names for other players
    for i in range(1, num_players):
        player = st.text_input(f"Player {i+1} Name", key=f"player_{i}")
        if player:
            players.append(player)
    
    if len(players) == num_players:
        # Calculate remainder cards
        remainder = ClueGameState.calculate_remainder_cards(num_players)
        st.write(f"Each player will receive 3 cards")
        st.write(f"3 cards are set aside as the solution")
        st.write(f"Remainder cards to be revealed: {remainder}")
        
        if st.button("Start Game", type="primary"):
            st.session_state.game_state = ClueGameState(players)
            st.session_state.setup_complete = True
            st.success("Game started! Please select your cards below.")

# Your cards selection (only shown after game start, before remainder cards)
if st.session_state.setup_complete and not st.session_state.remainder_cards:
    st.divider()
    st.header("Select Your Cards")
    st.write("Please select exactly 3 cards that you have in your hand.")
    
    # Combine all cards into one list
    all_cards = SUSPECTS + WEAPONS + ROOMS
    
    # Use multiselect to choose any 3 cards
    your_cards = st.multiselect(
        "Select your 3 cards",
        all_cards,
        max_selections=3,
        key="your_cards"
    )
    
    if len(your_cards) == 3:
        if st.button("Confirm Your Cards", type="primary"):
            # Update game state with your cards
            st.session_state.game_state.known_cards["You"] = set(your_cards)
            # Update global known cards and probability engine
            for card in your_cards:
                st.session_state.game_state.probability_engine._update_known_card(card)
            st.success("Your cards have been recorded! Now select the remainder cards.")
    else:
        st.warning(f"Please select exactly 3 cards (you have selected {len(your_cards)})")

# Remainder card selection (only shown after your cards are selected)
if st.session_state.setup_complete and not st.session_state.remainder_cards and "You" in st.session_state.game_state.known_cards:
    st.divider()
    st.header("Select Remainder Cards")
    remainder = ClueGameState.calculate_remainder_cards(len(st.session_state.game_state.players))
    
    if remainder > 0:
        # Get your cards to exclude from remainder selection
        your_cards = st.session_state.game_state.known_cards["You"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Suspects")
            # Filter out your cards from suspect options
            available_suspects = [s for s in SUSPECTS if s not in your_cards]
            suspect_cards = st.multiselect(
                "Select suspect cards",
                available_suspects,
                key="suspect_remainder"
            )
        
        with col2:
            st.subheader("Weapons")
            # Filter out your cards from weapon options
            available_weapons = [w for w in WEAPONS if w not in your_cards]
            weapon_cards = st.multiselect(
                "Select weapon cards",
                available_weapons,
                key="weapon_remainder"
            )
        
        with col3:
            st.subheader("Rooms")
            # Filter out your cards from room options
            available_rooms = [r for r in ROOMS if r not in your_cards]
            room_cards = st.multiselect(
                "Select room cards",
                available_rooms,
                key="room_remainder"
            )
        
        selected_cards = set(suspect_cards + weapon_cards + room_cards)
        if len(selected_cards) == remainder:
            if st.button("Confirm Remainder Cards", type="primary"):
                st.session_state.remainder_cards = selected_cards
                st.session_state.game_state.set_remainder_cards(selected_cards)
                st.success("Remainder cards set! You can now start making suggestions.")
        elif len(selected_cards) < remainder:
            st.warning(f"Please select {remainder - len(selected_cards)} more card(s)")
        else:
            st.error(f"Please select {len(selected_cards) - remainder} fewer card(s)")

# Real-time probability panel in right sidebar
with st.sidebar:
    st.title("Real-time Probabilities")
    if st.session_state.game_state:
        probs = st.session_state.game_state.get_solution_probabilities()
        
        # Create tabs for different categories
        suspect_tab, weapon_tab, room_tab = st.tabs(["Suspects", "Weapons", "Rooms"])
        
        with suspect_tab:
            st.subheader("Suspects")
            # Create a DataFrame for suspects
            suspect_df = pd.DataFrame([
                {"Card": card, "Probability": f"{prob:.1%}"}
                for card, prob in sorted(probs["Suspects"].items(), key=lambda x: x[1], reverse=True)
            ])
            # Display as a bar chart
            st.bar_chart(pd.DataFrame([
                {"Card": card, "Probability": prob}
                for card, prob in sorted(probs["Suspects"].items(), key=lambda x: x[1], reverse=True)
            ]).set_index("Card"))
            # Display as a table
            st.dataframe(suspect_df)
        
        with weapon_tab:
            st.subheader("Weapons")
            # Create a DataFrame for weapons
            weapon_df = pd.DataFrame([
                {"Card": card, "Probability": f"{prob:.1%}"}
                for card, prob in sorted(probs["Weapons"].items(), key=lambda x: x[1], reverse=True)
            ])
            # Display as a bar chart
            st.bar_chart(pd.DataFrame([
                {"Card": card, "Probability": prob}
                for card, prob in sorted(probs["Weapons"].items(), key=lambda x: x[1], reverse=True)
            ]).set_index("Card"))
            # Display as a table
            st.dataframe(weapon_df)
        
        with room_tab:
            st.subheader("Rooms")
            # Create a DataFrame for rooms
            room_df = pd.DataFrame([
                {"Card": card, "Probability": f"{prob:.1%}"}
                for card, prob in sorted(probs["Rooms"].items(), key=lambda x: x[1], reverse=True)
            ])
            # Display as a bar chart
            st.bar_chart(pd.DataFrame([
                {"Card": card, "Probability": prob}
                for card, prob in sorted(probs["Rooms"].items(), key=lambda x: x[1], reverse=True)
            ]).set_index("Card"))
            # Display as a table
            st.dataframe(room_df)
        
        # Most likely solution
        st.divider()
        st.subheader("Most Likely Solution")
        solution = st.session_state.game_state.get_most_likely_solution()
        for category, card in solution.items():
            prob = probs[category + "s"][card]  # Add 's' to match dictionary keys
            st.write(f"**{category}:** {card} ({prob:.1%})")
        
        # Confidence indicator
        if st.session_state.game_state.is_solution_confident():
            st.success("🎯 High confidence in solution!")
        else:
            st.info("🔍 Still gathering evidence...")

# Main game interface (only shown after remainder cards are selected)
if st.session_state.game_state and st.session_state.remainder_cards:
    st.divider()
    st.title("Game Dashboard")
    
    # New Suggestion Section
    st.header("New Suggestion")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        suggester = st.selectbox("Who made the suggestion?", players)
        # Filter out remainder cards from suspect options
        available_suspects = [s for s in SUSPECTS if s not in st.session_state.remainder_cards]
        suspect = st.selectbox("Suspect", available_suspects)
    
    with col2:
        # Filter out remainder cards from weapon options
        available_weapons = [w for w in WEAPONS if w not in st.session_state.remainder_cards]
        weapon = st.selectbox("Weapon", available_weapons)
        # Filter out remainder cards from room options
        available_rooms = [r for r in ROOMS if r not in st.session_state.remainder_cards]
        room = st.selectbox("Room", available_rooms)
    
    with col3:
        # Filter out the suggester from possible responders
        possible_responders = ["None"] + [p for p in players if p != suggester]
        responder = st.selectbox("Who responded?", possible_responders)
        
        # Only show card selection if someone responded
        shown_card = None
        if responder != "None":
            shown_card = st.selectbox("Which card was shown?", ["Unknown"] + [suspect, weapon, room])
    
    if st.button("Add Suggestion", type="primary"):
        st.session_state.game_state.add_suggestion(
            suggester=suggester,
            suspect=suspect,
            weapon=weapon,
            room=room,
            responder=None if responder == "None" else responder,
            shown_card=None if shown_card == "Unknown" else shown_card
        )
        st.success("Suggestion added!")
    
    st.divider()
    
    # Game State Display
    st.header("Game State")
    col1, col2 = st.columns(2)
    
    # Column 1: Player Cards and Global Known Cards
    with col1:
        st.subheader("Player Cards")
        for player in st.session_state.game_state.players:
            known_cards, cannot_have = st.session_state.game_state.get_player_cards(player)
            st.write(f"**{player}**")
            if known_cards:
                st.write("Known cards:", ", ".join(known_cards))
            if cannot_have:
                st.write("Cannot have:", ", ".join(cannot_have))
            st.write("---")
        
        # Display global known cards
        st.subheader("All Known Cards")
        global_known = st.session_state.game_state.get_global_known_cards()
        if global_known:
            st.write("These cards are known to be in play (not in the solution):")
            st.write(", ".join(sorted(global_known)))
        else:
            st.write("No cards known yet")
    
    # Column 2: Suggestions History
    with col2:
        st.subheader("Suggestions History")
        suggestions = st.session_state.game_state.get_suggestions()
        if suggestions:
            df = pd.DataFrame([
                {
                    "Time": s.timestamp.strftime("%H:%M:%S"),
                    "Suggester": s.suggester,
                    "Suspect": s.suspect,
                    "Weapon": s.weapon,
                    "Room": s.room,
                    "Responder": s.responder or "None",
                    "Shown": s.shown_card or "Unknown"
                }
                for s in suggestions
            ])
            st.dataframe(df)
        else:
            st.write("No suggestions yet")
else:
    st.info("Please complete the game setup to begin") 