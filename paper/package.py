#!/usr/bin/env python3
"""Package the generated preprint and verify its standalone compilation."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
TEX = HERE / 'latex'
OUT = HERE.parent / 'output/preprint'
ARCHIVE = OUT / 'opacity-is-not-just-opacity-arxiv.tar.gz'
FILES = [TEX / name for name in ['main.tex', 'main.bbl', 'references.bib',
         'acmart.cls', 'ACM-Reference-Format.bst', 'orcidlink.sty']]
FILES += sorted((TEX/'sections').glob('*.tex')) + sorted((TEX/'figures').glob('*.pdf'))
(TEX/'LICENSE-lucide.txt').write_bytes((HERE.parent/'experiments/formal-evaluation/assets/LICENSE').read_bytes())
FILES.append(TEX/'LICENSE-lucide.txt')

for path in FILES:
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.suffix == '.tex' and '/Users/' in path.read_text():
        raise ValueError(f'Local absolute path in {path.name}')

with tarfile.open(ARCHIVE, 'w:gz', format=tarfile.PAX_FORMAT) as archive:
    for path in FILES:
        archive.add(path, arcname=str(path.relative_to(TEX)), recursive=False)

with tempfile.TemporaryDirectory(prefix='opacity-arxiv-check-') as temp:
    directory = Path(temp)
    with tarfile.open(ARCHIVE) as archive:
        for member in archive.getmembers():
            if not member.isfile() or Path(member.name).is_absolute() or '..' in Path(member.name).parts:
                raise ValueError('Unexpected archive member: '+member.name)
            target = directory / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())
    # Use only the extracted project and the installed TeX distribution.
    env = dict(os.environ)
    for variable in ['TEXINPUTS', 'BIBINPUTS', 'BSTINPUTS']:
        env.pop(variable, None)
    result = subprocess.run(['latexmk', '-pdf', '-interaction=nonstopmode',
                             '-halt-on-error', '-file-line-error', 'main.tex'],
                            cwd=directory, env=env, capture_output=True, text=True)
    (HERE/'review/archive-build.txt').write_text(result.stdout + result.stderr)
    result.check_returncode()
    log = (directory/'main.log').read_text()
    problems = re.findall(r'^.*(?:Warning|Overfull|Underfull|undefined|Missing character).*$', log, re.M)
    if problems:
        raise RuntimeError('\n'.join(problems))
    def extracted_text(path):
        return subprocess.check_output(['pdftotext', '-layout', str(path), '-'], text=True)
    if extracted_text(directory/'main.pdf') != extracted_text(TEX/'main.pdf'):
        raise RuntimeError('Standalone PDF text differs from the main build')
    # Keep the isolated build for a rendered-page comparison.
    (HERE/'review/archive-check.pdf').write_bytes((directory/'main.pdf').read_bytes())

manifest = {str(p.relative_to(TEX)): hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES}
report = {'archive': ARCHIVE.name, 'archive_bytes': ARCHIVE.stat().st_size,
          'archive_sha256': hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
          'files': manifest, 'standalone_build': 'passed', 'pdf_text_matches': True,
          'tex_warnings': []}
(HERE/'review/archive-check.json').write_text(json.dumps(report, indent=2)+'\n')
print(ARCHIVE)
print(f'{len(FILES)} files; {ARCHIVE.stat().st_size:,} bytes; standalone compilation and PDF text match passed')
