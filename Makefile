.PHONY: bun-download
bun-download:
	npm install -g bun
	curl -fsSL https://bun.sh/installer/bun.sh | bash

.PHONY: cargo-download
cargo-download:
	curl https://sh.rustup.rs -sSf | sh -s -- -y

.PHONY: uv-download
uv-download:
	curl -LsSf https://astral.sh/uv/install.sh | sh

.PHONY: install
install:
	cd client && bun install && cd ..

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

.PHONY: diagram
diagram:
	pydeps apiary --max-bacon=2 -o=docs/img/apiary.svg --no-show  --cluster
