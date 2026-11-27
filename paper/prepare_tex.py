"""Convert the supplied Markdown; preserve body wording and all numeric claims."""
from pathlib import Path
import hashlib
import html
import json
import re
import subprocess

PAPER = Path(__file__).resolve().parent


def latex(text):
    return subprocess.check_output(['pandoc', '-f', 'markdown-tex_math_dollars-auto_identifiers-smart',
                                    '-t', 'latex', '--wrap=none'], input=text, text=True).strip()


def main():
    original = (PAPER/'draft.md').read_text()
    manuscript, notes = original.split('## Notes for typesetting (remove before submission)', 1)
    title = manuscript.splitlines()[0].removeprefix('# ')
    abstract = manuscript.split('## Abstract\n', 1)[1].split('\n## 1 Introduction', 1)[0].strip()
    body = '## 1 Introduction' + manuscript.split('\n## 1 Introduction', 1)[1].split('\n## References', 1)[0]
    citations = {
        '(Del Giudice et al. 2026)': r'\citep{delgiudice2026}',
        '(Kundu et al. 2026)': r'\citep{kundu2026}',
        '(Lee 2026; Chen 2026)': r'\citep{lee2026,chen2026}',
        '(Laurito et al. 2025)': r'\citep{laurito2025}',
        '(Choi et al. 2025)': r'\citep{choi2025}',
        '(Artificial Analysis 2026)': r'\citep{artificialanalysis2026}',
        '(Araujo and Uhlig 2026; Gu 2026)': r'\citep{araujo2026,gu2026}',
        '(Liang and Xu 2026)': r'\citep{liang2026}',
        '(Li and Shi 2026; Zhu et al. 2025)': r'\citep{li2026,zhu2025}',
        '(Lakens 2017)': r'\citep{lakens2017}',
        '(Schelling 1960)': r'\citep{schelling1960}',
        '(Hofstadter 1985)': r'\citep{hofstadter1985}',
    }
    for text, command in citations.items():
        assert body.count(text) == 1, text
        body = body.replace(text, command)
    assert '(Jin et al. 2025)' not in body and 'liu2026' not in body
    tables = re.findall(r'(?m)^\|.*\n(?:\|.*\n)+', body)
    assert len(tables) == 3
    replacements = []
    for index, source in enumerate(tables):
        parsed = [[cell.strip() for cell in line.strip().strip('|').split('|')] for line in source.strip().splitlines()]
        header, data = parsed[0], parsed[2:]
        assert all(len(r) == 3 for r in [header, *data])
        cells = lambda row: ' & '.join(latex(cell) for cell in row) + r' \\'
        if index == 0:
            # Relocate the existing paragraph label to the caption, without
            # creating a new caption sentence or duplicating words.
            assert '**Models.** We use' in body
            body = body.replace('**Models.** We use', 'We use', 1)
            environment, caption = 'table', 'Models.'
            columns = r'@{}p{.25\columnwidth}p{.37\columnwidth}p{.28\columnwidth}@{}'
        elif index == 1:
            # Preserve the third table (the design matrix) as an unnumbered block.
            environment, caption = None, None
            columns = r'@{}p{.38\columnwidth}p{.26\columnwidth}p{.26\columnwidth}@{}'
        else:
            environment, caption = 'table', header[0]
            header[0] = ''
            columns = r'@{}p{.38\columnwidth}p{.26\columnwidth}p{.26\columnwidth}@{}'
        columns = columns.replace('p{', r'>{\raggedright\arraybackslash}p{')
        block = [r'\begin{tabular}{' + columns + '}', r'\toprule', cells(header), r'\midrule',
                 *[cells(row) for row in data], r'\bottomrule', r'\end{tabular}']
        if environment:
            block = [r'\begin{table}[t]', r'\centering', *block,
                     r'\caption{' + latex(caption) + '}', r'\end{table}']
        else:
            block = [r'\begin{center}', *block, r'\end{center}']
        rendered = '\n'.join(block)
        body = body.replace(source, rendered + '\n', 1)
        replacements.append({'source_table': index+1, 'numbered': environment is not None,
                             'caption_relocated_from_existing_text': caption})
    figure = re.search(r'(?m)^.*embedded content: Figure 1\..*$', body)
    assert figure
    caption = html.unescape(figure.group()).split('Figure 1. ', 1)[1].rstrip('\\]')
    figure_tex = '\n'.join([r'\begin{figure*}[t]', r'\centering',
                             r'\includegraphics{figures/figure1.pdf}',
                             r'\caption{' + latex(caption) + '}', r'\label{fig:study1}', r'\end{figure*}'])
    body = body[:figure.start()] + figure_tex + body[figure.end():]
    # Native verbatim, with only the kit-permitted nine-point monospace size.
    code = re.search(r'```text\n(.*?)\n```', body, re.S)
    assert code
    body = body[:code.start()] + '\\begin{agentcard}\n\\begin{verbatim}\n' + code.group(1) + '\n\\end{verbatim}\n\\end{agentcard}' + body[code.end():]
    body = re.sub(r'(?m)^## [1-8] (.*)$', r'# \1', body)
    body_tex = latex(body)
    assert '\\hypertarget' not in body_tex and '\\href' not in body_tex
    preamble = r'''\documentclass[letterpaper]{article}
\usepackage{aaai2027}
\usepackage[hyphens]{url}
\usepackage{graphicx}
\urlstyle{rm}
\def\UrlFont{\rm}
\usepackage{natbib}
\usepackage{caption}
\frenchspacing
\usepackage{booktabs}
\usepackage{array}
\usepackage{listings}
\DeclareCaptionStyle{ruled}{labelfont=normalfont,labelsep=colon,strut=off}
\DeclareCaptionFormat{promptlisting}{\hrule\nobreak\strut #1#2#3\strut\par\nobreak\hrule}
\captionsetup[lstlisting]{style=ruled,format=promptlisting,
  justification=raggedright,singlelinecheck=false}
\lstset{basicstyle={\footnotesize\ttfamily},numbers=none,
  showstringspaces=false,tabsize=2,breaklines=true,breakatwhitespace=false,
  keepspaces=true,columns=fullflexible,frame=b,captionpos=t}
\pdfinfo{/TemplateVersion (2027.2)}
\setcounter{secnumdepth}{1}
% Empty compatibility hook: retain native list spacing; do not compact lists.
\providecommand{\tightlist}{}
\newenvironment{agentcard}{\footnotesize}{}
\DeclareUnicodeCharacter{2212}{\ensuremath{-}}
\DeclareUnicodeCharacter{2248}{\ensuremath{\approx}}
'''
    front = '\\title{' + latex(title) + '}\n\\author{Sambit Mukherjee}\n\\affiliations{Independent Researcher}\n'
    content = '\n'.join([preamble, front, r'\begin{document}', r'\maketitle',
                         r'\begin{abstract}', latex(abstract), r'\end{abstract}',
                         r'\begin{links}', r'\link{Code, prompts, pre-registrations and logs}{https://github.com/sambitmukherjee/kin-loyalty}',
                         r'\end{links}', body_tex, r'\nocite{*}', r'\bibliography{references}',
                         r'\input{appendix/appendices.tex}', r'\end{document}', ''])
    assert 'Notes for typesetting' not in content
    assert r'\$222.47' in content and r'\$1.70 per deal' in content
    assert 'Jin et al. 2025' not in content and 'liu2026' not in content
    (PAPER/'main.tex').write_text(content)
    (PAPER/'conversion-audit.json').write_text(json.dumps({
        'draft_sha256': hashlib.sha256(original.encode()).hexdigest(),
        'main_tex_sha256': hashlib.sha256(content.encode()).hexdigest(),
        'body_prose_reworded_by_converter': False, 'author_approved_edits_applied_to_input': True,
        'numeric_proposals_applied': True,
        'notes_section_omitted': True, 'export_timestamp_replaced_by_requested_author_affiliation': True,
        'references_editorial_warning_and_daggers_omitted': True,
        'repository_placeholder_replaced_per_typesetting_notes': True,
        'table_handling': replacements, 'figure_caption_from_export': caption,
        'pending_literal_citation': None,
        'citation_markup_replacements': citations
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
