import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import json
import os

st.title("FRC Alliance and Team Score Distributions")

# 檢查資料檔案是否存在
if not os.path.exists('team_stats.json'):
    st.error("""
    找不到資料檔案 'team_stats.json'！
    
    請先執行以下指令來生成資料檔案：
    ```
    python main.py
    ```
    """)
    st.stop()

# 從 JSON 檔案讀取資料
try:
    with open('team_stats.json', 'r') as f:
        teams_data = json.load(f)
except Exception as e:
    st.error(f"""
    讀取資料檔案時發生錯誤：
    {str(e)}
    
    請確認 'team_stats.json' 檔案格式正確。
    """)
    st.stop()

# 建立隊伍列表供選擇
team_list = sorted(list(teams_data.keys()))

# 使用下拉選單選擇隊伍
team1 = st.selectbox("選擇第一個隊伍:", team_list)
team2 = st.selectbox("選擇第二個隊伍:", team_list)
team3 = st.selectbox("選擇第三個隊伍:", team_list)

# Validate inputs
if team1 in teams_data and team2 in teams_data and team3 in teams_data:
    # Calculate alliance stats
    alliance_avg = teams_data[team1]['average'] + teams_data[team2]['average'] + teams_data[team3]['average']
    alliance_std = np.sqrt(teams_data[team1]['std_dev']**2 + teams_data[team2]['std_dev']**2 + teams_data[team3]['std_dev']**2)

    # Plot alliance distribution
    plt.figure(figsize=(10, 6))
    x_alliance = np.linspace(alliance_avg - 3*alliance_std, alliance_avg + 3*alliance_std, 100)
    y_alliance = norm.pdf(x_alliance, alliance_avg, alliance_std)
    plt.plot(x_alliance, y_alliance, label=f"Alliance (Mean: {alliance_avg:.2f}, Std: {alliance_std:.2f})", color='black')

    # Plot individual team distributions
    for team, color in zip([team1, team2, team3], ['blue', 'red', 'green']):
        avg = teams_data[team]['average']
        std = teams_data[team]['std_dev']
        if std > 0:  # Avoid plotting if std_dev is 0
            x = np.linspace(avg - 3*std, avg + 3*std, 100)
            y = norm.pdf(x, avg, std)
            plt.plot(x, y, label=f"Team {team} (Mean: {avg:.2f}, Std: {std:.2f})", color=color)

    plt.title("Alliance and Team Score Distributions")
    plt.xlabel("Score")
    plt.ylabel("Probability Density")
    plt.legend()
    plt.grid(True)

    # Save and display plot
    plt.savefig("alliance_team_distribution.png")
    st.image("alliance_team_distribution.png")

    # Explanation
    st.write("""
    **Why Normal Distribution?**  
    Team scores are assumed to follow a normal distribution due to the Central Limit Theorem, as scores result from many small, independent contributions (e.g., tasks, penalties).  

    **Alliance Score Calculation:**  
    The alliance score is the sum of the three teams' scores. The mean is the sum of individual means. The standard deviation is the square root of the sum of squared individual standard deviations, assuming independence.
    """)
else:
    st.error("Invalid team number(s). Please enter valid team numbers.")