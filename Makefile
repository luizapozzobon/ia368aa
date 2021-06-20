SRC_DIR = src
OUTPUT_DIR = outputs
SCRIPTS_DIR = scripts

PYTHON_FILES = $(wildcard $(SRC_DIR)/*.py)
PYTHON_FILES += $(wildcard $(SCRIPTS_DIR)/*.py)

.PHONY: clean lint check-black check-isort


correlate: $(OUTPUT_DIR)
	python -m $(SRC_DIR).vis.correlate

population_trend: $(OUTPUT_DIR)
	python -m $(SRC_DIR).vis.population_trend

homicides_per_capita: $(OUTPUT_DIR)
	python -m $(SCRIPTS_DIR).homicides_per_capita

parse_ideb: $(OUTPUT_DIR)
	python -m $(SCRIPTS_DIR).parse_ideb \
		--networks Pública Estadual Municipal Federal \
		--school_levels anos_iniciais anos_finais ensino_medio


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
