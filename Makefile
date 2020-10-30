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


.PHONY: test_with_html_coverage
test_with_html_coverage:
	pytest --cov-report=html:coverage_html --cov=./


.PHONY: test_with_xml_coverage
test_with_xml_coverage:
	pytest --cov-report=xml:coverage_xml --cov=./


.PHONY: run_linters
run_linters:
	black ./
	isort ./
	flake8 ./


.PHONY: check_linting
check_linting:
	black ./ --check
	isort ./ --check-only
	flake8 ./


.PHONY: install_git_hooks
install_git_hooks:
	pre-commit install
