# logic/latex_report.py
import os
import subprocess

LATEX_HEADER = r"""
\documentclass[a4paper,12pt]{article}
\usepackage{WSPARap}
\usepackage{graphicx}
\usepackage{float}
\usepackage[utf8]{inputenc}  % by zadbać o polskie znaki
\renewcommand{\tytulCw}{Grafika Wektorowa}
\renewcommand{\Autor}{Program testujący}
\renewcommand{\Studenci}{Generator Raportu}
\renewcommand{\Szkola}{Wyższa Szkoła Przedsiębiorczości i Administracji}
\renewcommand{\lab}{Zaawansowane przetwarzanie obrazów cyfrowych}
\renewcommand{\grlab}{Gr-1}
\renewcommand{\Data}{06-11-2024}

\begin{document}
\RapPage
"""

LATEX_FOOTER = r"""
\end{document}
"""

def generate_latex_report(pdf_path, images_for_pdf, chart_path_current, chart_path_history):
    """
    Generuje plik .tex z odpowiednimi sekcjami i wywołuje pdflatex,
    aby uzyskać finalny plik PDF.
    """
    # 1) Nazwa pliku .tex (tymczasowego)
    tex_path = pdf_path.replace(".pdf", ".tex")
    if not tex_path.endswith(".tex"):
        tex_path += ".tex"

    # 2) Zbuduj zawartość sekcji (LaTeX)
    # -- Sekcja pierwsza: obrazy z wynikami
    section_images = [r"\section{Poszczegolne obrazy}"]
    for item in images_for_pdf:
        line = (
            f"Obraz: {item['image_name']}, czas: {item['reaction_time']:.2f}s, "
            f"intensywność: {item['intensity']}, timestamp: {item['timestamp']}."
        )
        section_images.append(line)
        # wstawiamy oryginał i filtr obok siebie
        # \includegraphics[width=0.3\textwidth]{...}
        orig_rel = os.path.relpath(item['orig_path'], start=os.path.dirname(tex_path))
        filtered_rel = os.path.relpath(item['filtered_path'], start=os.path.dirname(tex_path))

        section_images.append(r"\begin{figure}[H]")
        section_images.append(r"\centering")
        section_images.append(fr"\includegraphics[width=0.35\textwidth]{{{orig_rel}}}")
        section_images.append(r"\hspace{1cm}")
        section_images.append(fr"\includegraphics[width=0.35\textwidth]{{{filtered_rel}}}")
        section_images.append(fr"\caption*{{{line}}}")
        section_images.append(r"\end{figure}")

    # -- Sekcja druga: wykresy
    section_charts = [r"\section{Wykresy}"]

    # Wykres bieżącego testu
    if os.path.exists(chart_path_current):
        chart_current_rel = os.path.relpath(chart_path_current, start=os.path.dirname(tex_path))
        section_charts.append(r"\begin{figure}[H]")
        section_charts.append(r"\centering")
        section_charts.append(fr"\includegraphics[width=0.6\textwidth]{{{chart_current_rel}}}")
        section_charts.append(r"\caption*{Wykres bieżącego testu}")
        section_charts.append(r"\end{figure}")

    # Wykres historyczny
    if os.path.exists(chart_path_history):
        chart_history_rel = os.path.relpath(chart_path_history, start=os.path.dirname(tex_path))
        section_charts.append(r"\begin{figure}[H]")
        section_charts.append(r"\centering")
        section_charts.append(fr"\includegraphics[width=0.6\textwidth]{{{chart_history_rel}}}")
        section_charts.append(r"\caption*{Wykres historyczny (wszystkie testy)}")
        section_charts.append(r"\end{figure}")

    # 3) Sklejamy pełną zawartość pliku .tex
    latex_content = (
        LATEX_HEADER + "\n" +
        "\n".join(section_images) + "\n" +
        "\n".join(section_charts) + "\n" +
        LATEX_FOOTER
    )

    # 4) Zapisujemy do pliku .tex
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_content)

    # 5) Kompilujemy do PDF (pdflatex dwukrotnie, by spis rysunków był aktualny, jeśli potrzeba)
    #    Tutaj minimalnie raz wystarczy, ale czasem warto 2x w LaTeX.
    try:
        # Wykonujemy w katalogu, gdzie znajduje się nasz plik .tex
        workdir = os.path.dirname(tex_path) if os.path.dirname(tex_path) else "."
        cmd = ["pdflatex", "-interaction=nonstopmode", os.path.basename(tex_path)]
        subprocess.run(cmd, check=True, cwd=workdir)
        # Można drugi raz:
        subprocess.run(cmd, check=True, cwd=workdir)
    except subprocess.CalledProcessError as e:
        print("Błąd podczas kompilowania LaTeX:", e)

    # 6) Możemy posprzątać pliki tymczasowe (.aux, .log, itp.)
    base_filename = os.path.splitext(os.path.basename(tex_path))[0]
    for ext in [".aux", ".log", ".out", ".toc"]:
        tmp_file = os.path.join(workdir, base_filename + ext)
        if os.path.exists(tmp_file):
            os.remove(tmp_file)

    # 7) (Opcjonalnie) przeniesienie powstałego PDF w docelowe miejsce
    #    W praktyce plik pdf wygeneruje się obok .tex, w `pdf_path` (jeśli jest tam sam plik).
    #    Zwykle pdflatex tworzy pdf o tej samej nazwie co .tex (czyli base_filename + ".pdf").
    #    Sprawdzamy, czy jest on tam i czy trzeba go przenieść:
    generated_pdf = os.path.join(workdir, base_filename + ".pdf")
    if os.path.exists(generated_pdf) and generated_pdf != pdf_path:
        os.rename(generated_pdf, pdf_path)

    print("[INFO] Wygenerowano PDF:", pdf_path)
