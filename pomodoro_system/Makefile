.PHONY: install_dev
install_dev:
	pip install -r requirements/base.txt
	pip install -r requirements/dev.txt


.PHONY: freeze-dependencies
freeze-dependencies:
	pip install poetry==1.1.0
	poetry export --without-hashes -o requirements/base.txt
	poetry export --dev --without-hashes -o requirements/dev.txt


.PHONY: coverage-html-reports
coverage-html-reports:
	pytest --cov-report=html:coverage_html --cov=./


.PHONY: coverage-xml-reports
coverage-xml-reports:
	pytest --cov-report=xml:coverage_xml --cov=./


.PHONY: run-linters
run-linters:
	flake8 ./
	black ./
	isort ./


.PHONY: check-linting
check-linting:
	flake8 ./
	black ./ --check
	isort ./ --check-only
