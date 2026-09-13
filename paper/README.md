# Opacity Is Not Just Opacity

Named preprint in the ACM `sigconf` two-column format used by The Web Conference. `nonacm` omits publication metadata for this unpublished manuscript. The author, affiliation, email, and ORCID are included.

## Sources

- `../markdown/00.abstract.en.md` through `07.appendix.en.md`: reviewed English sections.
- `../markdown/manuscript.en.md`: complete English reader with resolved references and figures.
- `../markdown/terminology.md`: terminology decisions.
- `main.template.tex`, `references.bib`: typesetting and verified references.
- `review/`: content, numerical, citation, and output checks.

## Build

From the repository root:

```sh
python3 paper/build.py
```

Requires Python 3, Pandoc, and a TeX installation providing pdfLaTeX, BibTeX, latexmk, acmart, orcidlink, placeins, float, and multicol. The build uses existing PDF figure exports; no figure conversion or browser is required. Markdown owns the text. Generated TeX is in `paper/latex/`; layout-only float placement is handled by the generator.

Outputs are in `output/preprint/`. To regenerate only the English reader, use `python3 paper/build.py --reader-only`.

After a successful build, `python3 paper/package.py` creates the arXiv source archive and verifies compilation in an isolated temporary directory. The archive includes a root `main.tex`, section files, PDF figures, BibTeX data and generated bibliography, and the unmodified local ACM class and styles. It excludes the compiled manuscript, build intermediates, experiments, and local paths.

The supplied class and styles retain their upstream license notices. They are bundled for reproducibility; no changes are made to them. This is a named preprint, not an anonymous submission or an accepted conference paper.
