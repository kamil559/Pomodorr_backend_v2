.PHONY: install_dev
install_dev:
	pip install -r requirements/requirements.txt
	pip install -r requirements/dev.txt


.PHONY: freeze-dependencies
freeze-dependencies:
	pip install --user poetry==1.1.0
	poetry export --without-hashes -o requirements/base.txt
	poetry export --dev --without-hashes -o requirements/dev.txt
