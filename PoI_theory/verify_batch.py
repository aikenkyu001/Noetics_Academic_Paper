import sys
import re
import glob
import os
from pdfminer.high_level import extract_text

def compare_files(md_path, pdf_path):
    label = md_path
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        bold_parts = re.findall(r'\*\*(.*?)\*\*', md_content)
        pdf_text = extract_text(pdf_path)
        pdf_text_clean = " ".join(pdf_text.split())
        
        results = []
        for part in bold_parts:
            clean_part = " ".join(re.sub(r"[*_`]", "", part).strip().split())
            if not clean_part or len(clean_part) < 3: continue
            if clean_part in pdf_text_clean:
                results.append(True)
            else:
                if any(x in clean_part for x in ["Author", "著者", "Date", "日付", "Keywords", "キーワード", "Repository"]):
                    continue
                results.append(False)
        
        total = len(results)
        matches = sum(results)
        percentage = (matches / total * 100) if total > 0 else 100
        return label, percentage, total - matches
    except Exception as e:
        return label, 0, str(e)

def main():
    files = glob.glob("*.md")
    header = f"{'File':<50} | {'Match %':<10} | {'Missing Bolds'}"
    print(header)
    print("-" * len(header))
    for md_f in sorted(files):
        is_jp = md_f.endswith("_jp.md")
        base = md_f[:-6] if is_jp else md_f[:-3]
        pdf_f = base + ("_jp.pdf" if is_jp else ".pdf")
        if os.path.exists(pdf_f):
            label, pct, missing = compare_files(md_f, pdf_f)
            print(f"{label:<50} | {pct:>8.1f}% | {missing}")

if __name__ == "__main__":
    main()
