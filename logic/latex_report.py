import datetime
import os
import subprocess
import shutil

from reportlab.lib.pagesizes import A4

from logic.pdf_report import generate_pdf_report

########################################
# 1) Funkcja do sprawdzenia dostępności LaTeX
########################################

def is_latex_installed():
    """
    Zwraca True, jeśli w systemie dostępne jest polecenie 'pdflatex'.
    """
    latex_path = shutil.which("pdflatex")  # None, jeśli nie znaleziono
    return latex_path is not None

########################################
# 2) Oryginalna funkcja od generowania LaTeX
########################################

LATEX_HEADER = r"""
\documentclass[a4paper,12pt]{article}
\usepackage{WSPARap}
\usepackage{graphicx}
\usepackage{float}
\usepackage[utf8]{inputenc}  
\renewcommand{\tytulCw}{Raport percepji barw}
\renewcommand{\Autor}{Program testujący}
\renewcommand{\Studenci}{Generator raportów}
\renewcommand{\Szkola}{Wyższa Szkoła Przedsiębiorczości i Administracji}
\renewcommand{\lab}{Raport z testu}
\renewcommand{\grlab}{Gr-5}
\renewcommand{\Data}{"""+f"{datetime.datetime.now().strftime('%d-%m-%Y')}"+r"""}

\begin{document}
\RapPage
"""

LATEX_FOOTER = r"""
\end{document}
"""

def generate_latex_report(pdf_path, images_for_pdf, chart_path_current, chart_path_history):
    """
    Generowanie PDF przez LaTeX (patrz poprzednie przykłady).
    """
    tex_path = pdf_path.replace(".pdf", ".tex")
    if not tex_path.endswith(".tex"):
        tex_path += ".tex"

    section_images = [r"\section{Poszczegolne obrazy}"]
    for item in images_for_pdf:
        line = (
            f"Obraz: {item['image_name']}, czas: {item['reaction_time']:.2f}s, "
            f"intensywność: {item['intensity']}."
        )
        section_images.append(line)
        section_images.append(r"\begin{figure}[H]")
        section_images.append(r"\centering")

        # relatywne ścieżki do pliku .tex
        orig_rel = os.path.basename(item['orig_path'])
        filtered_rel = os.path.basename(item['filtered_path'])

        section_images.append(fr"\includegraphics[width=0.35\textwidth]{{{orig_rel}}}")
        section_images.append(r"\hspace{1cm}")
        section_images.append(fr"\includegraphics[width=0.35\textwidth]{{{filtered_rel}}}")
        section_images.append(fr"\caption*{{{line}}}")
        section_images.append(r"\end{figure}")

    section_charts = [r"\section{Wykresy}"]
    if os.path.exists(chart_path_current):
        chart_current_rel = os.path.basename(chart_path_current)
        section_charts.append(r"\begin{figure}[H]")
        section_charts.append(r"\centering")
        section_charts.append(fr"\includegraphics[width=0.6\textwidth]{{{chart_current_rel}}}")
        section_charts.append(r"\caption*{{Wykres bieżącego testu}}")
        section_charts.append(r"\end{figure}")

    if os.path.exists(chart_path_history):
        chart_history_rel = os.path.basename(chart_path_history)
        section_charts.append(r"\begin{figure}[H]")
        section_charts.append(r"\centering")
        section_charts.append(fr"\includegraphics[width=0.6\textwidth]{{{chart_history_rel}}}")
        section_charts.append(r"\caption*{{Wykres historyczny (wszystkie testy)}}")
        section_charts.append(r"\end{figure}")

    latex_content = (
        LATEX_HEADER + "\n" +
        "\n".join(section_images) + "\n" +
        "\n".join(section_charts) + "\n" +
        LATEX_FOOTER
    )

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_content)

    sty_sources = ["resources/latex/WSPARap.sty", "resources/latex/logoWSPA.png"]
    workdir = os.path.dirname(tex_path) if os.path.dirname(tex_path) else "."
    for src in sty_sources:
        if os.path.exists(src):
            shutil.copy(src, os.path.join(workdir, src.split("/")[-1]))

    # Kompilacja LaTeX
    cmd = ["pdflatex", "-interaction=nonstopmode", os.path.basename(tex_path)]
    try:
        subprocess.run(cmd, check=True, cwd=workdir)
        subprocess.run(cmd, check=True, cwd=workdir)
    except subprocess.CalledProcessError as e:
        print("Błąd podczas kompilacji LaTeX:", e)

    # Sprzątanie
    base_filename = os.path.splitext(os.path.basename(tex_path))[0]
    for ext in [".aux", ".log", ".out", ".toc"]:
        tmp_file = os.path.join(workdir, base_filename + ext)
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
    for src in sty_sources:
        if os.path.exists(os.path.join(workdir, src.split("/")[-1])):
            os.remove(os.path.join(workdir, src.split("/")[-1]))

    # Przeniesienie powstałego PDF
    generated_pdf = os.path.join(workdir, base_filename + ".pdf")
    if os.path.exists(generated_pdf) and generated_pdf != pdf_path:
        os.rename(generated_pdf, pdf_path)

    print("[INFO] Wygenerowano PDF (LaTeX):", pdf_path)


########################################
# 4) Jedna spójna funkcja: generate_pdf_with_fallback
########################################

def generate_pdf_with_fallback(pdf_path, images_for_pdf, chart_path_current, chart_path_history):
    """
    Próbuje wygenerować PDF za pomocą LaTeX-a.
    Jeśli nie jest dostępny, generuje uproszczony PDF w reportlab.
    """
    if is_latex_installed():
        print("[INFO] LaTeX jest dostępny, generujemy PDF przez LaTeX.")
        generate_latex_report(pdf_path, images_for_pdf, chart_path_current, chart_path_history)
    else:
        print("[WARN] LaTeX nie jest dostępny. Generujemy uproszczony PDF (fallback).")
        generate_pdf_report(pdf_path, images_for_pdf, chart_path_current, chart_path_history)
