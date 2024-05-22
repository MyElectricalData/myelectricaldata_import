#!/bin/bash
set -x
export PATH=~/.asdf/bin:~/.asdf/shims:$PATH
export PATH=~/.asdf/installs/poetry/$POETRY_VERSION/bin:$PATH
make configure-poetry
make dev
