# order of libs is meaningful. First, we install libs without internal dependencies that other libs depend on.
libs := foundation pomodoros

define install_dependency
	pip install -e $(1)
endef

.PHONY: install_dev
install_dev:
	pip install -r requirements.txt -r requirements-dev.txt
	$(foreach lib,$(libs),$(call install_dependency,$(lib)))

.PHONY: freeze-dependencies
freeze-dependencies:
	pip install pip-tools==4.4.1
	pip-compile --output-file=base.txt $(foreach lib,$(libs), ./$(lib)/requirements/base.txt ./$(lib)/requirements/dev.txt)
