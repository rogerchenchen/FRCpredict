import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import math
import json
import os

# Initialize Firebase (if not already initialized)
@st.cache_resource
def initialize_firebase():
    try:
        app = firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate('key.json')
        app = firebase_admin.initialize_app(cred)
    return firestore.client()

# Score calculation function
def calculate_team_score(data):
    score = 0

    # Auto phase
    if data['auto'].get('leave', False):
        score += 3
    coral_auto = data['auto'].get('coral', [0, 0, 0, 0])
    auto_coral_scores = [3, 4, 6, 7]  # L1, L2, L3, L4
    for i, count in enumerate(coral_auto):
        score += count * auto_coral_scores[i]
    score += data['auto'].get('net', 0) * 4
    score += data['auto'].get('processor', 0) * 6

    # Teleop phase
    coral_teleop = data['teleop'].get('coral', [0, 0, 0, 0])
    teleop_coral_scores = [2, 3, 4, 5]  # L1, L2, L3, L4
    for i, count in enumerate(coral_teleop):
        score += count * teleop_coral_scores[i]
    score += data['teleop'].get('net', 0) * 4
    score += data['teleop'].get('processor', 0) * 6

    # Endgame phase
    barge_status = data['endgame'].get('bargeStatus', 'Did Not Attempt')
    if barge_status == 'Success Deep Cage':
        score += 12
    elif barge_status == 'Success Shallow Cage':
        score += 6
    elif barge_status == 'Park':
        score += 2

    return score

# Calculate mean and sample standard deviation
def calculate_stats(scores):
    n = len(scores)
    if n == 0:
        return 0, 0  # No data
    mean = sum(scores) / n
    if n == 1:
        return mean, 0  # Single match, std undefined
    variance = sum((x - mean) ** 2 for x in scores) / (n - 1)
    std_dev = math.sqrt(variance)
    return mean, std_dev

# Get and process data
@st.cache_data
def get_team_stats():
    db = initialize_firebase()
    docs = db.collection("matches/8020/2025_San_Diego").stream()
    
    # Group by teams
    team_scores = {}
    for doc in docs:
        doc_id = doc.id
        parts = doc_id.split('_')
        if len(parts) == 3:
            match_type, match_number, team_number = parts
            score = calculate_team_score(doc.to_dict())
            if team_number not in team_scores:
                team_scores[team_number] = {'scores': []}
            team_scores[team_number]['scores'].append(score)
    
    # Calculate statistics
    result = {}
    for team_number, data in team_scores.items():
        mean, std_dev = calculate_stats(data['scores'])
        result[team_number] = {
            'average': mean,
            'std_dev': std_dev
        }
    
    return result

# Streamlit interface
st.title("FRC Alliance Score Distribution Analyzer")

# Get data
teams_data = get_team_stats()

# Create team list for selection (sort by integer value)
team_list = sorted([int(team) for team in teams_data.keys()])
team_list = [str(team) for team in team_list]  # Convert back to string for display

# Split into two alliances
st.header("Blue Alliance")
blue1 = st.selectbox("Select Blue Alliance First Team:", team_list, key="blue1")
blue2 = st.selectbox("Select Blue Alliance Second Team:", team_list, key="blue2")
blue3 = st.selectbox("Select Blue Alliance Third Team:", team_list, key="blue3")

st.header("Red Alliance")
red1 = st.selectbox("Select Red Alliance First Team:", team_list, key="red1")
red2 = st.selectbox("Select Red Alliance Second Team:", team_list, key="red2")
red3 = st.selectbox("Select Red Alliance Third Team:", team_list, key="red3")

# Calculate and plot
if all(team in teams_data for team in [blue1, blue2, blue3, red1, red2, red3]):
    # Calculate alliance statistics
    blue_avg = sum(teams_data[team]['average'] for team in [blue1, blue2, blue3])
    blue_std = np.sqrt(sum(teams_data[team]['std_dev']**2 for team in [blue1, blue2, blue3]))
    
    red_avg = sum(teams_data[team]['average'] for team in [red1, red2, red3])
    red_std = np.sqrt(sum(teams_data[team]['std_dev']**2 for team in [red1, red2, red3]))

    # Create plot
    plt.figure(figsize=(12, 8))
    
    # Plot alliance distributions
    x_range = np.linspace(
        min(blue_avg - 3*blue_std, red_avg - 3*red_std),
        max(blue_avg + 3*blue_std, red_avg + 3*red_std),
        100
    )
    
    plt.plot(x_range, norm.pdf(x_range, blue_avg, blue_std), 
             label=f"Blue Alliance (Mean: {blue_avg:.2f}, Std: {blue_std:.2f})", 
             color='blue', linewidth=2)
    plt.plot(x_range, norm.pdf(x_range, red_avg, red_std), 
             label=f"Red Alliance (Mean: {red_avg:.2f}, Std: {red_std:.2f})", 
             color='red', linewidth=2)

    # Plot individual team distributions
    colors = ['lightblue', 'skyblue', 'dodgerblue', 'lightcoral', 'indianred', 'darkred']
    teams = [blue1, blue2, blue3, red1, red2, red3]
    
    for team, color in zip(teams, colors):
        avg = teams_data[team]['average']
        std = teams_data[team]['std_dev']
        if std > 0:
            x = np.linspace(avg - 3*std, avg + 3*std, 100)
            y = norm.pdf(x, avg, std)
            plt.plot(x, y, '--', label=f"Team {team} (Mean: {avg:.2f}, Std: {std:.2f})", 
                     color=color, alpha=0.6)

    plt.title("Alliance and Team Score Distributions")
    plt.xlabel("Score")
    plt.ylabel("Probability Density")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    
    # Adjust figure size to accommodate legend
    plt.tight_layout()

    # Save and display plot
    plt.savefig("alliance_distribution.png", bbox_inches='tight')
    st.image("alliance_distribution.png")

    # Win probability analysis
    st.header("Alliance Comparison")
    
    # Calculate blue alliance win probability
    z_score = (blue_avg - red_avg) / np.sqrt(blue_std**2 + red_std**2)
    win_prob = 1 - norm.cdf(0, z_score, 1)
    
    st.write(f"""
    **Alliance Total Score Comparison:**
    - Blue Alliance: {blue_avg:.2f} ± {blue_std:.2f}
    - Red Alliance: {red_avg:.2f} ± {red_std:.2f}
    
    **Win Probability Prediction:**
    - Blue Alliance Win Probability: {win_prob*100:.1f}%
    - Red Alliance Win Probability: {(1-win_prob)*100:.1f}%
    """)

    # Explanation
    st.write("""
    **Why Normal Distribution?**
    Team scores typically follow a normal distribution due to the Central Limit Theorem, as scores result from many small, independent contributions (e.g., various scoring elements).

    **Alliance Score Calculation:**
    - Alliance mean score is the sum of the three teams' mean scores
    - Alliance standard deviation is the square root of the sum of squared individual standard deviations (assuming team performances are independent)
    
    **Win Probability Calculation:**
    Uses the difference between two normal distributions to calculate the probability of one alliance scoring higher than the other.
    """)
else:
    st.error("Please ensure valid team numbers are selected.") 