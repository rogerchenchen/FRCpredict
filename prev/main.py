import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import math
import json

# 初始化 Firestore
cred = credentials.Certificate("key.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()


# 定義計分函數
def calculate_team_score(data):
    score = 0
    # Auto 階段
    if data["auto"].get("leave", False):
        score += 3
    coral_auto = data["auto"].get("coral", [0, 0, 0, 0])
    auto_coral_scores = [3, 4, 6, 7]  # L1, L2, L3, L4
    for i, count in enumerate(coral_auto):
        score += count * auto_coral_scores[i]
    score += data["auto"].get("net", 0) * 4
    score += data["auto"].get("processor", 0) * 6

    # Teleop 階段
    coral_teleop = data["teleop"].get("coral", [0, 0, 0, 0])
    teleop_coral_scores = [2, 3, 4, 5]  # L1, L2, L3, L4
    for i, count in enumerate(coral_teleop):
        score += count * teleop_coral_scores[i]
    score += data["teleop"].get("net", 0) * 4
    score += data["teleop"].get("processor", 0) * 6

    # Endgame 階段
    barge_status = data["endgame"].get("bargeStatus", "Did Not Attempt")
    if barge_status == "Success Deep Cage":
        score += 12
    elif barge_status == "Success Shallow Cage":
        score += 6
    elif barge_status == "Park":
        score += 2

    return score


# 計算平均值和樣本標準差
def calculate_stats(scores):
    n = len(scores)
    if n == 0:
        return 0, 0  # 無資料
    mean = sum(scores) / n
    if n == 1:
        return mean, 0  # 單場比賽，標準差未定義
    variance = sum((x - mean) ** 2 for x in scores) / (n - 1)
    std_dev = math.sqrt(variance)
    return mean, std_dev


# 獲取資料
docs = db.collection("matches/8020/2025_San_Diego").stream()

# 以隊伍分組
team_scores = {}
for doc in docs:
    doc_id = doc.id
    parts = doc_id.split("_")
    if len(parts) == 3:
        match_type, match_number, team_number = parts
        score = calculate_team_score(doc.to_dict())
        if team_number not in team_scores:
            team_scores[team_number] = {"scores": []}
        team_scores[team_number]["scores"].append(score)
    else:
        print(f"無效的文件 ID: {doc_id}")

# 計算統計並儲存為字典
result = {}
for team_number, data in team_scores.items():
    mean, std_dev = calculate_stats(data["scores"])
    result[team_number] = {"average": mean, "std_dev": std_dev}

# 輸出結果
print("隊伍統計字典：")
print(result)

# 將結果寫入 JSON 檔案
with open("team_stats.json", "w") as f:
    json.dump(result, f)
