import os
import re
import subprocess

def tex_escape(text):
    conv = {
        '&': r'\&',
        '%': r'\%',
        '#': r'\#',
        '$': r'\$',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '—': r'---',
        '–': r'--'
    }
    parts = re.split(r'(\$\$.*?\$\$|\$.*?\$)', text, flags=re.DOTALL)
    res = ""
    for part in parts:
        if part.startswith('$'):
            res += part
        else:
            temp = part
            for char, escape in conv.items():
                temp = temp.replace(char, escape)
            res += temp
    return res

def inline_format(text):
    parts = re.split(r'(\$\$.*?\$\$|\$.*?\$)', text, flags=re.DOTALL)
    res_parts = []
    for part in parts:
        if part.startswith('$'):
            res_parts.append(part)
        else:
            t = part
            t = re.sub(r'\[(.*?)\]\((.*?)\)', lambda m: f"\\href{{{m.group(2)}}}{{{m.group(1)}}}", t)
            t = re.sub(r'\*\*\*(.*?)\*\*\*', r'\\textbf{\\textit{\1}}', t)
            t = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', t)
            t = re.sub(r'\*(.*?)\*', r'\\textit{\1}', t)
            res_parts.append(t)
    return "".join(res_parts)

def clean_header(text):
    # Strictly remove manual numbering if it still exists
    return re.sub(r'^[\d\.]+\s+', '', text).strip()

