PYTHON ?= python3

.PHONY: harness-check harness-test evidence-capture archive-audit file-manifest bundle

harness-check:
	$(PYTHON) tools/validate_harness.py

harness-test:
	$(PYTHON) -m unittest discover -s tests -v

evidence-capture:
	$(PYTHON) tools/run_static_checks.py H0 --root . --output audit/logs/H0_STATIC_CHECKS.json
	$(PYTHON) tools/run_static_checks.py H1 --root . --output audit/logs/H1_STATIC_CHECKS.json

archive-audit:
	@test -n "$(ARCHIVE)" || (echo "usage: make archive-audit ARCHIVE=/absolute/path" >&2; exit 2)
	$(PYTHON) tools/audit_archive.py "$(ARCHIVE)"

file-manifest:
	$(PYTHON) tools/build_file_manifest.py --root . --output audit/FILE_MANIFEST.sha256

bundle:
	@test -n "$(OUTPUT)" || (echo "usage: make bundle OUTPUT=/absolute/path.zip" >&2; exit 2)
	$(PYTHON) tools/create_bundle.py --root . --output "$(OUTPUT)"
