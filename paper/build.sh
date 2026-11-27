#!/usr/bin/env bash
set -euo pipefail
paper_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$paper_dir"
if [[ -d .toolchain/TinyTeX/bin/universal-darwin ]]; then
  export PATH="$paper_dir/.toolchain/TinyTeX/bin/universal-darwin:$PATH"
fi
export TEXINPUTS="$paper_dir/:$paper_dir/author-kit/AuthorKit27//:${TEXINPUTS:-}"
export BSTINPUTS="$paper_dir/:$paper_dir/author-kit/AuthorKit27//:${BSTINPUTS:-}"
export TEXMFVAR="$paper_dir/.toolchain/texmf-var"
export TEXMFCONFIG="$paper_dir/.toolchain/texmf-config"
export TEXMFHOME="$paper_dir/.toolchain/texmf-home"
export MPLCONFIGDIR="$paper_dir/build/matplotlib"
mkdir -p build
paper_python="${PAPER_PYTHON:-$paper_dir/../.venv/bin/python}"
"$paper_python" figures/make_figure1.py
"$paper_python" appendix/build_materials.py
"$paper_python" appendix/wrap_prompts.py
"$paper_python" appendix/build_tables.py
"$paper_python" prepare_tex.py
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex >build/pdflatex-first.stdout 2>&1
bibtex build/main >build/bibtex.stdout 2>&1
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex >build/pdflatex-second.stdout 2>&1
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex >build/pdflatex-final.stdout 2>&1
cp build/main.pdf main.pdf
printf 'Built %s/main.pdf\n' "$paper_dir"
