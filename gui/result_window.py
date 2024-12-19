import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import csv
import time
from datetime import datetime
from logic.pdf_report import generate_pdf_report
from PIL import Image

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

        canvas2 = FigureCanvasTkAgg(fig2, master=self.charts_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side="right", padx=10, pady=10)

        # Przycisk PDF pod ramką wykresów
        self.pdf_button = tk.Button(self.button_frame, text="Generuj PDF", command=lambda: self.generate_pdf(chart_path_current, chart_path_history))
        self.pdf_button.pack(side="left", padx=10, pady=10)

    def load_all_results(self):
        """
        Load all results from a CSV file.

        This method reads a CSV file located at "resources/output/results.csv" and 
        loads the data into a list of dictionaries. Each dictionary contains the 
        following keys:
            - "timestamp": A float representing the timestamp of the result.
            - "image_name": A string representing the name of the image.
            - "reaction_time": A float representing the reaction time.
            - "intensity": An integer representing the intensity.

        Returns:
            list: A list of dictionaries containing the results. If the CSV file 
            does not exist, an empty list is returned.
        """
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
        """
        Creates a horizontal bar plot of average reaction times for each image in the current test.
        Args:
            results (list of dict): A list of dictionaries where each dictionary contains 'image_name' (str) 
                                    and 'reaction_time' (float) keys representing the image name and the 
                                    reaction time for that image.
        Returns:
            tuple: A tuple containing the following elements:
                - fig (matplotlib.figure.Figure): The created matplotlib figure.
                - ax (matplotlib.axes._axes.Axes): The created matplotlib axes.
                - chart_path_current (str): The file path where the plot image is saved.
        """
        # Obliczamy średni czas reakcji dla każdego obrazu w bieżącym teście
        from statistics import mean
        results_by_image = {}
        for r in results:
            img = r['image_name']
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
        """
        Creates a historical line plot of reaction times over time for different images.
        Parameters:
        all_results (list of dict): A list of dictionaries containing historical results. 
                                    Each dictionary should have keys 'image_name', 'timestamp', and 'reaction_time'.
        current_results (list of dict): A list of dictionaries containing current results. 
                                        Each dictionary should have keys 'image_name', 'timestamp', and 'reaction_time'.
        Returns:
        tuple: A tuple containing the figure object, the axes object, and the path to the saved chart image.
        """
        # Tworzymy liniowy wykres czasu reakcji w funkcji czasu dla poszczególnych obrazów
        # x - czas (datetime), y - czas reakcji, seria - nazwa obrazu
        fig, ax = plt.subplots(figsize=(5,4))

        # Grupowanie historycznych wyników po obrazie
        results_by_image = {}
        for r in all_results:
            img = r['image_name']
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
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
        fig.autofmt_xdate()  # automatyczne pochylanie etykiet

        ax.set_title("Czas reakcji w funkcji czasu (wszystkie testy)")
        ax.set_xlabel("Data i godzina")
        ax.set_ylabel("Czas reakcji (s)")
        ax.legend()

        output_dir = os.path.join("resources", "output")
        chart_path_history = os.path.join(output_dir, "chart_history.png")
        fig.savefig(chart_path_history)
        return fig, ax, chart_path_history

    def generate_pdf(self, chart_path_current, chart_path_history):
        """
        Generates a PDF report containing images and charts.
        This method processes a list of results, resizes and modifies images based on the results,
        and then generates a PDF report that includes these images along with the provided charts.
        Args:
            chart_path_current (str): The file path to the current chart image.
            chart_path_history (str): The file path to the historical chart image.
        Returns:
            None
        Raises:
            FileNotFoundError: If any of the image paths do not exist.
            Exception: If there is an error during the PDF generation process.
        Side Effects:
            Saves resized and modified images to the output directory.
            Generates and saves a PDF report to the output directory.
            Displays a message box with the path to the generated PDF report.
        """
        output_dir = "resources/output"
        results = self.results_manager.get_results()

        from logic.image_processor import resize_image, modify_image_intensity
        images_for_pdf = []
        for res in results:
            image_name = res['image_name'].split("\\")[-1]
            img_path = os.path.join("resources/images", image_name)
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
        generate_pdf_report(pdf_path, images_for_pdf, chart_path_current, chart_path_history)
        messagebox.showinfo("PDF", f"Wygenerowano raport PDF: {pdf_path}")
