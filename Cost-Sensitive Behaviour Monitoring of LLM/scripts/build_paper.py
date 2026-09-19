from pathlib import Path
import re

root = Path('/mnt/data/revision_work/final_revision')
tex_dir = root / 'paper'
src = (tex_dir / 'pandoc_body.tex').read_text()

m = re.search(r'\\subsection\{Abstract\}\\label\{abstract\}\n(.*?)(?=\\subsection\{1\. Introduction\})', src, re.S)
if not m:
    raise SystemExit('abstract not found')
abstract = m.group(1).strip()

start = src.find('\\subsection{1. Introduction}')
refs_pos = src.find('\\subsection{References}', start)
if start < 0 or refs_pos < 0:
    raise SystemExit('paper body sections not found')
body = src[start:refs_pos]

# Convert Markdown-generated heading levels into IJCAI section levels.
body = re.sub(r'\\subsection\{(\d+)\.\s+', r'\\section{', body)
body = re.sub(r'\\subsubsection\{(\d+(?:\.\d+)*)\s+([^}]*)\}', r'\\subsection{\2}', body)
body = body.replace('\\subsubsection{', '\\subsection{')
body = re.sub(r'\\label\{[^}]+\}', '', body)
body = body.replace('\\tightlist\n', '')

# Reference keys used by the final bibliography.
keys = {
    1: 'chen2023', 2: 'lauri2022', 3: 'rahbar2025', 4: 'li2025',
    5: 'truong2020', 6: 'shannon1948', 7: 'fu2025', 8: 'leeeval2025'
}
for n, key in keys.items():
    body = body.replace('{[}' + str(n) + '{]}', r'~\shortcite{' + key + r'}')
    body = body.replace('[' + str(n) + ']', r'~\shortcite{' + key + r'}')

captions = {
    1: 'Hypothetical prior over the four hidden states.',
    2: 'Posterior for the worked joint-evidence example.',
    3: 'Expected information gain of candidate probes at the prior.',
    4: 'State-aware action costs used by the main policy.',
    5: 'Development-split selection of the investigation cost.',
    6: 'Twenty-seed held-out comparison. Entries are means plus or minus 95 percent t confidence intervals.',
    7: 'Brier error across 20 held-out seeds.',
    8: 'Investigation-cost sensitivity on the 50-case seed-7 benchmark.',
    9: 'Representative failure cases from the revised benchmark.'
}

# Convert longtable blocks to standard IJCAI-compatible floats.
pat = re.compile(r'\\begin\{longtable\}\[\]\{(.*?)\}\n(.*?)\\end\{longtable\}', re.S)
counter = 0

def convert_table(mt):
    global counter
    counter += 1
    spec = mt.group(1).replace('@{}', '')
    content = mt.group(2)
    content = content.replace('\\toprule\\noalign{}', '\\toprule')
    content = content.replace('\\midrule\\noalign{}', '\\midrule')
    content = content.replace('\\bottomrule\\noalign{}', '\\bottomrule')
    content = content.replace('\\endhead\n', '').replace('\\endlastfoot\n', '')
    content = content.replace('\\noalign{}\n', '')

    # Keep very wide experimental tables across both columns.
    wide = counter in {6, 8, 9} or sum(ch in 'lcr' for ch in spec) >= 7
    env = 'table*' if wide else 'table'
    width = r'\textwidth' if wide else r'\columnwidth'

    return f'''\\begin{{{env}}}[t]
\\centering
\\scriptsize
\\resizebox{{{width}}}{{!}}{{%
\\begin{{tabular}}{{{spec}}}
{content}\\end{{tabular}}%
}}
\\caption{{{captions[counter]}}}
\\end{{{env}}}
'''

body = pat.sub(convert_table, body)
if counter != len(captions):
    raise SystemExit(f'expected {len(captions)} tables, converted {counter}')

# Pull the AI-use statement out as an unnumbered transparency section.
m_ai = re.search(r'\\subsection\{AI-use statement\}.*$', body, re.S)
if not m_ai:
    raise SystemExit('AI-use section not found')
ai = m_ai.group(0).strip().replace('\\subsection{AI-use statement}', '\\section*{AI Use Statement}')
body = body[:m_ai.start()].rstrip() + '\n\n' + ai + '\n'

refs = r'''\begin{thebibliography}{00}

\bibitem{chen2023}
Lingjiao Chen, Matei Zaharia, and James Zou. How is ChatGPT's behavior changing over time? \emph{arXiv preprint arXiv:2307.09009}, 2023.

\bibitem{lauri2022}
Mikko Lauri, David Hsu, and Joni Pajarinen. Partially Observable Markov Decision Processes in Robotics: A Survey. \emph{IEEE Transactions on Robotics}, 39(1):21--40, 2023. doi:10.1109/TRO.2022.3200138.

\bibitem{rahbar2025}
Arman Rahbar, Linus Aronsson, and Morteza Haghir Chehreghani. A Survey on Active Feature Acquisition Strategies. \emph{arXiv preprint arXiv:2502.11067}, 2025.

\bibitem{li2025}
Yang Li and Junier Oliva. Towards Cost Sensitive Decision Making. In \emph{Proceedings of The 28th International Conference on Artificial Intelligence and Statistics}, PMLR 258, pp. 3601--3609, 2025.

\bibitem{truong2020}
Charles Truong, Laurent Oudre, and Nicolas Vayatis. Selective review of offline change point detection methods. \emph{Signal Processing}, 167:107299, 2020.

\bibitem{shannon1948}
Claude E. Shannon. A Mathematical Theory of Communication. \emph{Bell System Technical Journal}, 27(3):379--423 and 27(4):623--656, 1948.

\bibitem{fu2025}
Xiyan Fu and Wei Liu. How Reliable is Multilingual LLM-as-a-Judge? In \emph{Findings of the Association for Computational Linguistics: ACL 2025}, pp. 11040--11053, 2025.

\bibitem{leeeval2025}
Yukyung Lee, JoongHoon Kim, Jaehee Kim, Hyowon Cho, Pilsung Kang, and Najoung Kim. CheckEval: A reliable LLM-as-a-Judge framework for evaluating text generation using checklists. In \emph{Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing}, pp. 15771--15798, 2025.

\end{thebibliography}
'''

header = r'''\documentclass{article}
\pdfpagewidth=8.5in
\pdfpageheight=11in
\usepackage{ijcai26}
\usepackage{times}
\usepackage{soul}
\usepackage{url}
\usepackage[hidelinks]{hyperref}
\usepackage[utf8]{inputenc}
\usepackage[small]{caption}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsthm}
\usepackage{booktabs}
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage[switch]{lineno}
\usepackage{array}
\linenumbers
\urlstyle{same}
\pdfinfo{
/TemplateVersion (IJCAI.2026.0)
}
\title{Active Cost-Sensitive Monitoring of Black-Box LLM Behavior}
\author{}
\begin{document}
\maketitle
\begin{abstract}
'''
footer = '\\end{abstract}\n' + body + '\n' + refs + '\\end{document}\n'

out = tex_dir / 'main.tex'
out.write_text(header + abstract + '\n' + footer, encoding='utf-8')
print(f'Wrote {out} with {counter} tables')
