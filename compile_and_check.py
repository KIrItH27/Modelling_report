import os
import subprocess
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(ROOT, "build")


def compile_pdf():
    os.makedirs(BUILD_DIR, exist_ok=True)

    env = os.environ.copy()
    env["BIBINPUTS"] = f"{ROOT};{env.get('BIBINPUTS', '')}"

    # Pass 1: pdflatex
    print("Running pdflatex (Pass 1)...", flush=True)
    subprocess.run(
        [
            "pdflatex",
            "-interaction=nonstopmode",
            "-output-directory", BUILD_DIR,
            "-aux-directory", BUILD_DIR,
            "main.tex",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=ROOT,
        env=env,
    )

    # BibTeX Pass: run bibtex inside build directory
    print("Running bibtex...", flush=True)
    subprocess.run(
        ["bibtex", "main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=BUILD_DIR,
        env=env,
    )

    # Pass 2 & Pass 3: pdflatex to resolve TOC and references completely
    for i in range(2):
        print(f"Running pdflatex (Pass {i+2})...", flush=True)
        subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-output-directory", BUILD_DIR,
                "-aux-directory", BUILD_DIR,
                "main.tex",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=ROOT,
            env=env,
        )

    build_pdf = os.path.join(BUILD_DIR, "main.pdf")
    root_pdf = os.path.join(ROOT, "main.pdf")
    if os.path.exists(build_pdf):
        shutil.copyfile(build_pdf, root_pdf)
        print(f"Successfully compiled and synced: {build_pdf} -> {root_pdf}", flush=True)
        return True
    else:
        print("Error: main.pdf was not generated in build directory!", flush=True)
        return False

def check_toc():
    toc_path = os.path.join(BUILD_DIR, "main.toc")
    if not os.path.exists(toc_path):
        print("TOC file not found.")
        return
    with open(toc_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    chapters = []
    for line in lines:
        m = re.match(r"\\contentsline\s*\{chapter\}\{\\numberline\s*\{(\d+)\}(.*?)\}\{(\d+)\}", line)
        if m:
            ch_num = int(m.group(1))
            ch_title = m.group(2).strip()
            ch_page = int(m.group(3))
            chapters.append((ch_num, ch_title, ch_page))
            
    print("\n--- Current Chapter Starting Pages ---", flush=True)
    for ch_num, ch_title, ch_page in chapters:
        print(f"Chapter {ch_num:2d}: {ch_title:<60} -> Page {ch_page}", flush=True)
    
    # Calculate lengths
    print("\n--- Chapter Page Lengths ---", flush=True)
    for i in range(len(chapters)):
        num, title, page = chapters[i]
        if i < len(chapters) - 1:
            next_page = chapters[i+1][2]
            length = next_page - page
        else:
            length = "Unknown (ends at EOF)"
        print(f"Chapter {num:2d}: {title:<60} -> Length: {length} pages", flush=True)

if __name__ == "__main__":
    if compile_pdf():
        check_toc()


