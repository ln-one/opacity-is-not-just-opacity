#!/usr/bin/env python3
"""Generate the English reader and ACM preprint from reviewed Markdown."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MD = ROOT / 'markdown'
TEX = HERE / 'latex'
FIGURES = ROOT / 'experiments/formal-evaluation/figures'
FIGURE_META = {
    'method-light': ('fig:method', True, 'Contraction and expansion of fixed source colors on light and dark canvases.'),
    'icon-examples-light': ('fig:icons', False, 'Seven icons at alpha 0.6, 1.0 and 1.4 on light and dark canvases.'),
    'figure1-light': ('fig:sweep', True, 'Three coefficient-sweep panels show contrast gains, decreases and color collisions.'),
    'color-examples-light': ('fig:colors', False, 'All seven Vibrant colors at six coefficients on a white canvas.'),
    'timing-sweep-light': ('fig:runtime', True, 'Runtime over 81 coefficients in Chrome, Firefox and WebKit, with empirical percentile bands.'),
    'background-gallery-1': ('fig:gallery1', True, 'All 300 icons on red, orange, teal and cyan near-source backgrounds; alpha one on the left and two on the right.'),
    'background-gallery-2': ('fig:gallery2', True, 'All 300 icons on blue, magenta, grey and dark grey backgrounds; alpha one on the left and two on the right.'),
}


def run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def pandoc(text, *args):
    return run(['pandoc', '--from=markdown', *args], input=text, capture_output=True).stdout


def reader():
    main = [(MD / f).read_text() for f in [
        '00.abstract.en.md', '01.introduction.en.md', '02.related-work.en.md',
        '03.method.en.md', '04.experiments.en.md', '05.conclusion.en.md',
        '06.acknowledgments.en.md']]
    text = (MD / 'title.md').read_text() + '\n\n' + '\n\n'.join(main)
    text += '\n\n## References\n\n::: {#refs}\n:::\n\n'
    text += (MD / '07.appendix.en.md').read_text()
    for i, stem in enumerate(FIGURE_META, 1):
        pattern = r'!\[(.*?)\]\(figures/' + re.escape(stem) + r'\.png\)\{#[^}]+\}'
        text = re.sub(pattern, lambda m: f'![Figure {i}](figures/{stem}.png)\n\n*Figure {i}. {m.group(1)}*', text)
    (MD / 'manuscript.en.source.md').write_text(text)
    rendered = pandoc(text, '--to=markdown-fenced_divs-bracketed_spans-grid_tables-simple_tables-multiline_tables', '--wrap=none', '--citeproc',
                      '--bibliography='+str(HERE/'references.bib'), '--csl='+str(HERE/'acm.csl'),
                      '--lua-filter='+str(HERE/'markdown-clean.lua'), '-M', 'link-citations=true')
    (MD / 'manuscript.en.md').write_text(rendered)


def tex_fragment(text):
    return pandoc(text, '--to=latex', '--natbib', '--wrap=none', '--top-level-division=section').strip()


def section(path):
    text = path.read_text()
    text = re.sub(r'^## ([1-5])\. ', '# ', text, flags=re.M)
    text = re.sub(r'^### [1-5]\.\d+ ', '## ', text, flags=re.M)
    text = re.sub(r'^## A\. ', '# ', text, flags=re.M)
    text = re.sub(r'^### A\.\d+ ', '## ', text, flags=re.M)

    def figure(m):
        caption, stem = m.group(1), m.group(2)
        label, wide, description = FIGURE_META[stem]
        number = list(FIGURE_META).index(stem) + 1
        env = 'figure*' if wide else 'figure'
        if stem.startswith('background-gallery-'): env='figure'
        placement = '!hb' if stem == 'color-examples-light' else ('!htbp' if stem == 'icon-examples-light' else '!t')
        if stem.startswith('background-gallery-'): placement='H'
        return ('\n\\begin{'+env+'}['+placement+']\n\\centering\n'
                '\\includegraphics[width=\\linewidth]{figures/'+stem+'.pdf}\n'
                '\\setcounter{figure}{'+str(number-1)+'}\n'
                '\\caption{'+tex_fragment(caption)+'}\n\\label{'+label+'}\n'
                '\\Description{'+description+'}\n\\end{'+env+'}\n')

    text = re.sub(r'!\[(.*?)\]\(figures/([^/)]+)\.png\)\{#[^}]+\}', figure, text)

    # A single compact table is easier to read in one column than four long headers.
    table = re.compile(r'\| \$\\alpha\$ \|.*?\{#tab:backgrounds\}', re.S)
    def make_table(m):
        raw = m.group(0)
        rows = [line for line in raw.splitlines() if re.match(r'\| 1\.[14] \|', line)]
        cells = [r.strip('| ').split('|') for r in rows]
        body = '\n'.join(' & '.join(c.strip() for c in row) + r' \\' for row in cells)
        caption = raw.split('\n\n: ', 1)[1].split(' {#tab:', 1)[0]
        return ('\n\\begin{table}[t]\n\\centering\n'
                '\\caption{'+tex_fragment(caption)+'}\n\\label{tab:backgrounds}\n'
                '\\begin{tabular}{@{}crrrr@{}}\n\\toprule\n'
                '& \\multicolumn{2}{c}{Predefined (\\%)} & \\multicolumn{2}{c}{Broad grid (\\%)} \\\\\n'
                '\\cmidrule(lr){2-3}\\cmidrule(l){4-5}\n'
                '$\\alpha$ & Increase & Decrease & Increase & Decrease \\\\\n\\midrule\n'
                +body+'\n\\bottomrule\n\\end{tabular}\n\\end{table}\n')
    text = table.sub(make_table, text)
    result = tex_fragment(text)
    if path.name == '03.method.en.md':
        result = result.replace('\\qquad\n\\alpha_o=', '\\\\\n\\alpha_o=')
        result = re.sub(r'\\\[\s*(.*?)\s*\\\]',
                        lambda m: '\\begin{equation}\n'+('\\begin{gathered}\n'+m.group(1)+'\n\\end{gathered}' if '\\\\' in m.group(1) else m.group(1))+'\n\\end{equation}',
                        result, flags=re.S)
    for number, label in enumerate([x[0] for x in FIGURE_META.values()], 1):
        result = re.sub(r'Figure '+str(number)+r'\b', r'Figure~\\ref{'+label+'}', result)
    result = result.replace('Table 1', r'Table~\ref{tab:backgrounds}')
    result = result.replace('Appendix A', r'Appendix~\ref{app:reproducibility}')
    return result+'\n'


def prepare():
    (TEX/'sections').mkdir(parents=True, exist_ok=True)
    (TEX/'figures').mkdir(exist_ok=True)
    for stem in FIGURE_META:
        src = FIGURES / (stem+'.pdf')
        if stem == 'method-light':
            src = HERE/'assets/method-light.pdf'
        shutil.copy2(src, TEX/'figures'/src.name)
    for name in ['acmart.cls','ACM-Reference-Format.bst','orcidlink.sty']:
        source = Path(run(['kpsewhich',name], capture_output=True).stdout.strip())
        shutil.copy2(source, TEX/name)
    shutil.copy2(HERE/'references.bib', TEX/'references.bib')
    abstract = (MD/'00.abstract.en.md').read_text().split('\n',1)[1].strip()
    (TEX/'sections/abstract.tex').write_text(tex_fragment(abstract)+'\n')
    for p in sorted(MD.glob('0[1-5].*.en.md')):
        rendered = section(p)
        if p.name == '04.experiments.en.md':
            # Wide and single-column figures have independent placement.
            # Explicit caption numbers preserve the manuscript reference order.
            blocks = list(re.finditer(r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}', rendered, re.S))
            sweep = next(m.group(0) for m in blocks if 'figures/figure1-light.pdf' in m.group(0))
            icons = next(m.group(0) for m in blocks if 'figures/icon-examples-light.pdf' in m.group(0))
            rendered = rendered.replace(sweep, '')
            (TEX/'sections/experiment-figures.tex').write_text(sweep+'\n')
            runtime = next(m.group(0) for m in blocks if 'figures/timing-sweep-light.pdf' in m.group(0))
            colors = next(m.group(0) for m in blocks if 'figures/color-examples-light.pdf' in m.group(0))
            rendered = rendered.replace(runtime, '')
            rendered = rendered.replace(icons, icons+'\n\n'+runtime)
            table = re.search(r'\\begin\{table\}.*?\\end\{table\}', rendered, re.S).group(0)
            rendered = rendered.replace(table, '')
            rendered = rendered.replace(icons, icons+'\n\n'+table.replace('[t]', '[!htbp]', 1))
        if p.name == '03.method.en.md':
            match = re.search(r'\\begin\{figure\*\}.*?\\end\{figure\*\}', rendered, re.S)
            (TEX/'sections/method-figure.tex').write_text(match.group(0)+'\n')
            rendered = rendered[:match.start()] + rendered[match.end():]
        (TEX/'sections'/(p.name.split('.')[1]+'.tex')).write_text(rendered)
    ack = (MD/'06.acknowledgments.en.md').read_text().split('\n',1)[1].strip()
    (TEX/'sections/acknowledgments.tex').write_text(tex_fragment(ack)+'\n')
    appendix = section(MD/'07.appendix.en.md')
    appendix = appendix.replace('\\section{Reproducibility Details}', '\\section{Reproducibility Details}\\label{app:reproducibility}')
    appendix = appendix.replace('\\begin{figure}[H]\n\\centering\n\\includegraphics[width=\\linewidth]{figures/background-gallery-1.pdf}', '\\end{multicols}\n\\clearpage\n\\begin{figure}[H]\n\\centering\n\\includegraphics[width=\\linewidth]{figures/background-gallery-1.pdf}')
    appendix = appendix.replace('Source and background grids are uniformly spaced', '\\clearpage\n\\onecolumn\n\\begin{multicols}{2}\nSource and background grids are uniformly spaced')
    # Insert the page break at the second plate only.
    appendix = appendix.replace('\\begin{figure}[H]\n\\centering\n\\includegraphics[width=\\linewidth]{figures/background-gallery-2.pdf}', '\\clearpage\n\\begin{figure}[H]\n\\centering\n\\includegraphics[width=\\linewidth]{figures/background-gallery-2.pdf}')
    (TEX/'sections/appendix.tex').write_text(appendix)
    shutil.copy2(HERE/'main.template.tex', TEX/'main.tex')


def build():
    run(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','-file-line-error','main.tex'], cwd=TEX,
        stdout=(HERE/'review/latexmk-output.txt').open('w'), stderr=subprocess.STDOUT)
    output=ROOT/'output/preprint';output.mkdir(parents=True,exist_ok=True)
    shutil.copy2(TEX/'main.pdf',output/'opacity-is-not-just-opacity.pdf')
    files=[*MD.glob('0*.en.md'),MD/'title.md',HERE/'references.bib',HERE/'main.template.tex',HERE/'build.py']
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (HERE/'review/build-inputs.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(output/'opacity-is-not-just-opacity.pdf')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--reader-only',action='store_true')
    args=parser.parse_args()
    (HERE/'review').mkdir(parents=True, exist_ok=True)
    reader()
    if not args.reader_only:
        prepare()
        build()
