import json
import math


def calculate_team_stats(
    cutoff_q_number, json_path="app/match_team_scores.json", use_practice_before=math.inf
):
    """
    Calculate team statistics from match scores.
    Args:
        cutoff_q_number (int): The cutoff match number for qualifications.
        json_path (str): Path to the JSON file containing match scores.
        use_practice_before (int): The match number before which practice matches are included.
    Returns:
        dict: A dictionary containing team numbers as keys and their average scores and standard deviations as values.
    """
    with open(json_path, "r") as f:
        match_scores = json.load(f)

    team_scores = {}

    raw_log = {}

    for match_id, teams in match_scores.items():
        parts = match_id.split("_")
        if len(parts) != 2:
            print(f"Invalid match_id：{match_id}")
            continue

        match_type, match_number_str = parts
        try:
            match_number = int(match_number_str)
        except ValueError:
            print(f"Invalid match number{match_number_str}")
            continue

        include_match = (
            match_type == "Practice" and cutoff_q_number <= use_practice_before
        ) or (match_type == "Qualifications" and match_number < cutoff_q_number)

        if not include_match:
            continue

        for team_number, score in teams.items():
            if team_number not in team_scores:
                team_scores[team_number] = []
            team_scores[team_number].append(score)
            if team_number not in raw_log:
                raw_log[team_number] = []
            raw_log[team_number].append({"match_id": match_id, "score": score})

    result = {}
    for team_number, scores in team_scores.items():
        mean, std_dev = calculate_stats(scores)
        result[team_number] = {"average": mean, "std_dev": std_dev}
    return result


def calculate_stats(scores):
    """
    Calculate the mean and sample standard deviation of a list of scores.
    Args:
        scores (list of float): List of scores to calculate statistics for.
    Returns:
        tuple: A tuple containing the mean and standard deviation of the scores.
    1. Mean is the average of the scores.
    2. Standard deviation is calculated using the sample standard deviation formula.
    """
    n = len(scores)
    if n == 0:
        return 0, 0  # No data
    mean = sum(scores) / n
    if n == 1:
        return mean, 0  # Single match, std undefined
    variance = sum((x - mean) ** 2 for x in scores) / (n - 1)
    std_dev = math.sqrt(variance)
    return mean, std_dev


if __name__ == "__main__":
    cutoff_q_number = 5  # Example cutoff, adjust as needed
    data = calculate_team_stats(cutoff_q_number)
    print("Team statistics:")
    # show with json
    print(json.dumps(data["8020"], indent=2))
