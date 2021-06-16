SRC_DIR = src
OUTPUT_DIR = outputs
SCRIPTS_DIR = scripts

PYTHON_FILES = $(wildcard $(SRC_DIR)/*.py)
PYTHON_FILES += $(wildcard $(SCRIPTS_DIR)/*.py)

.PHONY: clean lint check-black check-isort

$(OUTPUT_DIR):
	@mkdir -p $(OUTPUT_DIR)

lint: check-black check-isort check-pylint check-mypy

check-black:
	black --check $(PYTHON_FILES)

check-isort:
	isort --check $(PYTHON_FILES)

check-pylint:
	pylint $(PYTHON_FILES)

check-mypy:
	mypy $(PYTHON_FILES)

clean:
	rm -rf $(OUTPUT_DIR)
