import os
import re
import subprocess
import glob

def tex_escape(text):
    if not text: return ""
    conv = {
        '\\': r'\textbackslash{}',
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
    # This function is now ONLY for plain text parts.
    res = ""
    for char in text:
        res += conv.get(char, char)
    return res

def inline_format(text):
    if not text: return ""
    # Bold/Italic
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
    # Links
    text = re.sub(r'\[(.*?)\]\((.*?)\)', lambda m: f"\\href{{{m.group(2)}}}{{{m.group(1)}}}", text)
    return text

def process_inline(text):
    if not text: return ""
    # Protect inline math while escaping the rest
    pattern = r'(\$.*?\$|\\\(.*?\\\)|`.*?`)'
    parts = re.split(pattern, text)
    res = ""
    for part in parts:
        if not part: continue
        if part.startswith('$') or part.startswith('\\('):
            res += part
        elif part.startswith('`'):
            # Code block: convert to \texttt and escape special chars
            code_content = part[1:-1]
            res += f"\\texttt{{{tex_escape(code_content)}}}"
        else:
            res += inline_format(tex_escape(part))
    return res

def clean_caption(caption):
    if not caption: return ""
    caption = re.sub(r'^(?:#+|\*+)\s*', '', caption)
    caption = re.sub(r'^(?:Fig\.|Figure|図)\s*\d+(?:\.\d+)*[:.：]?\s*', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\*+$', '', caption.strip())
    return caption.strip().rstrip('.')

def convert_table(lines):
    if len(lines) < 3: return ""
    filtered_lines = [l for l in lines if not re.match(r'^\|[- :|]+\|$', l)]
    if not filtered_lines: return ""
    
    def split_row(row):
        row = row.strip().strip('|')
        return re.split(r'(?<!\\)\|', row)

    headers = [process_inline(h.strip()) for h in split_row(filtered_lines[0])]
    num_cols = len(headers)
    tex = [r"\begin{table}[htbp]\centering"]
    tex.append(r"\begin{tabular}{" + "l" * num_cols + "}")
    tex.append(r"\hline")
    tex.append(" & ".join(headers) + r" \\ \hline")
    for line in filtered_lines[1:]:
        cols = [process_inline(c.strip()) for c in split_row(line)]
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
        
        # 1. Mermaid handling
        if trimmed.startswith('```mermaid'):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            if i < len(lines): i += 1
            
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
                for j in range(i, min(i + 5, len(lines))):
                    nl = lines[j].strip()
                    if re.search(r'^(?:\*+)(?:Fig\.|Figure|図)\s*\d+', nl, re.IGNORECASE):
                        desc = clean_caption(nl)
                        lines[j] = "" 
                        break
                    if nl.startswith('#') or nl.startswith('!['): break
                
                if in_abstract:
                    tex_out.append(f"\\captionof{{figure}}{{{process_inline(desc)}}}")
                    tex_out.append(r"\end{center}")
                else:
                    tex_out.append(f"\\caption{{{process_inline(desc)}}}")
                    tex_out.append(r"\end{figure}")
            mermaid_idx += 1
            continue

        # 2. Code blocks (other than mermaid)
        if trimmed.startswith('```'):
            block = [line]
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                block.append(lines[i])
                i += 1
            if i < len(lines): block.append(lines[i]); i += 1
            # For code blocks, just use verbatim or similar.
            tex_out.append(r"\begin{verbatim}")
            tex_out.extend([l.replace('```', '') for l in block if l.strip() != '```'])
            tex_out.append(r"\end{verbatim}")
            continue

        # 3. Math Blocks and Environments
        if trimmed.startswith('$$') or trimmed.startswith('\\['):
            end_mark = '$$' if trimmed.startswith('$$') else '\\]'
            block = [line]
            # If start and end are on same line
            if len(trimmed) > 2 and trimmed.endswith(end_mark):
                tex_out.append(line)
                i += 1
                continue
            i += 1
            while i < len(lines) and not lines[i].strip().endswith(end_mark):
                block.append(lines[i])
                i += 1
            if i < len(lines): block.append(lines[i]); i += 1
            tex_out.extend(block)
            continue

        if trimmed.startswith('\\begin{'):
            block = [line]
            m = re.match(r'\\begin\{(.*?)\}', trimmed)
            if m:
                env_name = m.group(1)
                end_mark = f'\\end{{{env_name}}}'
                i += 1
                while i < len(lines) and not lines[i].strip().startswith(end_mark):
                    block.append(lines[i])
                    i += 1
                if i < len(lines): block.append(lines[i]); i += 1
                tex_out.extend(block)
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

        # Headers
        if trimmed.startswith('#'):
            if in_list: tex_out.append(f"\\end{{{in_list}}}"); in_list = None
            m = re.match(r'^(#+)\s*(.*)', trimmed)
            if m:
                level = len(m.group(1))
                h_text = m.group(2).strip()
                h_text = re.sub(r'^\d+(\.\d+)*\.?\s+', '', h_text)
                
                if h_text.lower() in ["references", "参考文献", "bibliography"]:
                    in_refs = True
                    tex_out.append(r"\begin{thebibliography}{99}")
                else:
                    cmd = "section"
                    if level == 2: cmd = "subsection"
                    elif level == 3: cmd = "subsubsection"
                    elif level >= 4: cmd = "paragraph"
                    tex_out.append(f"\\{cmd}{{{process_inline(h_text)}}}")
            i += 1
            continue

        # Image
        if trimmed.startswith('!['):
            if in_list: tex_out.append(f"\\end{{{in_list}}}"); in_list = None
            m = re.match(r'!\[(.*?)\]\((.*?)\)', trimmed)
            if m:
                cap_raw, path = m.groups()
                path = path.replace(r'\_', '_')
                desc = ""
                found_desc = False
                for j in range(i+1, min(i+5, len(lines))):
                    nl = lines[j].strip()
                    if re.search(r'^(?:\*+)(?:Fig\.|Figure|図)\s*\d+', nl, re.IGNORECASE):
                        desc = clean_caption(nl)
                        lines[j] = "" 
                        found_desc = True
                        break
                    if nl.startswith('#') or nl.startswith('!['): break
                if not found_desc: desc = clean_caption(cap_raw)
                
                if in_abstract:
                    tex_out.append(r"\begin{center}")
                    tex_out.append(f"\\includegraphics[width=0.8\\textwidth,height=0.35\\textheight,keepaspectratio]{{{path}}}")
                    tex_out.append(f"\\captionof{{figure}}{{{process_inline(desc)}}}")
                    tex_out.append(r"\end{center}")
                else:
                    tex_out.append(r"\begin{figure}[htbp]\centering")
                    tex_out.append(f"\\includegraphics[width=0.8\\textwidth,height=0.35\\textheight,keepaspectratio]{{{path}}}")
                    tex_out.append(f"\\caption{{{process_inline(desc)}}}")
                    tex_out.append(r"\end{figure}")
            i += 1
            continue

        # Lists
        if trimmed.startswith('- ') or trimmed.startswith('* '):
            if not in_refs:
                if in_list != 'itemize':
                    if in_list: tex_out.append(f"\\end{{{in_list}}}")
                    tex_out.append(r"\begin{itemize}")
                    in_list = 'itemize'
            
            content_text = re.sub(r'^[-*]\s*', '', trimmed)
            if in_refs:
                key = "".join(filter(str.isalnum, content_text[:15])) + str(i)
                tex_out.append(f"\\bibitem{{{key}}} {process_inline(content_text)}")
            else:
                # Handle inline math in lists
                tex_out.append(f"\\item {process_inline(content_text)}")
            i += 1
            continue
        elif re.match(r'^\d+\.\s+', trimmed):
            content_text = re.sub(r'^\d+\.\s+', '', trimmed)
            if in_refs:
                key = "".join(filter(str.isalnum, content_text[:15])) + str(i)
                tex_out.append(f"\\bibitem{{{key}}} {process_inline(content_text)}")
            else:
                if in_list != 'enumerate':
                    if in_list: tex_out.append(f"\\end{{{in_list}}}")
                    tex_out.append(r"\begin{enumerate}")
                    in_list = 'enumerate'
                tex_out.append(f"\\item {process_inline(content_text)}")
            i += 1
            continue

        # Normal Paragraph
        if in_refs:
            key = "".join(filter(str.isalnum, trimmed[:15])) + str(i)
            tex_out.append(f"\\bibitem{{{key}}} {process_inline(trimmed)}")
        else:
            tex_out.append(process_inline(trimmed))
        i += 1

    if in_list: tex_out.append(f"\\end{{{in_list}}}")
    if in_refs: tex_out.append(r"\end{thebibliography}")
    return tex_out, mermaid_idx

def process_markdown(md_path, output_pdf_name, is_jp=False):
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found.")
        return

    with open(md_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # Metadata extraction
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
    headers = list(re.finditer(r'^# .*', content, re.M))
    body_start = 0
    for h_match in headers:
        if h_match.start() < 10: continue # Title
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

    title_tex = tex_escape(title_raw).replace('\n', ' ')
    if is_jp and "：" in title_tex:
        title_tex = title_tex.replace("：", "：\\\\ ")
    
    m_base = os.path.basename(md_path)
    if m_base.endswith("_jp.md"): m_base = m_base[:-6]
    elif m_base.endswith("_en.md"): m_base = m_base[:-6]
    else: m_base = m_base[:-3]

    abstract_tex_lines, next_mermaid_idx = process_lines(abstract_raw.split('\n'), is_jp, m_base, mermaid_idx=1, in_abstract=True)
    abstract_tex = "\n".join(abstract_tex_lines)

    body_tex_lines, _ = process_lines(body_raw.split('\n'), is_jp, m_base, mermaid_idx=next_mermaid_idx)
    tex_body = "\n".join(body_tex_lines)

    jp_preamble = r'''\usepackage{xeCJK}
\setCJKmainfont{Hiragino Sans}''' if is_jp else ""
# \setCJKmainfont{Noto Sans CJK JP}''' if is_jp else ""
    
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
\usepackage{amsmath,amssymb,amscd}
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
''' + abstract_tex + r'''
\end{abstract}

\textbf{''' + ("Keywords:" if not is_jp else "キーワード:") + r'''} ''' + process_inline(keywords) + r'''

''' + tex_body + r'''

\end{document}
'''
    tex_path = output_pdf_name.replace(".pdf", ".tex")
    with open(tex_path, "w", encoding='utf-8') as f:
        f.write(full_tex)

    print(f"Running xelatex for {output_pdf_name}...")
    try:
        subprocess.run(["xelatex", "-interaction=nonstopmode", tex_path], capture_output=True, check=True)
        subprocess.run(["xelatex", "-interaction=nonstopmode", tex_path], capture_output=True, check=True)
        print(f"Successfully generated {output_pdf_name}")
    except subprocess.CalledProcessError:
        print(f"Error: xelatex failed for {output_pdf_name}. Check log.")

def main():
    files = glob.glob("*.md")
    for f in files:
        is_jp = f.endswith("_jp.md")
        base = f[:-6] if is_jp else f[:-3]
        out_name = base + (".pdf" if not is_jp else "_jp.pdf")
        process_markdown(f, out_name, is_jp=is_jp)

if __name__ == "__main__":
    main()
