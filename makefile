.PHONY: codestyle
codestyle:
	poetry run autoflake --remove-unused-variables --remove-all-unused-imports --recursive --in-place .
	poetry run pyupgrade --exit-zero-even-if-changed --py37-plus **/*.py
	poetry run isort --settings-path pyproject.toml ./
	poetry run black --config pyproject.toml ./

.PHONY: lint
lint:
	poetry run flake8 --max-line-length=88 --ignore=E203,W503 --exclude=venv
	poetry run mypy . --check-untyped-defs