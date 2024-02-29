SHELL := /bin/bash

PY = python3
VENV = .venv
BIN=$(VENV)/bin

PYTHON_VERSION=$(shell cat .tool-versions|grep 'python' | cut -d " " -f 2)

.ONESHELL:
.DEFAULT_GOAL := dev

######################################
## INSTALL/CONFIGURE LOCAL ENV
######################################
check: check-asdf
## Check ASDF install
check-asdf:
	@if ! command -v asdf &> /dev/null; then \
		echo "Error: asdf is not installed. Please install asdf first."; \
		echo " => https://asdf-vm.com/guide/getting-started.html"; \
		exit 1; \
	fi

## Init local environment file with exemple
init:
	if [ ! -f ".env" ]; then \
  		cp env.example .env; \
	fi

## Install dev environment
install: install-libdev install-asdf-full configure-poetry upgrade-pip

## Minimun install to speed run on Github
install-github:
	@$(call title,"ASDF Install in .tool-versions")
	asdf plugin-add poetry https://github.com/asdf-community/asdf-poetry.git
	asdf install poetry

## Install libdev for custom python version with ASDF
install-libdev:
	@$(call title, Install libdev requirement for python\n=> https://github.com/pyenv/pyenv/wiki#suggested-build-environment)
	if [ "$(shell uname)" == "Darwin" ]; then \
		brew install openssl readline sqlite3 xz zlib tcl-tk; \
	else\
		sudo apt update; \
		sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev; \
	fi

## Upgrade PIP
upgrade-pip:
	@$(call poetry, pip install --upgrade pip, "Upgrade pip")

## Full install for local dev
install-asdf-full:
	@$(call title,"ASDF Install in .tool-versions")
	asdf plugin-add poetry https://github.com/asdf-community/asdf-poetry.git
	asdf plugin-add python
	asdf plugin add pre-commit
	asdf install poetry
	asdf install python
	asdf install pre-commit

## Install poetry venv
install-poetry:
	poetry install

## Configure poetry for local dev
configure-poetry:
	@$(call title,"Poetry set python version")
	if [ "$(shell uname)" == "Darwin" ]; then \
		echo "Update python version $(PYTHON_VERSION) in pyproject.toml"
		sed -i '' 's/python = .*/python = "$(PYTHON_VERSION)"/g' pyproject.toml
		echo "Update python version $(PYTHON_VERSION) in Dockerfile"
		sed -i '' 's/FROM python:.*/FROM python:$(PYTHON_VERSION)-slim/g' Dockerfile
		echo "Update python version $(PYTHON_VERSION) in tox.ini"
		sed -i '' 's/min_python_version.*/min_python_version = $(PYTHON_VERSION)/g' tox.ini .flake8
	else\
		echo "Update python version $(PYTHON_VERSION) in pyproject.toml"
		sed -i 's/python = .*/python = "$(PYTHON_VERSION)"/g' pyproject.toml
		echo "Update python version $(PYTHON_VERSION) in Dockerfile"
		sed -i 's/FROM python:.*/FROM python:$(PYTHON_VERSION)-slim/g' Dockerfile
		echo "Update python version $(PYTHON_VERSION) in tox.ini & .flake8"
		sed -i 's/min_python_version.*/min_python_version = $(PYTHON_VERSION)/g' tox.ini .flake8
	fi
	@$(call title,"Switch venv to $(PYTHON_VERSION)")
	poetry env use ~/.asdf/installs/python/$(PYTHON_VERSION)/bin/python
	@$(call title,"Poetry self plugin")
	poetry self add poetry-plugin-export poetry-dotenv-plugin
	poetry self update
	@$(call title,"Poetry install")
	poetry install
	poetry update

######################################
## GIT
######################################
## Git Init
init-pre-commit:
	@$(call poetry, pre-commit install -t pre-commit -t commit-msg, "Init Pre-Commit in Git Hooks")

## Run Pre-Commit
pre-commit: init-pre-commit
	@$(call poetry, pre-commit run -a, "Run Pre-Commit")

######################################
## LOCAL RUNNING
######################################
## Run in local
run: init install-poetry disable-debug disable-dev
	@$(call poetry, --ansi python src/main.py, "Run main.py")

## Run in dev mode
dev: init install-poetry enable-debug enable-dev
	@$(call poetry, --ansi python src/main.py, "Run main.py")

## Enable debug mode
enable-debug:
	@$(call poetry, python -c "$$set_env" DEBUG true, "Enable debug mode")

## Disable debug mode
disable-debug:
	@$(call poetry, python -c "$$set_env" DEBUG False, "Disable debug mode")

## Enable debug mode
enable-dev:
	@$(call poetry, python -c "$$set_env" DEV true, "Enable dev mode")

## Disable debug mode
disable-dev:
	@$(call poetry, python -c "$$set_env" DEV false, "Disable dev mode")

######################################
## PYTHON PROCESSING
######################################
## Generate requirements.txt
generate-dependencies:
	@$(call title,"Generate requirements.txt")
	poetry export --without-hashes --output src/requirements.txt

clean: python-clean
## Clean venv
python-clean:
	rm -Rf $(VENV)

######################################
## TESTS
######################################
## Run PyTest
pytest: init
	if [ ! $$? -ne 0 ]; then \
		$(call poetry, tox -e pytest, "Run PyTest"); \
	fi

pytest-mock:
pytest-sandbox:
pytest-staging:
pytest-production:
pytest-%: 
	$(call poetry, tox -e pytest, "Run PyTest");

######################################
## CODE QUALITY
######################################
## Run regression testing
tox: init
	@$(call poetry, tox, "Run TOX")

format: code-format
## Check code formatting
code-format: black flake8 pylint ruff

## Run black
black: init
	@$(call poetry, task black, "Run Black")

## Run Black formater
black-format: init
	@$(call poetry, task black-style, "Run Black formater")

##Run flake8
flake8: init
	@$(call poetry, task flake8, "Run Flake8")

##Run pylint
pylint: init
	@$(call poetry, task pylint, "Run pylint")

##Run Ruff
ruff: init
	@$(call poetry, task ruff, "Run Ruff")

##Run Ruff fixe
ruff-fixe: init
	@$(call poetry, task ruff-fix, "Run Ruff fix code")

##Run Vulture
vulture: init
	@$(call poetry, task vulture, "Run Vulture")	

######################################
## DOCKER
######################################
## Build image
build: generate-dependencies
	@$(call title,"Build image in local")
	docker build ./

######################################
## MAKEFILE FUNCTION
######################################
define title
/bin/echo -e "\n------------------------------------------------\n${1}\n------------------------------------------------\n"
endef
define poetry
$(call title, ${2})
touch .env
poetry run -v ${1}
endef

######################################
## PYTHON SCRIPTS
######################################
define set_env
from sys import argv
KEY = argv[1]
VALUE = argv[2]
found = False
new_file = []
print(f"Set {KEY}={VALUE}")
with open(f".env", 'r') as file:
	env = file.read().splitlines()
for line in env:
	if line.startswith(f"{KEY}="):
		new_file.append(f"{KEY}={VALUE}")
		found = True
	else:
		new_file.append(line)
if not found:
	env.append(f"{KEY}={VALUE}")
else:
	env = new_file
with open(f".env", 'w') as file:
	file.write("\n".join(env))
endef
export set_env