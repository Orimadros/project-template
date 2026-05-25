SHELL := /bin/bash

R_SCRIPT ?= Rscript
PYTHON_RUN ?= uv run
LATEX ?= xelatex

.PHONY: help setup setup-python setup-r fetch build analysis latex articles slides compile-tex _compile-tex clean

help:
	@echo "Project workflow targets (run on host):"
	@echo "  make setup      Restore lockfiles (uv.lock / renv.lock if present)"
	@echo "  make fetch      Run shell scripts in code/00_fetch/"
	@echo "  make build      Run R scripts in code/01_build/"
	@echo "  make analysis   Run R scripts + notebooks in code/02_analyze/"
	@echo "  make latex      Compile every root .tex document in articles/ and slides/"
	@echo "  make articles   Compile every root .tex document in docs/deliverables/articles/"
	@echo "  make slides     Compile every root .tex document in docs/deliverables/slides/"
	@echo "  make all        setup -> fetch -> build -> analysis"
	@echo "  make clean      Delete generated files in data/clean, data/tmp, results"

setup: setup-python setup-r

setup-python:
	@if [ -f uv.lock ] && [ -f pyproject.toml ]; then \
		echo "[setup-python] uv.lock found -> running uv sync --frozen"; \
		uv sync --frozen; \
	else \
		echo "[setup-python] uv.lock or pyproject.toml not found -> skipping"; \
	fi

setup-r:
	@if [ -f renv.lock ]; then \
		echo "[setup-r] renv.lock found -> restoring R dependencies"; \
		$(R_SCRIPT) -e "if (!requireNamespace('renv', quietly=TRUE)) install.packages('renv', repos='https://cloud.r-project.org'); renv::restore(lockfile='renv.lock', prompt=FALSE)"; \
	else \
		echo "[setup-r] renv.lock not found -> skipping"; \
	fi

fetch:
	@if ls code/00_fetch/*.sh >/dev/null 2>&1; then \
		for script in $$(ls code/00_fetch/*.sh | sort); do \
			echo "[fetch] running $$script"; \
			bash "$$script"; \
		done; \
	else \
		echo "[fetch] no shell scripts found in code/00_fetch/"; \
		echo "        add scripts like code/00_fetch/00_download_xxx.sh"; \
	fi

build:
	@if ls code/01_build/*.R >/dev/null 2>&1; then \
		for script in $$(ls code/01_build/*.R | sort); do \
			echo "[build] running $$script"; \
			$(R_SCRIPT) "$$script"; \
		done; \
	else \
		echo "[build] no R scripts found in code/01_build/"; \
		echo "        add scripts like code/01_build/00_clean_xxx.R"; \
	fi

analysis:
	@if ls code/02_analyze/*.R >/dev/null 2>&1; then \
		for script in $$(ls code/02_analyze/*.R | sort); do \
			echo "[analysis] running $$script"; \
			$(R_SCRIPT) "$$script"; \
		done; \
	else \
		echo "[analysis] no R scripts found in code/02_analyze/"; \
	fi
	@if ls code/02_analyze/*.ipynb >/dev/null 2>&1; then \
		for nb in $$(ls code/02_analyze/*.ipynb | sort); do \
			base=$$(basename "$$nb" .ipynb); \
			echo "[analysis] executing notebook $$nb"; \
			$(PYTHON_RUN) jupyter nbconvert --to notebook --execute "$$nb" --output "$$base.executed.ipynb" --output-dir code/02_analyze; \
		done; \
	else \
		echo "[analysis] no notebooks found in code/02_analyze/"; \
	fi

all: setup fetch build analysis

latex: articles slides

compile-tex: latex

articles:
	@$(MAKE) _compile-tex TEX_ROOT=docs/deliverables/articles

slides:
	@$(MAKE) _compile-tex TEX_ROOT=docs/deliverables/slides

_compile-tex:
	@if [ ! -d "$(TEX_ROOT)" ]; then \
		echo "[latex] $(TEX_ROOT) not found -> skipping"; \
		exit 0; \
	fi; \
	docs="$$(find "$(TEX_ROOT)" -name '*.tex' -type f -print | sort | while read -r tex; do \
		if grep -q '^[[:space:]]*\\documentclass' "$$tex"; then \
			echo "$$tex"; \
		fi; \
	done)"; \
	if [ -z "$$docs" ]; then \
		echo "[latex] no root .tex documents found under $(TEX_ROOT)"; \
		exit 0; \
	fi; \
	preamble_dir="$$(pwd)/docs/deliverables/preambles"; \
	bib_dir="$$(pwd)/docs/sources"; \
	status=0; \
	while IFS= read -r tex; do \
		dir="$$(dirname "$$tex")"; \
		file="$$(basename "$$tex")"; \
		base="$${file%.tex}"; \
		echo "[latex] compiling $$tex"; \
		( cd "$$dir" && \
		  TEXINPUTS=".:$$preamble_dir:./sections:$${TEXINPUTS:-}" $(LATEX) -interaction=nonstopmode "$$file" && \
		  if [ -f "$$base.aux" ] && grep -q "\\\\citation" "$$base.aux"; then \
		    BIBINPUTS="$$bib_dir:$${BIBINPUTS:-}" bibtex "$$base"; \
		  fi && \
		  TEXINPUTS=".:$$preamble_dir:./sections:$${TEXINPUTS:-}" $(LATEX) -interaction=nonstopmode "$$file" && \
		  TEXINPUTS=".:$$preamble_dir:./sections:$${TEXINPUTS:-}" $(LATEX) -interaction=nonstopmode "$$file" ); \
		rc=$$?; \
		if [ "$$rc" -ne 0 ]; then status=$$rc; fi; \
	done <<< "$$docs"; \
	exit "$$status"

clean:
	@echo "[clean] removing generated artifacts from data/clean, data/tmp, and results"
	@find data/clean -mindepth 1 -delete 2>/dev/null || true
	@find data/tmp -mindepth 1 -delete 2>/dev/null || true
	@find results -mindepth 1 ! -name '.gitkeep' -delete 2>/dev/null || true
