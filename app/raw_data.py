import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

cred = credentials.Certificate("././key.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()


# Score calculation function
def calculate_team_score(data):
    """
    Calculate the score for a team based on their match data.
    Args:
        data (dict): Match data containing auto, teleop, and endgame phases.
    Returns:
        int: The calculated score for the team.
    """
    score = 0

    # Auto phase
    if data["auto"].get("leave", False):
        score += 3
    coral_auto = data["auto"].get("coral", [0, 0, 0, 0])
    auto_coral_scores = [3, 4, 6, 7]  # L1, L2, L3, L4
    for i, count in enumerate(coral_auto):
        score += count * auto_coral_scores[i]
    score += data["auto"].get("net", 0) * 4
    score += data["auto"].get("processor", 0) * 6

    # Teleop phase
    coral_teleop = data["teleop"].get("coral", [0, 0, 0, 0])
    teleop_coral_scores = [2, 3, 4, 5]  # L1, L2, L3, L4
    for i, count in enumerate(coral_teleop):
        score += count * teleop_coral_scores[i]
    score += data["teleop"].get("net", 0) * 4
    score += data["teleop"].get("processor", 0) * 6

    # Endgame phase
    barge_status = data["endgame"].get("bargeStatus", "Did Not Attempt")
    if barge_status == "Success Deep Cage":
        score += 12
    elif barge_status == "Success Shallow Cage":
        score += 6
    elif barge_status == "Park":
        score += 2

    return score



def save_scores_by_match():
    """Fetch match documents from Firestore, calculate team scores,
    and save the results in a JSON file.
    This function retrieves match data from the Firestore database,
    calculates the score for each team in each match, and organizes
    the results by match ID. The final scores are saved in a JSON file
    named "match_team_scores.json". Each match ID contains a dictionary
    of team numbers and their corresponding scores.
    """
    docs = db.collection("matches/8020/2025_San_Diego").stream()

    match_scores = {}
    for doc in docs:
        doc_id = doc.id
        parts = doc_id.split("_")
        if len(parts) == 3:
            match_type, match_number, team_number = parts
            match_id = f"{match_type}_{match_number}"
            score = calculate_team_score(doc.to_dict())

            if match_id not in match_scores:
                match_scores[match_id] = {}
            match_scores[match_id][team_number] = score
        else:
            print(f"Invalid Id: {doc_id}")
            
    with open("app/match_team_scores.json", "w") as f:
        json.dump(match_scores, f, indent=2)

    print("Saved as match_team_scores.json")

if __name__ == "__main__":
    save_scores_by_match()
    print("Scores by match saved successfully.")