# Get tba key from .env file
import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
TBA_API = os.getenv("TBA_API")

EVENT_KEY = "2025casd"

import requests

@st.cache_data
def get_match_schedule(event_key):
    """
    Get the match schedule for a given event from The Blue Alliance (TBA) API.
    Args:
        event_key (str): The event key for the FRC event.
    Returns:
        list: A list of matches for the specified event.
    """
    url = f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches"
    headers = {"X-TBA-Auth-Key": TBA_API}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching match schedule: {response.status_code}")

# run get match schedule when this file is run
if __name__ == "__main__":
    try:
        matches = get_match_schedule(EVENT_KEY)
        print(f"Fetched {len(matches)} matches for event {EVENT_KEY}.")
        print(matches[:5])  # Print first 5 matches for brevity
    except Exception as e:
        print(e)