SHELL := /bin/bash

PY = python3
VENV = .venv
BIN=$(VENV)/bin

PYTHON_VERSION=$(shell cat .tool-versions|grep 'python' | cut -d " " -f 2)
POETRY_VERSION=$(shell cat .tool-versions|grep 'poetry' | cut -d " " -f 2)

define title
@/bin/echo -e "\n------------------------------------------------\n${1}\n------------------------------------------------\n"
endef
define poetry
	$(call title, ${2})
	touch .env
	~/.asdf/shims/poetry run -vvv ${1}
endef

check: check-asdf

check-asdf:
	@if ! command -v asdf &> /dev/null; then \
		echo "Error: asdf is not installed. Please install asdf first."; \
		echo " => https://asdf-vm.com/guide/getting-started.html"; \
		exit 1; \
	fi

.ONESHELL:
.DEFAULT_GOAL := run

## Generate requirements.txt
generate-dependencies:
	poetry export --without-hashes --output src/requirements.txt

## Install dev environment
install: install-libdev install-asdf configure-poetry upgrade-pip

## Minimun install to speed run on Github
install-github:
	@$(call title,"ASDF Install in .tool-versions")
	asdf plugin-add poetry https://github.com/asdf-community/asdf-poetry.git
	asdf install poetry

install-libdev:
	@$(call title, Install libdev requirement for python\n=> https://github.com/pyenv/pyenv/wiki#suggested-build-environment)
	if [ "$(shell uname)" == "Darwin" ]; then \
		brew install openssl readline sqlite3 xz zlib tcl-tk; \
	else\
		sudo apt update; \
		sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev; \
	fi

install-asdf:
	@$(call title,"ASDF Install in .tool-versions")
	asdf plugin-add poetry https://github.com/asdf-community/asdf-poetry.git
	asdf plugin-add python
	asdf install

upgrade-pip:
	@$(call poetry, pip install --upgrade pip, "Upgrade pip")

configure-poetry:
	@$(call title,"Poetry set python version")
	@echo "Update python version $(PYTHON_VERSION) in pyproject.toml"
	sed -i 's/python = .*/python = "$(PYTHON_VERSION)"/g' pyproject.toml
	@echo "Update python version $(PYTHON_VERSION) in Dockerfile"
	sed -i 's/FROM python:.*/FROM python:$(PYTHON_VERSION)-slim/g' Dockerfile
	@echo "Update python version $(PYTHON_VERSION) in tox.ini"
	sed -i 's/min_python_version.*/min_python_version = $(PYTHON_VERSION)/g' tox.ini
	sed -i 's/FROM python:.*/FROM python:$(PYTHON_VERSION)-slim/g' Dockerfile
	@$(call title,"Switch venv to $(PYTHON_VERSION)")
	poetry env use ~/.asdf/installs/python/$(PYTHON_VERSION)/bin/python
	@$(call title,"Poetry self plugin")
	poetry self add poetry-plugin-export poetry-dotenv-plugin
	poetry self update
	@$(call title,"Poetry install")
	poetry install
	poetry update


clean: python-clean
## Clean venv
python-clean:
	rm -Rf $(VENV)

## Init local environment
init:
	if [ ! -f ".env" ]; then \
  		cp env.example .env; \
	fi

## Git Init
git-init:
	@$(call poetry, pre-commit install, "Install Pre-Commit in Git Hooks")

## Bootstap application
bootstrap:
	@$(call poetry, --ansi python src/main.py, "Run main.py")

## Enable debug mode
enable-debug:
	sed -i "s/DEBUG=.*/DEBUG=true/g" .env

## Disable debug mode
disable-debug:
	sed -i "s/DEBUG=.*/DEBUG=false/g" .env

## Enable debug mode
enable-dev:
	sed -i "s/DEV=.*/DEV=true/g" .env

## Disable debug mode
disable-dev:
	sed -i "s/DEV=.*/DEV=false/g" .env

## Run in local
run: init disable-debug bootstrap

## Run local dev (without debug)
dev: init disable-debug enable-dev bootstrap

## Run in local in debug
debug: init enable-debug bootstrap down

## Start all external ressource necessary to debug (MQTT, InfluxDB,...)
up:
	cd dev; docker compose up --force-recreate --detach; cd -

## Stop all external ressource necessary to debug (MQTT, InfluxDB,...)
down:
	docker compose -f dev/docker-compose.dev.yaml stop

## Run PyTest only
test: pytest

tnr: tox
## Run regression testing
tox: init
	@$(call poetry, tox, "Run TOX")

## Run PyTest
pytest: init
	@$(call poetry, tox -e pytest, "Run PyTest")

## Run black
black: init
	@$(call poetry, tox -e black, "Run Black")

## Run Black formater
black-format: init
	@$(call poetry, black --line-length 119 --color ., "Run Black formater")

##Run flake8
flake8: init
	@$(call poetry, tox -e flake8, "Run Flake8")

##Run pylint
pylint: init
	@$(call poetry, tox -e pylint, "Run pylint")

##Run pre-commit
pre-commit: init
	@$(call poetry, pre-commit run --all-files, "Run pre-commit test")

## Docker build
docker-build:
	docker build -t myelectricaldata_import:dev .