COMPOSE=docker-compose -f docker-compose.dev.yml

## Start docker conatiners for dev
up: .env
	@echo "Start docker container for dev"
	$(COMPOSE) up -d
	@echo ""
	@echo "\033[0;33mMQTT Explorer:\033[0m    \033[0;32mhttp://127.0.0.1:4000\033[0m    Auth info: (host: mosquitto)"
	@echo "\033[0;33mInflux DB:    \033[0m    \033[0;32mhttp://127.0.0.1:8086\033[0m    Auth info: (user: enedisgateway2mqtt, pawword: enedisgateway2mqtt)"
	
## Stop docker conatiners for dev
down: .env
	@echo "Start docker conatiner for dev"
	$(COMPOSE) down

## Start in app
start:
	$(COMPOSE) exec enedisgateway2mqtt python -u /app/main.py
	
## Connect to enedisgateway2mqtt container
bash:
	$(COMPOSE) exec enedisgateway2mqtt bash

## Create git branch
version=
git_branch:
	git branch $(version) || true
	git checkout $(version) || true
	echo $(branch) > app/VERSION

## Create add/commit/push
current_version := $(shell cat app/VERSION)
comment=
.PHONY: git_push
git_push:
	set -x
	@(echo "git add --all")
	git add --all
	@if [ "$(comment)" = "" ]; then comment="maj"; fi; \
    echo "git commit -m '$${comment}'"
	git commit -m "$${comment}"
	@(echo "git push origin $(current_version)")
	git push origin $(current_version)

.DEFAULT_GOAL := help
.PHONY: help
help:
	@echo "\033[0;33mUsage:\033[0m"
	@echo "     make [var_name=value ...] [target]\n"
	@echo "\033[0;33mAvailable variables:\033[0m"
	@echo ""
	@awk '/^[a-zA-Z\-_0-9\.@]+:/ {\
				helpMessage = match(lastLine, /^## (.*)/); \
				if (helpMessage) { \
					helpCommand = substr($$1, 0, index($$1, ":")); \
					helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
					printf "%s     \033[0;32m%-22s\033[0m   %s\n", key, helpCommand, helpMessage; \
				} \
			} \
			{lastLine = $$0;}' $(MAKEFILE_LIST)\
			| sed  -e "s/\`/\\\\\`/g"
	@echo ""