import pandas as pd
import predict_graph
import std as stdfun
import streamlit as st
import tba
import predict
import plotly.graph_objects as go

# get data from tba.py and show with streamlit
st.title("FRC Predict Viewer")

event_key = st.text_input("Enter Event Key", "2025casd")

if not event_key:
    st.warning("Please enter a valid event key.")
    st.stop()

data = tba.get_match_schedule(event_key=event_key)
# slider to choose match number (in simulation), only read firestore data before it to predict

match_count = len(list(filter(lambda x: x["comp_level"] in ["qm"], data)))

progress = st.slider(
    "Match Number",
    1,
    match_count,
    1,
    key="match_number_slider",
)
use_practice = st.checkbox("Use Practice Matches", value=True)
use_practice_before = (
    st.slider(
        "Use Practice Matches N",
        1,
        match_count,
        match_count,
        key="practice_match_number_slider",
    )
    if use_practice
    else 0
)

# show teamkeys with table
if data:
    # tab to show plot
    tabs = st.tabs(["Prediction Graphs", "Match Schedule"])
    with tabs[0]:
        # Plot accuracy by progress
        st.subheader("Prediction Accuracy by Match Progress")
        # Generate accuracy data
        accuracyData = predict_graph.accuracyByProgress(
            data, use_practice_before=use_practice_before
        )

        # Prepare DataFrame
        df = pd.DataFrame(list(accuracyData.items()), columns=["x", "y"])
        df["y"] *= 100  # Convert to percentage
        df.set_index("x", inplace=True)

        # Plotly version (optional)
        fig_progress = go.Figure()
        fig_progress.add_trace(
            go.Scatter(x=df.index, y=df["y"], mode="lines+markers", name="Accuracy")
        )
        fig_progress.update_layout(
            title=f"Accuracy by Match Progress \n(Using Practice Matches Before Qualification Matches {use_practice_before})",
            xaxis_title="Match Number",
            yaxis_title="Accuracy (%)",
        )
        st.plotly_chart(fig_progress, use_container_width=True)

        st.subheader("Prediction Accuracy by Practice Matches")

        # Generate practice accuracy data
        accuracyPracticeData = predict_graph.accuracyByPracticeBefore(
            data, progress=progress
        )

        # Prepare DataFrame
        df_practice = pd.DataFrame(
            list(accuracyPracticeData.items()), columns=["x", "y"]
        )
        df_practice["y"] *= 100  # Convert to percentage
        df_practice.set_index("x", inplace=True)

        # Plotly version (optional)
        fig_practice = go.Figure()
        fig_practice.add_trace(
            go.Scatter(
                x=df_practice.index,
                y=df_practice["y"],
                mode="lines+markers",
                name="Accuracy",
            )
        )
        fig_practice.update_layout(
            title=f"Accuracy by Practice Matches used\n(Data before qualification matches {progress})",
            xaxis_title="Practice Matches Used Before",
            yaxis_title="Accuracy (%)",
        )
        st.plotly_chart(fig_practice, use_container_width=True)
    with tabs[1]:
        st.subheader(f"Match Schedule for {event_key}")
        st.write(f"Total Matches: {len(data)}")
        # Create a table to display match data
        match_data = []
        correct_predictions = 0
        all_predictions = 0
        data.sort(key=lambda x: (x["comp_level"], x["match_number"]))
        data = list(filter(lambda x: x["comp_level"] in ["qm"], data))
        for match in data:
            # show 6 team keys by 2 alliances in table

            # Ensure match has alliances and team keys
            blue_alliance = match["alliances"]["blue"]["team_keys"]
            red_alliance = match["alliances"]["red"]["team_keys"]

            # remove 'frc' prefix

            blue_alliance = [team.replace("frc", "") for team in blue_alliance]
            red_alliance = [team.replace("frc", "") for team in red_alliance]
            has_data = False
            if int(match["match_number"]) <= progress:
                predict_data = stdfun.calculate_team_stats(
                    cutoff_q_number=int(match["match_number"]),
                    use_practice_before=use_practice_before,
                )
                has_data = True
            else:
                predict_data = stdfun.calculate_team_stats(
                    cutoff_q_number=progress, use_practice_before=use_practice_before
                )
                has_data = False
            predictWin = predict.alliance_win_prediction(
                blue_alliance, red_alliance, predict_data
            )
            match_info = {
                "Match": f'{match["match_number"]}',
                "Blue Alliance": ", ".join(match["alliances"]["blue"]["team_keys"]),
                "Red Alliance": ", ".join(match["alliances"]["red"]["team_keys"]),
                "Winning Alliance": (
                    "🔵" if match.get("winning_alliance", "N/A") == "blue" else "🔴"
                ),
                "Predicted Winner": (
                    "🔵"
                    if predictWin["blue_win_prob"] > predictWin["red_win_prob"]
                    else "🔴"
                ),
                "Pre Blue": f"{predictWin['blue_avg']:.1f}",
                "Pre Red": f"{predictWin['red_avg']:.1f}",
                # read data from tba
                "Blue": match["alliances"]["blue"]["score"],
                "Red": match["alliances"]["red"]["score"],
                "Win Probability": f"{max(predictWin['blue_win_prob'],predictWin['red_win_prob']):.2%}",
                "Correct Prediction": (
                    "✅"
                    if match.get("winning_alliance", "")
                    == (
                        "blue"
                        if predictWin["blue_win_prob"] > predictWin["red_win_prob"]
                        else "red"
                    )
                    else "❌"
                ),
            }
            if match.get("winning_alliance", "") == (
                "blue"
                if predictWin["blue_win_prob"] > predictWin["red_win_prob"]
                else "red"
            ):
                correct_predictions += 1
            all_predictions += 1
            match_data.append(match_info)
        st.write(
            f"Correct Predictions: {correct_predictions} / {all_predictions} ({(correct_predictions / all_predictions) * 100:.2f}%)"
        )
        st.table(match_data)
