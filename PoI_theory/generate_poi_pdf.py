import os
import re
import subprocess
import glob

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
    # Protect blocks that should NOT be escaped:
    # 1. Math mode: $...$, $$...$$, \[...\], \(...\), \begin{...}...\end{...}
    # 2. Code blocks: ```...```
    # We use a non-greedy match and re.DOTALL
    pattern = r'(\$\$.*?\$\$|\$.*?\$|\\\[.*?\\\]|\\\(.*?\\\)|\\begin\{.*?\}.*?\\end\{.*?\}|```.*?```)'
    parts = re.split(pattern, text, flags=re.DOTALL)
    res = ""
    for part in parts:
        if not part: continue
        # Check if this part is a protected block
        if (part.startswith('$') or part.startswith('\\[' ) or 
            part.startswith('\\(') or part.startswith('\\begin') or 
            part.startswith('```')):
            res += part
        else:
            temp = part
            for char, escape in conv.items():
                temp = temp.replace(char, escape)
            res += temp
    return res

def inline_format(text):
    # Markdown link conversion
    text = re.sub(r'\[(.*?)\]\((.*?)\)', lambda m: f"\\href{{{m.group(2)}}}{{{m.group(1)}}}", text)
    # Bold/Italic
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
    return text

def clean_caption(caption):
    # Remove "Fig. 1:", "図 1:", etc.
    caption = re.sub(r'^(?:\*\*|)\s*(?:Fig\.|Figure|Fig|図)\s*\d+[:.：]?\s*(?:\*\*|)', '', caption, flags=re.IGNORECASE)
    caption = caption.replace('**', '')
    return caption.strip().rstrip('.')

def convert_table(lines):
    if len(lines) < 3: return ""
    filtered_lines = [l for l in lines if not re.match(r'^\|[- :|]+\|$', l)]
    if not filtered_lines: return ""
    
    headers = [inline_format(h.strip()) for h in filtered_lines[0].strip('|').split('|')]
    num_cols = len(headers)
    tex = [r"\begin{table}[htbp]\centering"]
    tex.append(r"\begin{tabular}{" + "l" * num_cols + "}")
    tex.append(r"\hline")
    tex.append(" & ".join(headers) + r" \\ \hline")
    for line in filtered_lines[1:]:
        cols = [inline_format(c.strip()) for c in line.strip('|').split('|')]
        if len(cols) < num_cols: cols += [""] * (num_cols - len(cols))
        else: cols = cols[:num_cols]
        tex.append(" & ".join(cols) + r" \\")
    tex.append(r"\hline")
    tex.append(r"\end{tabular}")
    tex.append(r"\end{table}")
    return "\n".join(tex)

