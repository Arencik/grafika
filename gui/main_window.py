import tkinter as tk
from tkinter import messagebox
from gui.test_window import TestWindow
from logic.test_controller import TestController
from logic.results_manager import ResultsManager
import os

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Test percepcji barw")
        self.master.geometry("300x150")

        self.frame = tk.Frame(self.master)
        self.frame.pack(expand=True, fill="both")

        self.start_button = tk.Button(
            self.frame, text="Start testu", command=self.start_test)
        self.start_button.pack(pady=20)

        self.controller = TestController()
        self.results_manager = ResultsManager()

    def start_test(self):
        images_path = os.path.join("resources", "images")
        if not os.path.exists(images_path):
            messagebox.showerror("Błąd", "Brak katalogu z obrazami testowymi.")
            return

        test_images = os.listdir(images_path)
        test_images = [os.path.join(images_path, img) for img in test_images if os.path.exists(os.path.join(images_path, img))]

        if len(test_images) == 0:
            messagebox.showerror("Błąd", "Brak obrazów do testu.")
            return

        self.controller.setup_test(test_images, num_iterations=4)

        self.new_window = tk.Toplevel(self.master)
        self.test_window = TestWindow(self.new_window, self.controller, self.results_manager, self.on_test_end)

    def on_test_end(self):
        from gui.result_window import ResultWindow
        result_window = tk.Toplevel(self.master)
        ResultWindow(result_window, self.results_manager)
