import os
import csv
import matplotlib
import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
from tkinter import messagebox
from logic.latex_report import generate_pdf_with_fallback


matplotlib.use("TkAgg")


class ResultWindow:
    def __init__(self, master, results_manager):
        self.master = master
        self.results_manager = results_manager

        self.master.title("Wyniki testu")
        self.master.geometry("1200x800")

        # Główna ramka dzieląca na tekst i wykresy
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(expand=True, fill="both")

        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.pack(side="top", fill="x", pady=10)

        self.bottom_frame = tk.Frame(self.main_frame)
        self.bottom_frame.pack(side="top", expand=True, fill="both", pady=10)

        # Wewnętrzne ramki dla lepszej organizacji
        self.text_frame = tk.Frame(self.top_frame)
        self.text_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.charts_frame = tk.Frame(self.bottom_frame)
        self.charts_frame.pack(side="top", fill="both", expand=True)

        self.button_frame = tk.Frame(self.bottom_frame)
        self.button_frame.pack(side="bottom", fill="x", pady=10)

        # Dane bieżącego testu
        results = self.results_manager.get_results()

        # Tekstowe podsumowanie
        summary_text = "Wyniki testu (bieżącej sesji):\n\n"
        for i, res in enumerate(results, start=1):
            dt_str = datetime.fromtimestamp(res['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            summary_text += f"{i}. Obraz: {res['image_name']}, Czas: {res['reaction_time']:.2f}s, Intensywność: {res['intensity']}, Timestamp: {dt_str}\n"

        self.text_label = tk.Label(self.text_frame, text=summary_text, justify="left")
        self.text_label.pack(pady=10, anchor="w")

        # Zapis wyników do CSV (append)
        self.results_manager.export_csv()

        # Wczytanie wszystkich danych (historycznych)
        all_results = self.load_all_results()

        # WYKRES 1: Bar plot (bieżący test), oś Y: obrazy, oś X: średni czas reakcji
        fig1, ax1, chart_path_current = self.create_current_test_bar_plot(results)

        # WYKRES 2: Historyczny wykres reakcji w czasie dla każdego obrazu
        fig2, ax2, chart_path_history = self.create_historical_line_plot(all_results, results)

        # Osadzenie wykresów
        canvas1 = FigureCanvasTkAgg(fig1, master=self.charts_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side="left", padx=10, pady=10)

        self.pdf_button = tk.Button(self.button_frame, text="Generuj PDF", command=lambda: self.generate_pdf(chart_path_current, chart_path_history))
        self.pdf_button.pack(side="top", padx=10, pady=10)

        canvas2 = FigureCanvasTkAgg(fig2, master=self.charts_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side="right", padx=10, pady=10)

        # Przycisk PDF pod ramką wykresów
        

    def load_all_results(self):
        csv_path = "resources/output/results.csv"
        if not os.path.exists(csv_path):
            return []
        results = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append({
                    "timestamp": float(row["timestamp"]),
                    "image_name": row["image_name"],
                    "reaction_time": float(row["reaction_time"]),
                    "intensity": int(row["intensity"])
                })
        return results

    def create_current_test_bar_plot(self, results):
        # Obliczamy średni czas reakcji dla każdego obrazu w bieżącym teście
        from statistics import mean
        results_by_image = {}
        for r in results:
            img = r['image_name'].split("\\")[-1]
            if img not in results_by_image:
                results_by_image[img] = []
            results_by_image[img].append(r['reaction_time'])

        images = list(results_by_image.keys())
        avg_times = [mean(results_by_image[img]) for img in images]

        fig, ax = plt.subplots(figsize=(5,4))
        y_pos = range(len(images))
        ax.barh(y_pos, avg_times, align='center', color='skyblue')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(images)
        ax.invert_yaxis()  # żeby najwyższy był na górze
        ax.set_xlabel('Czas reakcji (s)')
        ax.set_title('Czas reakcji dla obrazow (biezacy test)')

        output_dir = os.path.join("resources", "output")
        os.makedirs(output_dir, exist_ok=True)
        chart_path_current = os.path.join(output_dir, "chart_current_test.png")
        fig.savefig(chart_path_current)
        return fig, ax, chart_path_current

    def create_historical_line_plot(self, all_results, current_results):
        # Tworzymy liniowy wykres czasu reakcji w funkcji czasu dla poszczególnych obrazów
        # x - czas (datetime), y - czas reakcji, seria - nazwa obrazu
        fig, ax = plt.subplots(figsize=(5,4))

        # Grupowanie historycznych wyników po obrazie
        results_by_image = {}
        for r in all_results:
            img = r['image_name'].split("\\")[-1]
            if img not in results_by_image:
                results_by_image[img] = []
            results_by_image[img].append(r)

        # Sortujemy każdą listę po timestamp
        for img in results_by_image:
            results_by_image[img].sort(key=lambda x: x['timestamp'])

        # Rysujemy wykres dla każdego obrazu
        for img, res_list in results_by_image.items():
            x = [datetime.fromtimestamp(r['timestamp']) for r in res_list]
            y = [r['reaction_time'] for r in res_list]
            ax.plot(x, y, marker='o', label=img)

        # Dodajemy formatowanie osi X jako datę i godzinę
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        fig.autofmt_xdate(rotation=15, ha='right')  # automatyczne pochylanie etykiet z rotacją i wyrównaniem
        fig.set_size_inches(5, 4)

        ax.set_title("Czas reakcji w funkcji czasu (wszystkie testy)")
        ax.set_xlabel("Data i godzina")
        ax.set_ylabel("Czas reakcji (s)")
        ax.legend()

        output_dir = os.path.join("resources", "output")
        chart_path_history = os.path.join(output_dir, "chart_history.png")
        fig.savefig(chart_path_history)
        return fig, ax, chart_path_history

    def generate_pdf(self, chart_path_current, chart_path_history):
        output_dir = "resources/output"
        results = self.results_manager.get_results()

        from logic.image_processor import resize_image, modify_image_intensity
        import os

        images_for_pdf = []
        for res in results:
            image_name = os.path.basename(res['image_name'])
            img_path = os.path.join("resources", "images", image_name)
            if not os.path.exists(img_path):
                continue
            # Oryginał (miniatura)
            orig_img = resize_image(img_path, 150, 150)
            orig_path = os.path.join(output_dir, f"orig_{res['timestamp']}_{image_name}")
            orig_img.save(orig_path)

            # Obraz z filtrem
            filtered_img = modify_image_intensity(orig_img.copy(), res['intensity'])
            filtered_path = os.path.join(output_dir, f"filtered_{res['timestamp']}_{image_name}")
            filtered_img.save(filtered_path)

            images_for_pdf.append({
                "timestamp": res['timestamp'],
                "image_name": image_name,
                "reaction_time": res['reaction_time'],
                "intensity": res['intensity'],
                "orig_path": orig_path,
                "filtered_path": filtered_path
            })

        pdf_path = os.path.join(output_dir, "report.pdf")

        generate_pdf_with_fallback(pdf_path, images_for_pdf, chart_path_current, chart_path_history)

        messagebox.showinfo("PDF", f"Wygenerowano raport PDF: {pdf_path}")

        # Usunięcie plików tymczasowych
        for file_name in os.listdir(output_dir):
            if file_name.startswith("orig_") or file_name.startswith("filtered_"):
                os.remove(os.path.join(output_dir, file_name))