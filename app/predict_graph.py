import math
import streamlit as st
import predict
import std as stdfun
import tba


@st.cache_data()
def accuracyByProgress(tba_data,use_practice_before=math.inf):
    """
    Calculate the accuracy of predictions by progress in matches.
    This function iterates through the matches, calculates the win predictions
    for each alliance, and compares them to the actual winning alliance.
    It returns a dictionary where the keys are the match progress numbers
    and the values are the accuracy of predictions up to that point.
    Args:
        tba_data (list): List of match data from TBA API.
        use_practice_before (int): The cutoff match number to include practice matches.
    Returns:
        dict: A dictionary with match progress as keys and accuracy as values.
    """
    match_count = len(list(filter(lambda x: x["comp_level"] in ["qm"], tba_data)))
    result={}
    tba_data.sort(key=lambda x: (x["comp_level"], x["match_number"]))
    tba_data = list(filter(lambda x: x["comp_level"] in ["qm"], tba_data))
    for progress in range(1, match_count + 1):
        correct_predictions = 0
        all_predictions = 0
        for match in tba_data:
            # show 6 team keys by 2 alliances in table

            # Ensure match has alliances and team keys
            blue_alliance = match["alliances"]["blue"]["team_keys"]
            red_alliance = match["alliances"]["red"]["team_keys"]

            # remove 'frc' prefix

            blue_alliance = [team.replace("frc", "") for team in blue_alliance]
            red_alliance = [team.replace("frc", "") for team in red_alliance]
            if int(match["match_number"]) <= progress:
                predict_data = stdfun.calculate_team_stats(
                    cutoff_q_number=int(match["match_number"]),
                    use_practice_before=use_practice_before
                )
            else:
                predict_data = stdfun.calculate_team_stats(cutoff_q_number=progress,use_practice_before=use_practice_before)
            predictWin = predict.alliance_win_prediction(
                blue_alliance, red_alliance, predict_data
            )
            if match.get("winning_alliance", "") == (
                "blue"
                if predictWin["blue_win_prob"] > predictWin["red_win_prob"]
                else "red"
            ):
                correct_predictions += 1
            all_predictions += 1
        result[progress] = correct_predictions / all_predictions if all_predictions > 0 else 0
    return result

@st.cache_data()
def accuracyByPracticeBefore(tba_data, progress=1):
    """
    Calculate the accuracy of predictions based on the number of practice matches
    used before the qualification matches.
    This function iterates through the matches, calculates the win predictions
    for each alliance, and compares them to the actual winning alliance.
    It returns a dictionary where the keys are the number of practice matches used
    before the qualification matches and the values are the accuracy of predictions.
    Args:
        tba_data (list): List of match data from TBA API.
        progress (int): The match number up to which predictions are made.
    Returns:
        dict: A dictionary with the number of practice matches used as keys and accuracy as values.
    """
    match_count = len(list(filter(lambda x: x["comp_level"] in ["qm"], tba_data)))
    result={}
    tba_data.sort(key=lambda x: (x["comp_level"], x["match_number"]))
    tba_data = list(filter(lambda x: x["comp_level"] in ["qm"], tba_data))
    for use_practice_before in range(1, match_count + 1):
        correct_predictions = 0
        all_predictions = 0
        for match in tba_data:
            # show 6 team keys by 2 alliances in table

            # Ensure match has alliances and team keys
            blue_alliance = match["alliances"]["blue"]["team_keys"]
            red_alliance = match["alliances"]["red"]["team_keys"]

            # remove 'frc' prefix

            blue_alliance = [team.replace("frc", "") for team in blue_alliance]
            red_alliance = [team.replace("frc", "") for team in red_alliance]
            if int(match["match_number"]) <= progress:
                predict_data = stdfun.calculate_team_stats(
                    cutoff_q_number=int(match["match_number"]),
                    use_practice_before=use_practice_before
                )
            else:
                predict_data = stdfun.calculate_team_stats(cutoff_q_number=progress,use_practice_before=use_practice_before)
            predictWin = predict.alliance_win_prediction(
                blue_alliance, red_alliance, predict_data
            )
            if match.get("winning_alliance", "") == (
                "blue"
                if predictWin["blue_win_prob"] > predictWin["red_win_prob"]
                else "red"
            ):
                correct_predictions += 1
            all_predictions += 1
        result[use_practice_before] = correct_predictions / all_predictions if all_predictions > 0 else 0
    return result

if __name__ == "__main__":
    tba_data  = tba.get_match_schedule(event_key='2025casd')
    if tba_data:
        progress_accuracy = accuracyByProgress(tba_data)
        print(f"Progress Accuracy: {progress_accuracy}")
    else:
        print("No data available for the event.")