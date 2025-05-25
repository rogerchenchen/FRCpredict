# FRC Predict Viewer

This is a Python project for analyzing and predicting FRC (FIRST Robotics Competition) match results, featuring an interactive Streamlit web interface. You can use historical match data to predict alliance scores, win rates, and analyze prediction accuracy.

## Features

- Fetches match schedules and results from [The Blue Alliance (TBA)](https://www.thebluealliance.com/) API
- Reads match data from Firestore, calculates team score statistics
- Predicts win rates and score distributions for alliances
- Interactive charts and prediction accuracy analysis (via Streamlit)

## Installation & Requirements

1. **Python 3.9+**
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

1. **Add your TBA API Key**
   - Create a `.env` file in the project root with the following content:
     ```
     TBA_API=your_TBA_API_KEY
     ```
   - You can get your API key from your [TBA Account](https://www.thebluealliance.com/account).

2. **Add your Firebase key**
   - Download your Firebase service account key as a JSON file.
   - Rename it to `key.json` and place it in the project root.
   - You can generate this key in Firebase Console > Project Settings > Service Accounts > Generate new private key.

3. **Generate match score data**
   - Run the Firestore conversion script to create `app/match_team_scores.json`:
     ```bash
     python app/raw_data.py
     ```

4. **Start the Streamlit app**
   ```bash
   streamlit run app/main.py
   ```

## Project Structure

- `app/main.py`: Main Streamlit app
- `app/tba.py`: TBA API integration
- `app/raw_data.py`: Firestore data conversion and score calculation
- `app/std.py`: Statistical calculations
- `app/predict.py`: Win rate and score prediction
- `app/predict_graph.py`: Prediction accuracy analysis
- `app/match_team_scores.json`: Match score data (auto-generated)

## Notes

- **Important:** Add both `key.json` and `.env` to your `.gitignore` to keep your keys safe.
- If you encounter issues with TBA API or Firebase, double-check your keys and network settings.
