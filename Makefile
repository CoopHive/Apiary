#* Poetry
.PHONY: client-install
bun-install:
	curl -fsSL https://bun.sh/installer/bun.sh | bash
	cd client && bun install && cd ..

.PHONY: uv-download
uv-download:
	curl -LsSf https://astral.sh/uv/install.sh | sh

.PHONY: install
install:
	cargo update
	cargo build

	rm -rf .venv && uv venv
	uv pip install .[dev]
	uvx maturin develop
	uv run pre-commit install

.PHONY: codestyle
codestyle:
	uv run isort ./
	uv run ruff check ./
	uv run ruff format ./

.PHONY: check-codestyle
check-codestyle:
	uv run isort --diff --check-only ./
	uv run ruff check --exit-non-zero-on-fix ./
	uv run ruff format --diff ./

.PHONY: docs
docs:
	uv run pydocstyle --convention=google .

.PHONY: test
test:
	uv run pytest -c pyproject.toml tests/

.PHONY: diagrams
diagrams:
	pyreverse apiary -A --colorized -p apiary -d docs/img -o dot
	python3 docs/classes_filter.py
	dot -Tpng docs/img/classes_apiary.dot -o docs/img/classes_apiary.png
	dot -Tpng docs/img/packages_apiary.dot -o docs/img/packages_apiary.png
