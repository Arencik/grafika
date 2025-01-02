import tkinter as tk
import time
from PIL import ImageTk
from logic.image_processor import modify_image_intensity, resize_image
from tkinter import messagebox

class TestWindow:
    def __init__(self, master, controller, results_manager, end_callback, test_duration=60):
        self.master = master
        self.controller = controller
        self.results_manager = results_manager
        self.end_callback = end_callback
        self.test_duration = test_duration  # nowy parametr

        self.master.title("Test percepcji barw")
        self.master.geometry("600x500")

        self.frame = tk.Frame(self.master, bg="white")
        self.frame.pack(expand=True, fill="both")

        self.image_label = tk.Label(self.frame, bg="white")
        self.image_label.pack(pady=20)

        self.stop_button = tk.Button(self.frame, text="Przerwij test", command=self.stop_test)
        self.stop_button.pack(side="bottom", pady=20)

        self.current_image_path = None
        self.start_time = None
        self.intensity = 0
        self.direction = 1
        self.timeout_id = None

        # Timer całkowitego czasu testu
        self.total_test_timeout_id = self.master.after(self.test_duration * 1000, self.on_test_time_exceeded)

        self.master.bind("<space>", self.on_space_press)

        self.load_next_image()
        self.update_image_intensity()

    def on_test_time_exceeded(self):
        tk.messagebox.showinfo("Koniec testu", 
            f"Minął wybrany czas testu ({self.test_duration} s). Test zostanie zakończony.")
        self.end_test()

    def load_next_image(self):
        img_path = self.controller.get_next_image()
        if img_path is None:
            self.end_test()
            return
        self.current_image_path = img_path
        self.start_time = time.time()

        # Ustawienie timera timeout (60 sek)
        if self.timeout_id is not None:
            self.master.after_cancel(self.timeout_id)
        self.timeout_id = self.master.after(60000, self.on_timeout)

    def on_timeout(self):
        messagebox.showerror("Timeout", "Czas odpowiedzi przekroczył 60 sekund. Test zostaje przerwany.")
        self.end_test()

    def update_image_intensity(self):
        self.intensity += 5 * self.direction
        if self.intensity >= 255:
            self.intensity = 255
            self.direction = -1
        elif self.intensity <= 0:
            self.intensity = 0
            self.direction = 1

        self.show_image_with_intensity(self.current_image_path, self.intensity)

        self.master.after(100, self.update_image_intensity)

    def show_image_with_intensity(self, path, intensity):
        try:
            # Pobierz wymiary okna i dopasuj obraz
            self.master.update_idletasks()
            w = self.frame.winfo_width()
            h = self.frame.winfo_height() - 100  # odjąć miejsce na przyciski
            img = resize_image(path, w, h)
            img = modify_image_intensity(img, intensity)
            tk_img = ImageTk.PhotoImage(img)
            self.image_label.configure(image=tk_img)
            self.image_label.image = tk_img
        except FileNotFoundError:
            self.stop_test(error=True)

    def on_space_press(self, event):
        reaction_time = time.time() - self.start_time
        current_intensity = self.intensity
        image_name = self.current_image_path.split("/")[-1]

        self.results_manager.add_result(image_name, reaction_time, current_intensity)
        self.load_next_image()

    def stop_test(self, error=False):
        if error:
            messagebox.showerror("Błąd", "Nie można wczytać obrazu.")
        self.end_test()

    def end_test(self):
        # Anuluj timery
        if self.timeout_id is not None:
            self.master.after_cancel(self.timeout_id)
        if self.total_test_timeout_id is not None:
            self.master.after_cancel(self.total_test_timeout_id)

        self.master.destroy()
        self.end_callback()