def process_lines(lines, is_jp, m_base, mermaid_idx=1, in_abstract=False):
    tex_out = []
    in_list = None
    in_table = False
    table_buffer = []
    in_refs = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        trimmed = line.strip()
        
        # Mermaid handling
        if trimmed.startswith('```mermaid'):
            # Skip until ```
            while i < len(lines) and not lines[i].strip() == '```' and not (i > 0 and lines[i].strip().startswith('```') and not lines[i].strip().startswith('```mermaid')):
                i += 1
            if i < len(lines): i += 1 # Skip the closing ```
            
            pattern = f"images/mermaid_{m_base}_{mermaid_idx}_*.pdf"
            matches = glob.glob(pattern)
            if matches:
                pdf_path = matches[0]
                if len(matches) > 1:
                    matches.sort(key=lambda x: os.path.getsize(x), reverse=is_jp)
                    pdf_path = matches[0]
                
                if in_abstract:
                    tex_out.append(r"\begin{center}")
                    tex_out.append(f"\\includegraphics[width=0.8\\textwidth,height=0.4\\textheight,keepaspectratio]{{{pdf_path}}}")
                else:
                    tex_out.append(r"\begin{figure}[htbp]\centering")
                    tex_out.append(f"\\includegraphics[width=0.8\\textwidth,height=0.4\\textheight,keepaspectratio]{{{pdf_path}}}")
                
                desc = f"Diagram {mermaid_idx}"
                # Look ahead for caption
                for j in range(i, min(i + 5, len(lines))):
                    nl = lines[j].strip()
                    if nl.startswith('\\textbf{Fig') or nl.startswith('\\textbf{図'):
                        desc = clean_caption(nl)
                        lines[j] = "" # Consume it
                        break
                    if nl.startswith('\\section') or nl.startswith('!['): break
                
                if in_abstract:
                    tex_out.append(f"\\captionof{{figure}}{{{inline_format(desc)}}}")
                    tex_out.append(r"\end{center}")
                else:
                    tex_out.append(f"\\caption{{{inline_format(desc)}}}")
                    tex_out.append(r"\end{figure}")
            mermaid_idx += 1
            continue

        if not trimmed:
            if in_list: tex_out.append(f"\\end{{{in_list}}}"); in_list = None
            if in_table: tex_out.append(convert_table(table_buffer)); table_buffer = []; in_table = False
            tex_out.append("\n")
            i += 1
            continue
        
        if trimmed.startswith('|'):
            in_table = True
            table_buffer.append(trimmed)
            i += 1
            continue
        elif in_table:
            tex_out.append(convert_table(table_buffer))
            table_buffer = []
            in_table = False

        if trimmed == "---":
            i += 1
            continue

        # Headers - they are already escaped, so we look for \#
        if trimmed.startswith('\\# '):
            if in_list: tex_out.append(f"\\end{{{in_list}}}"); in_list = None
            h_text = trimmed[3:].strip()
            # Remove leading numbers like "1 ", "2.1 " etc.
            h_text = re.sub(r'^\d+(\.\d+)*\.?\s+', '', h_text)
            if h_text.lower() in ["references", "参考文献", "bibliography"]:
                in_refs = True
                tex_out.append(r"\begin{thebibliography}{99}")
            else:
                tex_out.append(f"\\section{{{inline_format(h_text)}}}")
            i += 1
            continue
        elif trimmed.startswith('\\#\\# '):
            if in_list: tex_out.append(f"\\end{{{in_list}}}"); in_list = None
            h_text = trimmed[5:].strip()
            h_text = re.sub(r'^\d+(\.\d+)*\.?\s+', '', h_text)
            tex_out.append(f"\\subsection{{{inline_format(h_text)}}}")
            i += 1
            continue
        elif trimmed.startswith('\\#\\#\\# '):
            if in_list: tex_out.append(f"\\end{{{in_list}}}"); in_list = None
            h_text = trimmed[7:].strip()
            h_text = re.sub(r'^\d+(\.\d+)*\.?\s+', '', h_text)
            tex_out.append(f"\\subsubsection{{{inline_format(h_text)}}}")
            i += 1
            continue

        # Image
        if trimmed.startswith('!['):
            if in_list: tex_out.append(f"\\end{{{in_list}}}"); in_list = None
            m = re.match(r'!\[(.*?)\]\((.*?)\)', trimmed)
            if m:
                cap_raw, path = m.groups()
                desc = ""
                found_desc = False
                for j in range(i+1, min(i+5, len(lines))):
                    nl = lines[j].strip()
                    if nl.startswith('\\textbf{Fig') or nl.startswith('\\textbf{図'):
                        desc = clean_caption(nl)
                        lines[j] = "" 
                        found_desc = True
                        break
                    if nl.startswith('\\section') or nl.startswith('!['): break
                if not found_desc: desc = clean_caption(cap_raw)
                
                if in_abstract:
                    tex_out.append(r"\begin{center}")
                    tex_out.append(f"\\includegraphics[width=0.8\\textwidth,height=0.35\\textheight,keepaspectratio]{{{path}}}")
                    tex_out.append(f"\\captionof{{figure}}{{{inline_format(desc)}}}")
                    tex_out.append(r"\end{center}")
                else:
                    tex_out.append(r"\begin{figure}[htbp]\centering")
                    tex_out.append(f"\\includegraphics[width=0.8\\textwidth,height=0.35\\textheight,keepaspectratio]{{{path}}}")
                    tex_out.append(f"\\caption{{{inline_format(desc)}}}")
                    tex_out.append(r"\end{figure}")
            i += 1
            continue

        # Lists - after tex_escape, - becomes - (no change) or \-? No, - is not in conv.
        # But * becomes \*
        if trimmed.startswith('- ') or trimmed.startswith('\\* '):
            if not in_refs:
                if in_list != 'itemize':
                    if in_list: tex_out.append(f"\\end{{{in_list}}}")
                    tex_out.append(r"\begin{itemize}")
                    in_list = 'itemize'
            
            content_text = trimmed[2:].strip() if trimmed.startswith('- ') else trimmed[3:].strip()
            if in_refs:
                key = "".join(filter(str.isalnum, content_text[:15])) + str(i)
                tex_out.append(f"\\bibitem{{{key}}} {inline_format(content_text)}")
            else:
                tex_out.append(f"\\item {inline_format(content_text)}")
            i += 1
            continue
        elif re.match(r'^\d+\.\s+', trimmed):
            if in_list != 'enumerate':
                if in_list: tex_out.append(f"\\end{{{in_list}}}")
                tex_out.append(r"\begin{enumerate}")
                in_list = 'enumerate'
            content_text = re.sub(r'^\d+\.\s+', '', trimmed)
            tex_out.append(f"\\item {inline_format(content_text)}")
            i += 1
            continue

        # Normal Paragraph
        tex_out.append(inline_format(trimmed))
        i += 1

    if in_list: tex_out.append(f"\\end{{{in_list}}}")
    if in_refs: tex_out.append(r"\end{thebibliography}")
    return tex_out, mermaid_idx

