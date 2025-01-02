# gui/main_window.py

import tkinter as tk
from tkinter import ttk  # aby użyć np. ttk.Combobox, jeżeli wolisz
from gui.test_window import TestWindow
from logic.test_controller import TestController
from logic.results_manager import ResultsManager
import os

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Test percepcji barw")
        self.master.geometry("400x250")  # może minimalnie większe

        # Główna ramka
        self.frame = tk.Frame(self.master, bg="lightblue")  # troszkę koloru
        self.frame.pack(expand=True, fill="both")

        # Logo (opcjonalnie, jeśli masz plik logo.png)
        try:
            self.logo_img = tk.PhotoImage(file="resources/images/2.jpg")
            self.logo_label = tk.Label(self.frame, image=self.logo_img, bg="lightblue")
            self.logo_label.pack(pady=5)
        except:
            pass  # Jeśli nie masz pliku logo, po prostu pomiń

        # Dropdown z kanałami
        self.channel_var = tk.StringVar(value="blue")  # domyślny kanał
        self.channels = ["red", "green", "blue"]

        tk.Label(self.frame, text="Wybierz kanał:", bg="lightblue").pack()
        self.channel_menu = tk.OptionMenu(self.frame, self.channel_var, *self.channels)
        self.channel_menu.pack(pady=5)

        # Pasek wyboru czasu testu
        tk.Label(self.frame, text="Czas trwania testu (sekundy):", bg="lightblue").pack()
        self.test_duration_var = tk.IntVar(value=60)
        self.test_duration_scale = tk.Scale(self.frame, from_=10, to=300, orient="horizontal", 
                                            variable=self.test_duration_var, bg="lightblue")
        self.test_duration_scale.pack(pady=5)

        # Przycisk Start
        self.start_button = tk.Button(self.frame, text="Start testu", command=self.start_test)
        self.start_button.pack(pady=10)

        # Przycisk PDF z poprzednich testów
        self.pdf_button = tk.Button(self.frame, text="Generuj PDF z poprzednich testów", 
                                    command=self.generate_pdf_from_history)
        self.pdf_button.pack(pady=5)

        self.controller = TestController()
        self.results_manager = ResultsManager()

    def start_test(self):
        images_path = os.path.join("resources", "images")
        if not os.path.exists(images_path):
            tk.messagebox.showerror("Błąd", "Brak katalogu z obrazami testowymi.")
            return

        test_images = os.listdir(images_path)
        test_images = [os.path.join(images_path, img) for img in test_images 
                       if os.path.exists(os.path.join(images_path, img))]
        if len(test_images) == 0:
            tk.messagebox.showerror("Błąd", "Brak obrazów do testu.")
            return

        # Pobieramy wartości z dropdown i slidera
        chosen_channel = self.channel_var.get()
        test_duration = self.test_duration_var.get()

        # Ustawiamy test
        self.controller.setup_test(test_images, num_iterations=4, channel=chosen_channel)

        self.new_window = tk.Toplevel(self.master)
        self.test_window = TestWindow(self.new_window, 
                                      self.controller, 
                                      self.results_manager,
                                      self.on_test_end,
                                      test_duration=test_duration)

    def on_test_end(self):
        from gui.result_window import ResultWindow
        result_window = tk.Toplevel(self.master)
        ResultWindow(result_window, self.results_manager)

    def generate_pdf_from_history(self):
        """
        Funkcja, która generuje PDF z istniejących historycznych danych
        (jeśli takie istnieją).
        """
        # Wczytaj wszystkie wyniki z pliku CSV
        from gui.result_window import ResultWindow
        all_results = self.load_all_results()

        if not all_results:
            tk.messagebox.showinfo("PDF", "Brak historycznych wyników do wygenerowania PDF.")
            return

        # Sztucznie „podrzucimy” te dane do results_managera,
        # a następnie wywołamy okno z generowaniem PDF.
        temp_manager = ResultsManager() 
        temp_manager.results = all_results

        dummy_window = tk.Toplevel(self.master)
        dummy_window.withdraw()  # Ukryj okno
        rw = ResultWindow(dummy_window, temp_manager)

    def load_all_results(self):
        """
        Pomocnicza funkcja do wczytania wszystkich rezultatów z CSV.
        """
        import csv
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
