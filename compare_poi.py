import os
import re

def get_h1_h2(path):
    headings = []
    if not os.path.exists(path): return None
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('# ') or line.startswith('## '):
                # Clean up: remove bolding, trailing spaces, parenthetical translations in JP
                h = line.strip().replace('**', '')
                # Remove common numbering patterns for easier comparison
                h = re.sub(r'^(#+)\s*([0-9A-L.]+)?\s*', r'\1 ', h)
                # Remove Japanese translations in parentheses for JP files
                h = re.sub(r'（[^）]+）', '', h)
                h = re.sub(r'\([^)]+\)', '', h)
                headings.append(h.strip())
    return headings

en_h = get_h1_h2('PoI_theory/PoI_Theory_en.md')
jp_h = get_h1_h2('PoI_theory/PoI_Theory_jp.md')

print(f"EN count: {len(en_h)}, JP count: {len(jp_h)}")
max_len = max(len(en_h), len(jp_h))
for i in range(max_len):
    e = en_h[i] if i < len(en_h) else "MISSING"
    j = jp_h[i] if i < len(jp_h) else "MISSING"
    if e != j:
        # Check if they are just translations
        print(f"Row {i}:")
        print(f"  EN: {e}")
        print(f"  JP: {j}")
