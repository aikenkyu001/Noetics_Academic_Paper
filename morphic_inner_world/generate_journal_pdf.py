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
    # real markdown link conversion first
    text = re.sub(r'\[(.*?)\]\((.*?)\)', lambda m: f"\\href{{{m.group(2)}}}{{{m.group(1)}}}", text)
    # Bold/Italic
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
    return text

def clean_caption(caption):
    # Remove leading Fig descriptors
    caption = re.sub(r'^(?:\*\*|)\s*(?:Fig\.|Figure|Fig)\s*\d+[:.]?\s*(?:\*\*|)\s*', '', caption, flags=re.IGNORECASE)
    # Remove trailing ** if any
    caption = re.sub(r'\s*\*\*\s*$', '', caption)
    caption = caption.strip().rstrip('.')
    return caption

def convert_table(lines):
    if len(lines) < 3: return ""
    # Filter separator line |---|
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
    md_path = "morphic_inner_world_en.md"
    if not os.path.exists(md_path): return

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Metadata
    title = re.search(r'^# (.*)', content, re.M).group(1).strip()
    author = re.search(r'\*\*Author:\*\* (.*)', content).group(1).strip()
    date = re.search(r'\*\*Date:\*\* (.*)', content).group(1).strip()
    keywords = re.search(r'\*\*Keywords:\*\* (.*)', content).group(1).strip()
    
    # Abstract
    abstract_m = re.search(r'## Abstract\s+(.*?)\s+(?:---|\n## )', content, re.S)
    abstract = abstract_m.group(1).strip() if abstract_m else ""

    # Body - start from Introduction
    body_start_match = re.search(r'## 1\. Introduction', content)
    if body_start_match:
        body_content = content[body_start_match.start():]
    else:
        # fallback if header numbering is different
        body_content = content[content.find('---', content.find('## Abstract') + 10) + 3:]

    lines = body_content.split('\n')
    tex_body = []
    in_list = None
    in_table = False
    table_buffer = []
    in_refs = False

    for i, line in enumerate(lines):
        trimmed = line.strip()
        if not trimmed:
            if in_list: tex_body.append(f"\\end{{{in_list}}}"); in_list = None
            if in_table: tex_body.append(convert_table(table_buffer)); table_buffer = []; in_table = False
            tex_body.append("\n")
            continue
        
        # Table
        if trimmed.startswith('|'):
            in_table = True
            table_buffer.append(trimmed)
            continue
        elif in_table:
            tex_body.append(convert_table(table_buffer))
            table_buffer = []
            in_table = False

        # Separators
        if trimmed == "---": continue

        # Headers
        if trimmed.startswith('## '):
            if in_list: tex_body.append(f"\\end{{{in_list}}}"); in_list = None
            h_text = trimmed[3:].strip()
            if h_text.lower() == "references":
                in_refs = True
                tex_body.append(r"\begin{thebibliography}{99}")
            else:
                tex_body.append(f"\\section{{{tex_escape(h_text)}}}")
            continue
        elif trimmed.startswith('### '):
            if in_list: tex_body.append(f"\\end{{{in_list}}}"); in_list = None
            tex_body.append(f"\\subsection{{{tex_escape(trimmed[4:].strip())}}}")
            continue

        # Image
        if trimmed.startswith('!['):
            if in_list: tex_body.append(f"\\end{{{in_list}}}"); in_list = None
            m = re.match(r'!\[(.*?)\]\((.*?)\)', trimmed)
            if m:
                cap_raw, path = m.groups()
                if 'fig7_manifold.pdf' in path: path = path.replace('fig7_manifold.pdf', 'fig7_reduction.pdf')
                desc = ""
                found_desc = False
                for j in range(i+1, min(i+4, len(lines))):
                    nl = lines[j].strip()
                    if nl.startswith('**Fig'):
                        desc = clean_caption(nl)
                        lines[j] = "" 
                        found_desc = True
                        break
                    if nl.startswith('##') or nl.startswith('!['): break
                if not found_desc: desc = clean_caption(cap_raw)
                tex_body.append(r"\begin{figure}[htbp]\centering")
                tex_body.append(f"\\includegraphics[width=0.8\\textwidth,height=0.35\\textheight,keepaspectratio]{{{path}}}")
                tex_body.append(f"\\caption{{{tex_escape(desc)}}}")
                tex_body.append(r"\end{figure}")
            continue

        # Lists
        if trimmed.startswith('- ') or trimmed.startswith('* '):
            if not in_refs:
                if in_list != 'itemize':
                    if in_list: tex_body.append(f"\\end{{{in_list}}}")
                    tex_body.append(r"\begin{itemize}")
                    in_list = 'itemize'
            
            content_text = trimmed[2:].strip()
            if in_refs:
                key = "".join(filter(str.isalnum, content_text[:15])) + str(i)
                tex_body.append(f"\\bibitem{{{key}}} {inline_format(tex_escape(content_text))}")
            else:
                tex_body.append(f"\\item {inline_format(tex_escape(content_text))}")
            continue
        elif re.match(r'^\d+\.\s+', trimmed):
            if in_list != 'enumerate':
                if in_list: tex_body.append(f"\\end{{{in_list}}}")
                tex_body.append(r"\begin{enumerate}")
                in_list = 'enumerate'
            content_text = re.sub(r'^\d+\.\s+', '', trimmed)
            tex_body.append(f"\\item {inline_format(tex_escape(content_text))}")
            continue

        # Normal Paragraph
        tex_body.append(inline_format(tex_escape(trimmed)))

    if in_list: tex_body.append(f"\\end{{{in_list}}}")
    if in_refs: tex_body.append(r"\end{thebibliography}")

    full_tex = r'''\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{hyperref}
\usepackage{geometry}
\usepackage{url}
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
''' + tex_escape(abstract) + r'''
\end{abstract}

\textbf{Keywords:} ''' + tex_escape(keywords) + r'''

''' + '\n'.join(tex_body) + r'''

\end{document}
'''
    with open("morphic_inner_world_journal.tex", "w", encoding='utf-8') as f:
        f.write(full_tex)

    print("Running xelatex...")
    subprocess.run(["xelatex", "-interaction=nonstopmode", "morphic_inner_world_journal.tex"], capture_output=True)
    subprocess.run(["xelatex", "-interaction=nonstopmode", "morphic_inner_world_journal.tex"], capture_output=True)
    print("Successfully generated morphic_inner_world_journal.pdf")

if __name__ == "__main__":
    main()
