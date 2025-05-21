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
if 'cards_confirmed' not in st.session_state:
    st.session_state.cards_confirmed = False

# Only show setup title and player setup if setup is not complete
if not st.session_state.setup_complete:
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

# Your cards selection (only shown after game start, before remainder cards, and before cards are confirmed)
if st.session_state.setup_complete and not st.session_state.remainder_cards and not st.session_state.cards_confirmed:
    st.divider()
    st.header("Select Your Cards")
    st.write("Please select exactly 3 cards that you have in your hand.")
    
    # Initialize confirmed_cards in session state if it doesn't exist
    if 'confirmed_cards' not in st.session_state:
        st.session_state.confirmed_cards = set()
    
    # Combine all cards into one list
    all_cards = SUSPECTS + WEAPONS + ROOMS
    
    # Use multiselect to choose any 3 cards
    your_cards = st.multiselect(
        "Select your 3 cards",
        all_cards,
        max_selections=3,
        key="card_selector"
    )
    
    if len(your_cards) == 3:
        if st.button("Confirm Your Cards", type="primary"):
            # Store your cards in session state with a different key
            st.session_state.confirmed_cards = set(your_cards)
            # Update game state with your cards
            st.session_state.game_state.known_cards["You"] = set(your_cards)
            # Update global known cards and probability engine
            for card in your_cards:
                st.session_state.game_state.probability_engine._update_known_card(card)
            # Mark cards as confirmed
            st.session_state.cards_confirmed = True
            st.success("Your cards have been recorded! Now select the remainder cards.")
    else:
        st.warning(f"Please select exactly 3 cards (you have selected {len(your_cards)})")

# Remainder card selection (only shown after your cards are confirmed)
if st.session_state.setup_complete and not st.session_state.remainder_cards and st.session_state.cards_confirmed:
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

# Main game interface (only shown after remainder cards are selected)
if st.session_state.game_state and st.session_state.remainder_cards:
    st.divider()
    st.title("Game Dashboard")
    
    # New Suggestion Section
    st.header("New Suggestion")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        suggester = st.selectbox("Who made the suggestion?", st.session_state.game_state.players)
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
        possible_responders = ["None"] + [p for p in st.session_state.game_state.players if p != suggester]
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

    # Add probability summary section
    st.divider()
    st.subheader("Current Probability Summary")
    
    # Get probabilities for each category
    probs = st.session_state.game_state.get_solution_probabilities()
    
    # Create three columns for Suspects, Weapons, and Rooms
    sum_col1, sum_col2, sum_col3 = st.columns(3)
    
    with sum_col1:
        st.markdown("**Suspects**")
        # Filter out zero probabilities and sort
        suspect_probs = [(s, p) for s, p in probs["Suspects"].items() if p > 0]
        suspect_probs.sort(key=lambda x: x[1], reverse=True)
        
        # Highest probability suspects
        st.markdown("""
        <div style='background-color: rgba(0, 255, 0, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'>
            <span style='color: #00ff00; font-weight: bold;'>Most Likely:</span>
        """, unsafe_allow_html=True)
        for suspect, prob in suspect_probs[:2]:  # Show top 2
            st.markdown(f"- {suspect} ({prob:.1%})", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Lowest non-zero probability suspects
        if len(suspect_probs) >= 2:
            st.markdown("""
            <div style='background-color: rgba(255, 0, 0, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'>
                <span style='color: #ff0000; font-weight: bold;'>Least Likely (>0%):</span>
            """, unsafe_allow_html=True)
            for suspect, prob in suspect_probs[-2:]:  # Show bottom 2 non-zero
                st.markdown(f"- {suspect} ({prob:.1%})", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    with sum_col2:
        st.markdown("**Weapons**")
        # Filter out zero probabilities and sort
        weapon_probs = [(w, p) for w, p in probs["Weapons"].items() if p > 0]
        weapon_probs.sort(key=lambda x: x[1], reverse=True)
        
        # Highest probability weapons
        st.markdown("""
        <div style='background-color: rgba(0, 255, 0, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'>
            <span style='color: #00ff00; font-weight: bold;'>Most Likely:</span>
        """, unsafe_allow_html=True)
        for weapon, prob in weapon_probs[:2]:  # Show top 2
            st.markdown(f"- {weapon} ({prob:.1%})", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Lowest non-zero probability weapons
        if len(weapon_probs) >= 2:
            st.markdown("""
            <div style='background-color: rgba(255, 0, 0, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'>
                <span style='color: #ff0000; font-weight: bold;'>Least Likely (>0%):</span>
            """, unsafe_allow_html=True)
            for weapon, prob in weapon_probs[-2:]:  # Show bottom 2 non-zero
                st.markdown(f"- {weapon} ({prob:.1%})", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    with sum_col3:
        st.markdown("**Rooms**")
        # Filter out zero probabilities and sort
        room_probs = [(r, p) for r, p in probs["Rooms"].items() if p > 0]
        room_probs.sort(key=lambda x: x[1], reverse=True)
        
        # Highest probability rooms
        st.markdown("""
        <div style='background-color: rgba(0, 255, 0, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'>
            <span style='color: #00ff00; font-weight: bold;'>Most Likely:</span>
        """, unsafe_allow_html=True)
        for room, prob in room_probs[:2]:  # Show top 2
            st.markdown(f"- {room} ({prob:.1%})", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Lowest non-zero probability rooms
        if len(room_probs) >= 2:
            st.markdown("""
            <div style='background-color: rgba(255, 0, 0, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'>
                <span style='color: #ff0000; font-weight: bold;'>Least Likely (>0%):</span>
            """, unsafe_allow_html=True)
            for room, prob in room_probs[-2:]:  # Show bottom 2 non-zero
                st.markdown(f"- {room} ({prob:.1%})", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    
    # Game State Display
    st.header("Game State")
    col1, col2 = st.columns(2)
    
    # Column 1: Player Cards and Global Known Cards
    with col1:
        st.subheader("Player Cards")
        for player in st.session_state.game_state.players:
            st.write(f"**{player}**")
            
            # Special display for "You" player
            if player == "You":
                if "confirmed_cards" in st.session_state and st.session_state.confirmed_cards:
                    st.markdown("""
                    <div style='background-color: rgba(0, 191, 255, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'>
                        <span style='color: #00bfff; font-weight: bold;'>Your Cards:</span>
                    """, unsafe_allow_html=True)
                    st.markdown("- " + "<br>- ".join(sorted(st.session_state.confirmed_cards)), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Add high probability cards section with green highlighting
            high_prob_cards = st.session_state.game_state.player_tracker.get_high_probability_cards(player)
            if high_prob_cards:
                st.markdown("""
                <div style='background-color: rgba(0, 255, 0, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'>
                    <span style='color: #00ff00; font-weight: bold;'>High Probability Cards:</span>
                """, unsafe_allow_html=True)
                for card, prob in high_prob_cards:
                    st.markdown(f"- {card} ({prob:.1%})", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Display cannot-have cards in red (except for "You" player)
            if player != "You":
                cannot_have = st.session_state.game_state.player_tracker.get_cannot_have_cards(player)
                if cannot_have:
                    st.markdown("""
                    <div style='background-color: rgba(255, 0, 0, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'>
                        <span style='color: #ff0000; font-weight: bold;'>Cannot Have:</span>
                    """, unsafe_allow_html=True)
                    st.markdown("- " + "<br>- ".join(sorted(cannot_have)), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            
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