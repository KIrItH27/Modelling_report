import os
import subprocess
import re

ROOT = r"C:\Users\amrut\Modelling_report"
BUILD_DIR = os.path.join(ROOT, "build")


def compile_pdf():
    os.makedirs(BUILD_DIR, exist_ok=True)

    # Only clear the build output artifacts; leave the root PDF alone.
    for stale in ["main.aux", "main.log", "main.out", "main.toc", "main.synctex.gz", "main.pdf", "main_updated.pdf"]:
        path = os.path.join(BUILD_DIR, stale)
        if os.path.exists(path):
            os.remove(path)

    # Run pdflatex twice to resolve references and TOC, writing all generated files into build/
    for i in range(2):
        print(f"Running pdflatex (Pass {i+1})...")
        res = subprocess.run(
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
        )
        if res.returncode != 0:
            print("Compilation error!")
            print(res.stdout[-1000:])
            return False
    return True

def check_toc():
    toc_path = os.path.join(BUILD_DIR, "main.toc")
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
            
    print("\n--- Current Chapter Starting Pages ---")
    for ch_num, ch_title, ch_page in chapters:
        print(f"Chapter {ch_num:2d}: {ch_title:<60} -> Page {ch_page}")
    
    # Calculate lengths
    print("\n--- Chapter Page Lengths ---")
    for i in range(len(chapters)):
        num, title, page = chapters[i]
        if i < len(chapters) - 1:
            next_page = chapters[i+1][2]
            length = next_page - page
        else:
            length = "Unknown (ends at EOF)"
        print(f"Chapter {num:2d}: {title:<60} -> Length: {length} pages")

if __name__ == "__main__":
    if compile_pdf():
        check_toc()
