SHELL := /bin/bash

R_SCRIPT ?= Rscript
PYTHON_RUN ?= uv run
LATEX ?= xelatex

.PHONY: help setup setup-python setup-r fetch build analysis provenance asset-graph-check asset-graph-test asset-graph-query check agents all latex articles slides compile-tex _compile-tex clean

define RUN_PIPELINE_SCRIPTS
	@set -e; \
	stage="$(1)"; \
	label="$(2)"; \
	scripts="$$(find "$$stage" -maxdepth 1 -type f \
		\( -name '*.sh' -o -name '*.py' -o -name '*.R' \) -print | LC_ALL=C sort | \
		grep -E '/[0-9]{2}_[a-z][a-z0-9]*(_[a-z0-9]+)*\.(sh|py|R)$$' || true)"; \
	if [ -z "$$scripts" ]; then \
		echo "[$$label] no numbered pipeline scripts found in $$stage/"; \
		echo "         add an entry point such as $$stage/01_verb_noun.py"; \
	else \
		while IFS= read -r script; do \
			echo "[$$label] running $$script"; \
			case "$$script" in \
				*.sh) bash "$$script" ;; \
				*.py) $(PYTHON_RUN) python "$$script" ;; \
				*.R) $(R_SCRIPT) "$$script" ;; \
			esac; \
		done <<< "$$scripts"; \
	fi
endef

help:
	@echo "Project workflow targets (run on host):"
	@echo "  make setup      Restore lockfiles (uv.lock / renv.lock if present)"
	@echo "  make fetch      Run numbered pipeline scripts in code/00_fetch/"
	@echo "  make build      Run numbered pipeline scripts in code/01_build/"
	@echo "  make analysis   Run numbered scripts + notebooks in code/02_analyze/"
	@echo "  make provenance Validate docs/data/provenance-ledger coverage"
	@echo "  make asset-graph-check  Validate Asset Graph identity, history, lineage, and freshness"
	@echo "  make asset-graph-test   Run Asset Graph unit and historical-lineage fixtures"
	@echo "  make asset-graph-query NODE=path-or-id  Show a compact node/adjacency view"
	@echo "  make agents     Regenerate .codex/agents/*.toml from .claude/agents/*.md"
	@echo "  make check      Validate Claude Code / Codex cross-harness parity"
	@echo "  make latex      Compile every root .tex document in articles/ and slides/"
	@echo "  make articles   Compile every root .tex document in docs/deliverables/articles/"
	@echo "  make slides     Compile every root .tex document in docs/deliverables/slides/"
	@echo "  make all        setup -> fetch -> build -> analysis -> provenance -> check"
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
	$(call RUN_PIPELINE_SCRIPTS,code/00_fetch,fetch)

build:
	$(call RUN_PIPELINE_SCRIPTS,code/01_build,build)

analysis:
	$(call RUN_PIPELINE_SCRIPTS,code/02_analyze,analysis)
	@set -e; \
	notebooks="$$(find code/02_analyze -maxdepth 1 -type f -name '*.ipynb' -print | LC_ALL=C sort | \
		grep -E '/[0-9]{2}_[a-z][a-z0-9]*(_[a-z0-9]+)*\.ipynb$$' || true)"; \
	if [ -z "$$notebooks" ]; then \
		echo "[analysis] no numbered pipeline notebooks found in code/02_analyze/"; \
	else \
		while IFS= read -r nb; do \
			base=$$(basename "$$nb" .ipynb); \
			echo "[analysis] executing notebook $$nb"; \
			$(PYTHON_RUN) jupyter nbconvert --to notebook --execute "$$nb" --output "$$base.executed.ipynb" --output-dir code/02_analyze; \
		done <<< "$$notebooks"; \
	fi

provenance:
	@python3 code/03_quality/check_provenance_ledger.py

asset-graph-check: provenance

asset-graph-test:
	@python3 -m unittest discover -s code/03_quality/tests -p 'test_asset_graph*.py'

asset-graph-query:
	@if [ -z "$(NODE)" ]; then \
		echo "Usage: make asset-graph-query NODE=path-or-id"; \
		exit 2; \
	fi
	@python3 code/03_quality/asset_graph.py show "$(NODE)" --format agent

agents:
	@python3 code/03_quality/gen_codex_agents.py

check:
	@python3 code/03_quality/check_conformance.py

all: setup fetch build analysis provenance check

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
