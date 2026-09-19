# IJCAI Submission Notes

## Format

- Official IJCAI-ECAI 2026 style file: `paper/ijcai26.sty`
- Anonymous main-track author block.
- US Letter page size.
- Two-column IJCAI layout.
- Line numbers enabled for review.
- Main paper body occupies 7 pages; the reference list continues onto a separate 8th page, which is within the conference allowance for reference pages.
- No Unicode em dash, en dash, or minus characters appear in the Markdown manuscript.

## Build

From `paper/`:

1. `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
2. `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
3. Copy `main.pdf` to `preprint.pdf`.

The environment did not provide `tectonic` or classic `bibtex`; the final source uses an inline `thebibliography` block, so two PDFLaTeX passes are sufficient.

## Final preflight

- `pdflatex`: successful.
- PDF pages: 8 total, 7 content pages plus reference overflow page.
- Page size: US Letter.
- Encrypted: no.
- Overfull boxes: 0.
- Undefined citation warnings: 0.
- Undefined reference warnings: 0.
- Rerun warnings: 0.
- Tests: 7/7 passed.
- Development seeds: 100 through 104.
- Held-out seeds: 0 through 19.
- Training cases: 6,000 with seed 901.
- Selected investigation cost: 0.4.

## Final held-out result

The two-step policy has mean decision cost 81.51 +/- 3.70 at a 95 percent seed-level t confidence interval, compared with 84.92 +/- 3.97 for one-step VOI, 92.75 +/- 3.83 for EIG, 99.60 +/- 4.63 for always-acquire, and 231.30 +/- 3.74 for the static threshold baseline.

## Important interpretation

The revision changes the evidence model, state costs, and acquisition horizon together. The paper therefore presents the main comparison as a controlled engineering ablation, not as a causal decomposition proving that one component alone explains the improvement.