def process_markdown(md_path, output_pdf_name, is_jp=False):
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found.")
        return

    # Use utf-8-sig to handle BOM
    with open(md_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # Metadata extraction (BEFORE tex_escape to keep regex simple)
    title_m = re.search(r'^#\s+(.*?)(?=\n\n|\n\*\*)', content, re.S | re.M)
    title_raw = title_m.group(1).strip() if title_m else os.path.basename(md_path)
    
    author_m = re.search(r'\*\*(?:Author|著者)[:：]\s*(?:\*\*|)\s*(.*?)(?:\*\*|(?=\n))', content)
    author = author_m.group(1).strip() if author_m else ""
    
    date_m = re.search(r'\*\*(?:Date|日付)[:：]\s*(?:\*\*|)\s*(.*?)(?:\*\*|(?=\n))', content)
    date = date_m.group(1).strip() if date_m else ""
    
    keywords_m = re.search(r'\*\*(?:Keywords|キーワード)[:：]\s*(?:\*\*|)\s*(.*?)(?:\*\*|(?=\n))', content)
    keywords = keywords_m.group(1).strip() if keywords_m else ""
    
    # Abstract extraction
    abstract_m = re.search(r'(?:##|#)\s+(?:\*\*|)\s*(?:0\.\s*|)(?:Abstract|概要|要旨.*?)\s*(?:\*\*|)\s+(.*?)\s+(?:---|\n# |\n## )', content, re.S | re.I)
    abstract_raw = abstract_m.group(1).strip() if abstract_m else ""

    # Body extraction
    headers = list(re.finditer(r'^#+ .*', content, re.M))
    body_start = 0
    for h_match in headers:
        h_text = h_match.group(0).lower()
        if h_match.start() < 10: continue # Title
        if any(x in h_text for x in ["abstract", "概要", "要旨"]): continue
        if h_text.startswith('# **0.'): continue
        body_start = h_match.start()
        break
    
    if body_start:
        body_raw = content[body_start:]
    else:
        idx = content.find('---')
        if idx != -1:
            idx2 = content.find('---', idx + 3)
            if idx2 != -1: body_raw = content[idx2 + 3:]
            else: body_raw = content[idx + 3:]
        else:
            body_raw = content

    # NOW tex_escape everything
    title_tex = tex_escape(title_raw).replace('\n', ' ')
    if is_jp and "：" in title_tex:
        title_tex = title_tex.replace("：", "：\\\\\\\\ ")
    
    author_tex = tex_escape(author)
    date_tex = tex_escape(date)
    keywords_tex = tex_escape(keywords)
    
    abstract_escaped = tex_escape(abstract_raw)
    body_escaped = tex_escape(body_raw)

    # Derive mermaid base name
    m_base = os.path.basename(md_path)
    if m_base.endswith("_jp.md"): m_base = m_base[:-6]
    elif m_base.endswith("_en.md"): m_base = m_base[:-6]
    else: m_base = m_base[:-3]

    # Process abstract
    abstract_tex_lines, next_mermaid_idx = process_lines(abstract_escaped.split('\n'), is_jp, m_base, mermaid_idx=1, in_abstract=True)
    abstract_tex = "\n".join(abstract_tex_lines)

    # Process body
    body_tex_lines, _ = process_lines(body_escaped.split('\n'), is_jp, m_base, mermaid_idx=next_mermaid_idx)
    tex_body = "\n".join(body_tex_lines)

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
\author{''' + author_tex + r'''}
\date{''' + date_tex + r'''}

\begin{document}
''' + localized_labels + r'''
\maketitle

\begin{abstract}
''' + abstract_tex + r'''
\end{abstract}

\textbf{''' + ("Keywords:" if not is_jp else "キーワード:") + r'''} ''' + keywords_tex + r'''

''' + tex_body + r'''

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
    files = glob.glob("*.md")
    for f in files:
        is_jp = f.endswith("_jp.md")
        base = f[:-6] if is_jp else f[:-3]
        out_name = base + (".pdf" if not is_jp else "_jp.pdf")
        process_markdown(f, out_name, is_jp=is_jp)

if __name__ == "__main__":
    main()
