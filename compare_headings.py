import os
import re

def get_headings(path):
    headings = []
    if not os.path.exists(path): return None
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                # Strip symbols and bolding just in case
                h = line.strip().replace('**', '')
                headings.append(h)
    return headings

pairs = [
    ('Noetics_en.md', 'Noetics_jp.md'),
    ('Parallel_Key_Geometric_Flow_en.md', 'Parallel_Key_Geometric_Flow_jp.md'),
    ('PKGF_Finite_Dimensional_en.md', 'PKGF_Finite_Dimensional_jp.md'),
    ('PKGF_Generic_Onsager_en.md', 'PKGF_Generic_Onsager_jp.md'),
    ('PKGF_Nonlinear_Extensions_en.md', 'PKGF_Nonlinear_Extensions_jp.md'),
    ('PKGF_Spectral_Flow_Unified_Phase_en.md', 'PKGF_Spectral_Flow_Unified_Phase_jp.md'),
    ('PKGF_structural_correspondence_modern_physics_en.md', 'PKGF_structural_correspondence_modern_physics_jp.md'),
    ('PoI_Theory_en.md', 'PoI_Theory_jp.md')
]

for en_name, jp_name in pairs:
    en_path = os.path.join('PoI_theory', en_name)
    jp_path = os.path.join('PoI_theory', jp_name)
    
    en_h = get_headings(en_path)
    jp_h = get_headings(jp_path)
    
    print(f"--- Comparing {en_name} and {jp_name} ---")
    if en_h is None or jp_h is None:
        print("One or both files missing.")
        continue
    
    if len(en_h) != len(jp_h):
        print(f"DIFFERENT NUMBER OF HEADINGS: EN={len(en_h)}, JP={len(jp_h)}")
        max_len = max(len(en_h), len(jp_h))
        for i in range(max_len):
            e = en_h[i] if i < len(en_h) else "MISSING"
            j = jp_h[i] if i < len(jp_h) else "MISSING"
            # Only print if they seem different (ignoring language)
            # A simple heuristic: check if level and numbers match
            e_prefix = re.match(r'^(#+)\s*([0-9.]+)?', e)
            j_prefix = re.match(r'^(#+)\s*([0-9.]+)?', j)
            if e_prefix and j_prefix:
                if e_prefix.groups() != j_prefix.groups():
                    print(f"  Row {i}: EN: {e} | JP: {j}")
            else:
                print(f"  Row {i}: EN: {e} | JP: {j}")
    else:
        print("Heading count matches.")
        # Optional: check internal numbering
        for i in range(len(en_h)):
            e_prefix = re.match(r'^(#+)\s*([0-9.]+)?', en_h[i])
            j_prefix = re.match(r'^(#+)\s*([0-9.]+)?', jp_h[i])
            if e_prefix and j_prefix:
                if e_prefix.groups() != j_prefix.groups():
                    print(f"  Mismatch at Row {i}: EN: {en_h[i]} | JP: {jp_h[i]}")
