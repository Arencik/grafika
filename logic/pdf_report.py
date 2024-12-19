from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
from datetime import datetime

def generate_pdf_report(pdf_path, images_for_pdf, chart_path_current, chart_path_history):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Nagłówek
    c.setTitle("Raport z testu percepcji barw")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "Wyniki testu")

    y_pos = height - 100
    c.setFont("Helvetica", 12)
    # Lista obrazów z miniaturami
    for item in images_for_pdf:
        dt_str = datetime.fromtimestamp(item['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        line = f"Obraz: {item['image_name']} | Czas: {item['reaction_time']:.2f}s | Intensywność: {item['intensity']} | {dt_str}"
        print(line)
        c.drawString(50, y_pos, line)
        y_pos -= 20
        # Rysujemy dwa obrazki: oryginał i filtr obok siebie
        if os.path.exists(item['orig_path']):
            c.drawImage(item['orig_path'], 50, y_pos - 100, width=100, height=100, preserveAspectRatio=True)
        if os.path.exists(item['filtered_path']):
            c.drawImage(item['filtered_path'], 200, y_pos - 100, width=100, height=100, preserveAspectRatio=True)
        y_pos -= 120

    # Wstawiamy wykresy
    c.showPage()
    y_pos = height - 100
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y_pos, "Wykresy")
    c.setFont("Helvetica", 12)

    # Wstawiamy wykres bieżącego testu (bar plot)
    if os.path.exists(chart_path_current):
        c.drawString(50, y_pos - 50, "Czas reakcji dla obrazow (biezacy test) - wykres slupkowy")
        c.drawImage(chart_path_current, 50, y_pos-250, width=300, height=200, preserveAspectRatio=True)
    y_pos -= 300

    if y_pos < 300:
        c.showPage()
        y_pos = height - 50
    if os.path.exists(chart_path_history):
        c.drawString(50, y_pos, "Czas reakcji w funkcji czasu (wszystkie testy)")
        y_pos -= 50
        c.drawImage(chart_path_history, 50, y_pos - 200, width=400, height=200, preserveAspectRatio=True)
        y_pos -= 250

    c.showPage()
    c.save()

    # Czyszczenie plików tymczasowych
    for file_name in os.listdir(os.path.join("resources", "output")):
        if file_name.startswith("orig_") or file_name.startswith("filtered_"):
            os.remove(os.path.join("resources", "output", file_name))