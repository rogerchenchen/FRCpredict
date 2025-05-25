from scipy.stats import norm
import math


def predict_win_probability(blue_avg, blue_std, red_avg, red_std):
    """
    Calculate the win probability for the blue alliance against the red alliance
    based on their average scores and standard deviations.
    Args:
        blue_avg (float): Average score of the blue alliance.
        blue_std (float): Standard deviation of the blue alliance's scores.
        red_avg (float): Average score of the red alliance.
        red_std (float): Standard deviation of the red alliance's scores.
    Returns:
        float: Probability that the blue alliance wins against the red alliance.
    """
    if blue_std == 0 and red_std == 0:
        return 1.0 if blue_avg > red_avg else 0.0 if blue_avg < red_avg else 0.5
    combined_std = math.sqrt(blue_std**2 + red_std**2)
    z_score = (blue_avg - red_avg) / combined_std
    return norm.cdf(z_score)


def alliance_win_prediction(blue_teams, red_teams, stats):
    """#in english
    Calculate the win probability for an alliance based on team statistics.
    Args:
        blue_teams (list of str): List of team numbers for the blue alliance (3 teams).
        red_teams (list of str): List of team numbers for the red alliance (3 teams).
        stats (dict): Team statistics in the format:
            {
                "8020": {"average": 65.2, "std_dev": 7.1},
                ...
            }
    Returns:
        dict: Contains average, standard deviation, and win probabilities for both alliances.
    """
    blue_avg = sum(stats.get(team, {}).get("average", 0) for team in blue_teams)
    blue_std = math.sqrt(
        sum(stats.get(team, {}).get("std_dev", 0) ** 2 for team in blue_teams)
    )

    red_avg = sum(stats.get(team, {}).get("average", 0) for team in red_teams)
    red_std = math.sqrt(
        sum(stats.get(team, {}).get("std_dev", 0) ** 2 for team in red_teams)
    )

    blue_win_prob = predict_win_probability(blue_avg, blue_std, red_avg, red_std)

    return {
        "blue_avg": blue_avg,
        "blue_std": blue_std,
        "red_avg": red_avg,
        "red_std": red_std,
        "blue_win_prob": blue_win_prob,
        "red_win_prob": 1 - blue_win_prob,
    }


if __name__ == "__main__":
    from std import calculate_team_stats

    team_stats = calculate_team_stats(cutoff_q_number=50) 

    # frc3647, frc8119, frc3341
    # frc7441, frc1572, frc4738
    blue_alliance = ["3647", "8119", "3341"]
    red_alliance = ["7441", "1572", "4738"]

    result = alliance_win_prediction(blue_alliance, red_alliance, team_stats)

    print(
        "🔵 Blue Alliance: {:.2f} ± {:.2f}".format(
            result["blue_avg"], result["blue_std"]
        )
    )
    print(
        "🔴 Red Alliance: {:.2f} ± {:.2f}".format(result["red_avg"], result["red_std"])
    )
    print("🔵 Blue Win Probability: {:.1f}%".format(result["blue_win_prob"] * 100))
    print("🔴 Red Win Probability: {:.1f}%".format(result["red_win_prob"] * 100))
