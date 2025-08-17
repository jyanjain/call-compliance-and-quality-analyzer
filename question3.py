import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


class CallQualityAnalyzer:
    """Analyzer for call quality metrics including overtalk and silence detection"""

    def __init__(self):
        self.call_data = {}
        self.metrics_df = None

    def load_json_file(self, file_path: str):
        """Load a JSON file containing utterances"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if "conversations" in data:
                return data["conversations"]
            elif "utterances" in data:
                return data["utterances"]
            elif "messages" in data:
                return data["messages"]
            else:
                return [data]
        return []

    def load_all_calls(self, directory_path: str):
        """Load all JSON calls from directory"""
        directory = Path(directory_path)
        json_files = list(directory.glob("*.json"))

        for json_file in json_files:
            call_id = json_file.stem
            call_data = self.load_json_file(str(json_file))
            if call_data:
                self.call_data[call_id] = call_data

        print(f"Loaded {len(self.call_data)} calls")

    def validate_utterances(self, call_data):
        """Ensure utterances have correct fields & valid times"""
        valid = []
        for u in call_data:
            if not all(k in u for k in ["speaker", "stime", "etime"]):
                continue
            try:
                st = float(u["stime"])
                et = float(u["etime"])
                if et > st >= 0:
                    valid.append(
                        {
                            "speaker": str(u["speaker"]).lower(),
                            "text": str(u.get("text", "")),
                            "stime": st,
                            "etime": et,
                        }
                    )
            except:
                continue
        return sorted(valid, key=lambda x: x["stime"])

    def calc_overtalk_and_silence(self, utterances):
        """Calculate overtalk and silence percentages"""
        if len(utterances) < 2:
            return 0.0, 0.0

        total_duration = max(u["etime"] for u in utterances) - min(
            u["stime"] for u in utterances
        )
        if total_duration <= 0:
            return 0.0, 0.0

        silence_time = 0.0
        overtalk_time = 0.0

        for i in range(len(utterances) - 1):
            curr = utterances[i]
            nxt = utterances[i + 1]

            if nxt["stime"] > curr["etime"]:
                # Silence
                silence_time += nxt["stime"] - curr["etime"]
            elif nxt["stime"] < curr["etime"]:
                # Overtalk
                overtalk_time += curr["etime"] - nxt["stime"]

        silence_pct = round((silence_time / total_duration) * 100, 2)
        overtalk_pct = round((overtalk_time / total_duration) * 100, 2)
        return overtalk_pct, silence_pct

    def analyze_all_calls(self):
        """Run analysis for all calls"""
        results = []
        for call_id, call_data in self.call_data.items():
            utterances = self.validate_utterances(call_data)
            if not utterances:
                continue

            overtalk_pct, silence_pct = self.calc_overtalk_and_silence(utterances)

            call_duration = max(u["etime"] for u in utterances) - min(
                u["stime"] for u in utterances
            )
            results.append(
                {
                    "call_id": call_id,
                    "overtalk_percentage": overtalk_pct,
                    "silence_percentage": silence_pct,
                    "call_duration_seconds": round(call_duration, 2),
                }
            )

        self.metrics_df = pd.DataFrame(results)
        return self.metrics_df

    def save_results_json(self, filename="call_quality_results.json"):
        """Save results in JSON file"""
        if self.metrics_df is None:
            print("Run analysis first")
            return
        results = self.metrics_df.to_dict(orient="records")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {filename}")

    def create_visualizations(self):
        """Make plots"""
        if self.metrics_df is None or self.metrics_df.empty:
            print("No data to visualize")
            return

        plt.figure(figsize=(12, 5))

        # Overtalk
        plt.subplot(1, 2, 1)
        plt.hist(
            self.metrics_df["overtalk_percentage"], bins=15, color="red", edgecolor="black"
        )
        plt.title("Distribution of Overtalk %")
        plt.xlabel("Overtalk %")
        plt.ylabel("Number of Calls")

        # Silence
        plt.subplot(1, 2, 2)
        plt.hist(
            self.metrics_df["silence_percentage"], bins=15, color="blue", edgecolor="black"
        )
        plt.title("Distribution of Silence %")
        plt.xlabel("Silence %")
        plt.ylabel("Number of Calls")

        plt.tight_layout()
        plt.savefig("call_quality_plots.png", dpi=300)
        plt.show()

# if __name__ == "__main__":
#     analyzer = CallQualityAnalyzer()
#     analyzer.load_all_calls("All_Conversations")  
#     metrics = analyzer.analyze_all_calls()
#     print(metrics)
#     analyzer.save_results_json("call_quality_metrics.json")
#     analyzer.create_visualizations()
