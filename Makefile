.PHONY: install_dev
install_dev:
	pip install poetry==1.1.0
	poetry config virtualenvs.create false
	poetry install

.PHONY: freeze_dependencies
freeze_dependencies:
	pip install poetry==1.1.0
	poetry export --without-hashes -o requirements/base.txt
	poetry export --dev --without-hashes -o requirements/dev.txt


.PHONY: generate_coverage_html
generate_coverage_html:
	pytest --cov-report=html:coverage_html --cov=./


.PHONY: generate_coverage_xml
generate_coverage_xml:
	pytest --cov-report=xml:coverage_xml --cov=./


.PHONY: run_linters
run_linters:
	flake8 ./
	black ./
	isort ./


.PHONY: check_linting
check_linting:
	flake8 ./
	black ./ --check
	isort ./ --check-only


.PHONY: install_git_hooks
install_git_hooks:
	pre-commit install
