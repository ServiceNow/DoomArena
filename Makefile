.PHONY: tests ci-tests install

tests:
	pytest doomarena/core/tests
	pytest doomarena/browsergym/tests
	pytest doomarena/taubench/tests

ci-tests:
	pytest -m 'not local' doomarena/core/tests
	pytest -m 'not local' doomarena/browsergym/tests
	pytest -m 'not local' doomarena/taubench/tests

install:
	pip install -e doomarena/core
	pip install -e doomarena/browsergym
	pip install -e doomarena/taubench
	@echo "Make sure to install taubench manually, see instructions in doomarena/taubench/README.md"

format:
	black .

.PHONY: dry-release
dry-release:
	@echo "### 🏷️  Latest existing tags (most recent first):"
	@git tag --sort=-creatordate | head -n 5 || echo "No tags yet"
	@echo ""

	@echo "### 📦 Current versions in pyproject.toml files:"
	@printf "doomarena-core:        %s\n" "$$(grep -E '^\s*version\s*=' doomarena/core/pyproject.toml | head -n1)"
	@printf "doomarena-browsergym:  %s\n" "$$(grep -E '^\s*version\s*=' doomarena/browsergym/pyproject.toml | head -n1)"
	@printf "doomarena-taubench:    %s\n" "$$(grep -E '^\s*version\s*=' doomarena/taubench/pyproject.toml | head -n1)"
	@echo ""

	@if [ -z "$(version)" ]; then \
		echo "❌ Please specify a version, e.g., 'make dry-release version=0.1.0'"; \
		exit 1; \
	fi

	@echo "To make the release, follow these steps (you can also check https://packaging.python.org/en/latest/tutorials/packaging-projects/):"
	@echo "Make sure to (separately) register and get your API keys from pypi.org and test.pypi.org"
	@echo ""

	@echo "### 1. Ensure required tools are installed"
	@echo "pip install build twine"
	@echo ""

	@echo "### 2. Confirm all versions are correctly set to '$(version)' in:"
	@echo "  - doomarena/core/pyproject.toml"
	@echo "  - doomarena/browsergym/pyproject.toml"
	@echo "  - doomarena/taubench/pyproject.toml"
	@echo ""

	@echo "### 3. Build and upload each package to PyPI (please use --repository testpypi for testing first!!)"
	@echo "(cd doomarena/core && python -m build && twine upload dist/*)"
	@echo "(cd doomarena/browsergym && python -m build && twine upload dist/*)"
	@echo "(cd doomarena/taubench && python -m build && twine upload dist/*)"
	@echo ""

	@echo "### 4. Test it's working"
	@echo "conda create python=3.12 --name doomarena-test-$(version)"
	@echo "conda activate doomarena-test-$(version)"
	@echo "FOR TESTING: pip install --index-url https://test.pypi.org/simple/ doomarena==$(version) --no-deps"
	@echo "FOR REAL: pip install doomarena browsergym taubench"
	@echo "Then run: make tests"
	@echo ""

	@echo "### 5. Tag the release and push to GitHub"
	@echo "git tag -a v$(version) -m \"Release v$(version)\""
	@echo "git push origin v$(version)"
	@echo ""

	@echo "### ✅ All release steps printed for version $(version)"
	@echo "### ⚠️ IMPORTANT: You may want to copy this output somewhere for reference as you're running these steps"
