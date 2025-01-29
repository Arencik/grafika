import csv
import os
import time


class ResultsManager:
    def __init__(self, csv_path="resources/output/results.csv"):
        self.results = []
        self.csv_path = csv_path

    def add_result(self, image_name, reaction_time, intensity, channel):
        # Dodanie timestamp (czas naciśnięcia klawisza)
        current_timestamp = time.time()
        self.results.append({
            "timestamp": current_timestamp,
            "image_name": image_name,
            "reaction_time": reaction_time,
            "intensity": intensity,
            "channel": channel
        })

    def get_results(self):
        return self.results

    def export_csv(self):
        # Append do istniejącego pliku
        fieldnames = ["timestamp", "image_name", "reaction_time", "intensity", "channel"]
        file_exists = os.path.exists(self.csv_path)
        with open(self.csv_path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for res in self.results:
                writer.writerow(res)
