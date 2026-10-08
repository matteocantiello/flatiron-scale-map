PYTHON ?= python3

.PHONY: figures test clean help

help:  ## list targets
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-8s %s\n", $$1, $$2}'

figures:  ## render every layout to figures/ (PNG + PDF)
	$(PYTHON) -m scalemap

test:  ## run the test suite
	$(PYTHON) -m pytest -q

clean:  ## remove caches (keeps the committed figures)
	rm -rf .pytest_cache scalemap/__pycache__ tests/__pycache__
