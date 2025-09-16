import json
import matplotlib.pyplot as plt

def analyze(filepath):
    data = json.load(open(filepath))
    states = [e["state"] for e in data.get("history", [])]
    counts = {s: states.count(s) for s in set(states)}
    plt.bar(counts.keys(), counts.values())
    plt.title("Emotion Cycle Counts")
    plt.xlabel("Emotion State")
    plt.ylabel("Occurrences")
    plt.show()

if __name__ == "__main__":
    analyze("infra/logs/mental_logs/emotions.json")  
import argparse 
import cvs 
import json 
import os 
import matplotlib.pyploy as plt 


def load_emotions(filepath: str) -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
