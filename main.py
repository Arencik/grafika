import tkinter as tk
from gui.main_window import MainWindow

def main():
    import sys
    root = tk.Tk()

    def on_close():
        root.destroy()
        sys.exit(0)  # wymusza zakończenie interpretacji

    root.protocol("WM_DELETE_WINDOW", on_close)

    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