def clean_caption(caption):
    caption = re.sub(r'^[\*\s]*(?:\*\*|)\s*(?:Fig\.|Figure|Fig)\s*\d+[:.]?\s*(?:\*\*|)\s*', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\s*\*\*\s*$', '', caption)
    caption = re.sub(r'^\*\[', '', caption)
    caption = re.sub(r'\]\*$', '', caption)
    return caption.strip().rstrip('.')

def convert_table(lines):
    if len(lines) < 3: return ""
    filtered_lines = [l for l in lines if not re.match(r'^\|[- :|]+\|$', l)]
    if not filtered_lines: return ""
    
    headers = [inline_format(tex_escape(h.strip())) for h in filtered_lines[0].strip('|').split('|')]
    num_cols = len(headers)
    tex = [r"\begin{table}[htbp]\centering"]
    tex.append(r"\begin{tabular}{" + "l" * num_cols + "}")
    tex.append(r"\hline")
    tex.append(" & ".join(headers) + r" \\ \hline")
    for line in filtered_lines[1:]:
        cols = [inline_format(tex_escape(c.strip())) for c in line.strip('|').split('|')]
        if len(cols) < num_cols: cols += [""] * (num_cols - len(cols))
        else: cols = cols[:num_cols]
        tex.append(" & ".join(cols) + r" \\")
    tex.append(r"\hline")
    tex.append(r"\end{tabular}")
    tex.append(r"\end{table}")
    return "\n".join(tex)

def main():
    import sys
    if len(sys.argv) > 1:
        md_path = sys.argv[1]
    else:
        md_path = "morphic_autonomy_lab_en.md"
        
    if not os.path.exists(md_path):
        print(f"File not found: {md_path}")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Metadata
    title_m = re.search(r'^# (.*)', content, re.M)
    title = clean_header(title_m.group(1)) if title_m else "Untitled"
    author_m = re.search(r'\*\*Author:\*\* (.*)', content)
    author = author_m.group(1).strip() if author_m else ""
    date_m = re.search(r'\*\*Date:\*\* (.*)', content)
    date = date_m.group(1).strip() if date_m else ""
    keywords_m = re.search(r'\*\*Keywords:\*\* (.*)', content)
    keywords = keywords_m.group(1).strip() if keywords_m else ""
    
    # Abstract
    abstract_m = re.search(r'### (?:Abstract|概要 \(Abstract\))\s+(.*?)\s+(?:---|# )', content, re.S)
    abstract_text = abstract_m.group(1).strip() if abstract_m else ""
    # Remove any keywords line from abstract text
    abstract_text = re.sub(r'^\s*\*\*Keywords:\*\*.*?\n', '', abstract_text, flags=re.MULTILINE | re.IGNORECASE)
    abstract = inline_format(tex_escape(abstract_text))

    # Body
    body_start_match = re.search(r'^# [0-9]+\s+(?:Introduction|はじめに)', content, re.M | re.I)
    if body_start_match:
        body_content = content[body_start_match.start():]
    else:
        # Fallback: search for the first section after the first separator
        sep_pos = content.find('---', content.find('Abstract') if 'Abstract' in content else 0)
        if sep_pos != -1:
            body_content = content[sep_pos + 3:]
        else:
            body_content = content

    lines = body_content.split('\n')
    tex_body = []
    in_list = None
    in_table = False
    table_buffer = []
    in_refs = False

    i = 0
    while i < len(lines):
        line = lines[i]
        trimmed = line.strip()
        if not trimmed:
            if in_list: tex_body.append(f"\\end{{{in_list}}}"); in_list = None
            if in_table: tex_body.append(convert_table(table_buffer)); table_buffer = []; in_table = False
            tex_body.append("\n")
            i += 1
            continue
        
        if trimmed.startswith('|'):
            in_table = True
            table_buffer.append(trimmed)
            i += 1
            continue
        elif in_table:
            tex_body.append(convert_table(table_buffer))
            table_buffer = []
            in_table = False

        if trimmed == "---":
            i += 1
            continue
        
        if "©" in trimmed and "All Rights Reserved" in trimmed:
            i += 1
            continue

        if trimmed.startswith('# '):
            if in_list: tex_body.append(f"\\end{{{in_list}}}"); in_list = None
            h_text = clean_header(trimmed[2:])
            if "References" in h_text or "参考文献" in h_text:
                in_refs = True
                tex_body.append(r"\begin{thebibliography}{99}")
            else:
                tex_body.append(f"\\section{{{tex_escape(h_text)}}}")
            i += 1
            continue
        elif trimmed.startswith('## '):
            if in_list: tex_body.append(f"\\end{{{in_list}}}"); in_list = None
            tex_body.append(f"\\subsection{{{tex_escape(clean_header(trimmed[3:]))}}}")
            i += 1
            continue
        elif trimmed.startswith('### '):
            if in_list: tex_body.append(f"\\end{{{in_list}}}"); in_list = None
            tex_body.append(f"\\subsubsection{{{tex_escape(clean_header(trimmed[4:]))}}}")
            i += 1
            continue

        if trimmed.startswith('!['):
            if in_list: tex_body.append(f"\\end{{{in_list}}}"); in_list = None
            m = re.match(r'!\[(.*?)\]\((.*?)\)', trimmed)
            if m:
                cap_raw, path = m.groups()
                pdf_path = path.replace('.png', '.pdf')
                if os.path.exists(pdf_path): path = pdf_path
                desc = clean_caption(cap_raw)
                tex_body.append(r"\begin{figure}[htbp]\centering")
                tex_body.append(f"\\includegraphics[width=0.8\\textwidth,height=0.35\\textheight,keepaspectratio]{{{path}}}")
                tex_body.append(f"\\caption{{{tex_escape(desc)}}}")
                tex_body.append(r"\end{figure}")
            i += 1
            continue

        if re.match(r'^\d+\.\s+', trimmed) or trimmed.startswith('- ') or trimmed.startswith('* '):
            list_type = 'enumerate' if re.match(r'^\d+\.\s+', trimmed) else 'itemize'
            if not in_refs:
                if in_list != list_type:
                    if in_list: tex_body.append(f"\\end{{{in_list}}}")
                    tex_body.append(f"\\begin{{{list_type}}}")
                    in_list = list_type
            
            content_text = re.sub(r'^(\d+\.\s+|- |\* )', '', trimmed)
            if in_refs:
                key = "".join(filter(str.isalnum, content_text[:15])) + str(i)
                tex_body.append(f"\\bibitem{{{key}}} {inline_format(tex_escape(content_text))}")
            else:
                tex_body.append(f"\\item {inline_format(tex_escape(content_text))}")
            i += 1
            continue

        tex_body.append(inline_format(tex_escape(trimmed)))
        i += 1

    if in_list: tex_body.append(f"\\end{{{in_list}}}")
    if in_refs: tex_body.append(r"\end{thebibliography}")

    full_tex = r'''\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{unicode-math}
\usepackage{url}
\usepackage{xurl}
\usepackage{hyperref}
\usepackage{geometry}
\usepackage{enumitem}
\usepackage{authblk}

\geometry{margin=1in}
\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=cyan}

\title{''' + tex_escape(title) + r'''}
\author{''' + tex_escape(author) + r'''}
\date{''' + tex_escape(date) + r'''}

\begin{document}
\maketitle

\begin{abstract}
''' + abstract + r'''
\end{abstract}

''' + (f"\\textbf{{Keywords:}} {tex_escape(keywords)}\n" if keywords else "") + r'''

''' + '\n'.join(tex_body) + r'''

\end{document}
'''
    base_name = os.path.splitext(md_path)[0]
    # Strip language suffix for the output filename if present
    out_base = re.sub(r'_(?:en|jp)$', '', base_name)
    tex_file = f"{out_base}.tex"
    with open(tex_file, "w", encoding='utf-8') as f:
        f.write(full_tex)

    print(f"Running xelatex on {tex_file}...")
    subprocess.run(["xelatex", "-interaction=nonstopmode", tex_file], capture_output=True)
    subprocess.run(["xelatex", "-interaction=nonstopmode", tex_file], capture_output=True)
    print(f"Successfully generated {out_base}.pdf")

if __name__ == "__main__":
    main()
