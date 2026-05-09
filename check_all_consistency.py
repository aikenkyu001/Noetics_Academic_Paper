import os
import glob
from datetime import datetime

def check_consistency():
    md_files = glob.glob("**/*.md", recursive=True)
    results = []
    
    # Files to ignore (READMEs, or other meta files)
    ignore_list = ["README.md", "page.md", "en_headers.txt", "jp_headers.txt", "en_poi.txt", "jp_poi.txt"]
    
    for md_path in md_files:
        if os.path.basename(md_path) in ignore_list:
            continue
            
        base_dir = os.path.dirname(md_path)
        base_name = os.path.basename(md_path)
        
        # Determine expected PDF name
        # Patterns:
        # file_en.md -> file_en.pdf or file.pdf
        # file_jp.md -> file_jp.pdf or file.pdf
        # file.md -> file.pdf
        
        expected_pdfs = []
        if base_name.endswith("_en.md"):
            expected_pdfs.append(base_name.replace("_en.md", "_en.pdf"))
            expected_pdfs.append(base_name.replace("_en.md", ".pdf"))
        elif base_name.endswith("_jp.md"):
            expected_pdfs.append(base_name.replace("_jp.md", "_jp.pdf"))
            expected_pdfs.append(base_name.replace("_jp.md", ".pdf"))
        elif base_name.endswith("_ja.md"):
            expected_pdfs.append(base_name.replace("_ja.md", "_ja.pdf"))
            expected_pdfs.append(base_name.replace("_ja.md", ".pdf"))
        else:
            expected_pdfs.append(base_name.replace(".md", ".pdf"))
            
        found_pdf = None
        for pdf_name in expected_pdfs:
            pdf_path = os.path.join(base_dir, pdf_name)
            if os.path.exists(pdf_path):
                found_pdf = pdf_path
                break
                
        status = "OK"
        md_time = os.path.getmtime(md_path)
        
        if not found_pdf:
            status = "MISSING PDF"
        else:
            pdf_time = os.path.getmtime(found_pdf)
            if md_time > pdf_time + 1: # 1 second buffer
                status = "OUTDATED PDF"
                
        results.append({
            "md": md_path,
            "pdf": found_pdf if found_pdf else "N/A",
            "status": status,
            "md_date": datetime.fromtimestamp(md_time).strftime('%Y-%m-%d %H:%M:%S'),
            "pdf_date": datetime.fromtimestamp(os.path.getmtime(found_pdf)).strftime('%Y-%m-%d %H:%M:%S') if found_pdf else "N/A"
        })
        
    return results

if __name__ == "__main__":
    results = check_consistency()
    
    print(f"{'MD File':<60} | {'Status':<12} | {'PDF File'}")
    print("-" * 120)
    
    missing = []
    outdated = []
    
    for r in sorted(results, key=lambda x: x['status']):
        if r['status'] == "OK":
            continue
        print(f"{r['md']:<60} | {r['status']:<12} | {r['pdf']}")
        if r['status'] == "MISSING PDF":
            missing.append(r)
        else:
            outdated.append(r)
            
    print("-" * 120)
    print(f"Total MD files checked: {len(results)}")
    print(f"Missing PDFs: {len(missing)}")
    print(f"Outdated PDFs: {len(outdated)}")
