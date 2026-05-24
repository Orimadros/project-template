SHELL := /bin/bash

R_SCRIPT ?= Rscript
PYTHON_RUN ?= uv run

.PHONY: help setup setup-python setup-r fetch build analysis all clean

help:
	@echo "Project workflow targets (run on host):"
	@echo "  make setup      Restore lockfiles (uv.lock / renv.lock if present)"
	@echo "  make fetch      Run shell scripts in code/00_fetch/"
	@echo "  make build      Run R scripts in code/01_build/"
	@echo "  make analysis   Run R scripts + notebooks in code/02_analyze/"
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

clean:
	@echo "[clean] removing generated artifacts from data/clean, data/tmp, and results"
	@find data/clean -mindepth 1 -delete 2>/dev/null || true
	@find data/tmp -mindepth 1 -delete 2>/dev/null || true
	@find results -mindepth 1 ! -name '.gitkeep' -delete 2>/dev/null || true
