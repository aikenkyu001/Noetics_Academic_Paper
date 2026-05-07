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
    # 1. Remove "Fig. 1:", "図 1:", etc., including surrounding stars
    caption = re.sub(r'^(?:\*\*|)\s*(?:Fig\.|Figure|Fig|図)\s*\d+[:.：]?\s*(?:\*\*|)', '', caption, flags=re.IGNORECASE)
    # 2. Aggressively remove any literal ** markers from the caption
    caption = caption.replace('**', '')
    return caption.strip().rstrip('.')

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

def process_markdown(md_path, output_pdf_name, is_jp=False):
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found.")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Metadata (English/Japanese support)
    title_m = re.search(r'^# (.*)', content, re.M)
    title_raw = title_m.group(1).strip() if title_m else "Untitled"
    title_tex = tex_escape(title_raw)
    if is_jp and "：" in title_tex:
        # Break after colon for Japanese title to improve balance
        title_tex = title_tex.replace("：", "：\\\\\\\\ ")
    
    author_m = re.search(r'\*\*(?:Author|著者):\*\* (.*)', content)
    author = author_m.group(1).strip() if author_m else ""
    
    date_m = re.search(r'\*\*(?:Date|日付):\*\* (.*)', content)
    date = date_m.group(1).strip() if date_m else ""
    
    keywords_m = re.search(r'\*\*(?:Keywords|キーワード):\*\* (.*)', content)
    keywords = keywords_m.group(1).strip() if keywords_m else ""
    
    # Abstract / 概要
    abstract_m = re.search(r'### (?:Abstract|概要.*?)\s+(.*?)\s+(?:---|\n# )', content, re.S)
    abstract = inline_format(tex_escape(abstract_m.group(1).strip())) if abstract_m else ""

    # Body - start from Introduction / はじめに
    body_start_match = re.search(r'# 1 (?:Introduction|はじめに)', content)
    if body_start_match:
        body_content = content[body_start_match.start():]
    else:
        # fallback
        search_term = '### Abstract' if not is_jp else '### 概要'
        idx = content.find('---', content.find(search_term) + 10)
        if idx != -1:
            body_content = content[idx + 3:]
        else:
            body_content = content

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
        if trimmed.startswith('# '):
            if in_list: tex_body.append(f"\\end{{{in_list}}}"); in_list = None
            h_text = trimmed[2:].strip()
            # Remove leading numbers like "1 ", "2.1 " etc.
            h_text = re.sub(r'^\d+(\.\d+)*\.?\s+', '', h_text)
            
            if h_text.lower() in ["references", "参考文献"]:
                in_refs = True
                tex_body.append(r"\begin{thebibliography}{99}")
            else:
                tex_body.append(f"\\section{{{inline_format(tex_escape(h_text))}}}")
            continue
        elif trimmed.startswith('## '):
            if in_list: tex_body.append(f"\\end{{{in_list}}}"); in_list = None
            h_text = trimmed[3:].strip()
            # Remove leading numbers like "1.1 ", "2.1.1 " etc.
            h_text = re.sub(r'^\d+(\.\d+)*\.?\s+', '', h_text)
            tex_body.append(f"\\subsection{{{inline_format(tex_escape(h_text))}}}")
            continue
        elif trimmed.startswith('### '):
            if in_list: tex_body.append(f"\\end{{{in_list}}}"); in_list = None
            h_text = trimmed[4:].strip()
            # Remove leading numbers like "1.1.1 " etc.
            h_text = re.sub(r'^\d+(\.\d+)*\.?\s+', '', h_text)
            tex_body.append(f"\\subsubsection{{{inline_format(tex_escape(h_text))}}}")
            continue

        # Image
        if trimmed.startswith('!['):
            if in_list: tex_body.append(f"\\end{{{in_list}}}"); in_list = None
            m = re.match(r'!\[(.*?)\]\((.*?)\)', trimmed)
            if m:
                cap_raw, path = m.groups()
                desc = ""
                found_desc = False
                for j in range(i+1, min(i+4, len(lines))):
                    nl = lines[j].strip()
                    if nl.startswith('**Fig') or nl.startswith('**図'):
                        desc = clean_caption(nl)
                        lines[j] = "" 
                        found_desc = True
                        break
                    if nl.startswith('#') or nl.startswith('!['): break
                if not found_desc: desc = clean_caption(cap_raw)
                tex_body.append(r"\begin{figure}[htbp]\centering")
                tex_body.append(f"\\includegraphics[width=0.8\\textwidth,height=0.35\\textheight,keepaspectratio]{{{path}}}")
                tex_body.append(f"\\caption{{{inline_format(tex_escape(desc))}}}")
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

    # LaTeX Template
    jp_preamble = r'''\usepackage{xeCJK}
\setCJKmainfont{Hiragino Mincho ProN}''' if is_jp else ""
    
    localized_labels = r'''
\renewcommand{\abstractname}{概要}
\renewcommand{\figurename}{図}
\renewcommand{\tablename}{表}
\renewcommand{\refname}{参考文献}
''' if is_jp else ""

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
\usepackage{caption}
\captionsetup{labelfont=bf,textfont=bf}
''' + jp_preamble + r'''

\geometry{margin=1in}
\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=cyan}

\title{''' + title_tex + r'''}
\author{''' + tex_escape(author) + r'''}
\date{''' + tex_escape(date) + r'''}

\begin{document}
''' + localized_labels + r'''
\maketitle

\begin{abstract}
''' + abstract + r'''
\end{abstract}

\textbf{''' + ("Keywords:" if not is_jp else "キーワード:") + r'''} ''' + inline_format(tex_escape(keywords)) + r'''

''' + '\n'.join(tex_body) + r'''

\end{document}
'''
    tex_path = output_pdf_name.replace(".pdf", ".tex")
    with open(tex_path, "w", encoding='utf-8') as f:
        f.write(full_tex)

    print(f"Running xelatex for {output_pdf_name}...")
    subprocess.run(["xelatex", "-interaction=nonstopmode", tex_path], capture_output=True)
    subprocess.run(["xelatex", "-interaction=nonstopmode", tex_path], capture_output=True)
    print(f"Successfully generated {output_pdf_name}")

def main():
    # 1. English conversion
    process_markdown("morphic_autonomy_lab_en.md", "morphic_autonomy_lab.pdf", is_jp=False)
    
    # 2. Japanese conversion
    process_markdown("morphic_autonomy_lab_jp.md", "morphic_autonomy_lab_jp.pdf", is_jp=True)

if __name__ == "__main__":
    main()
