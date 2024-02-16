#!/bin/bash
echo "Install ASDF"
git clone https://github.com/asdf-vm/asdf.git ~/.asdf
echo '. "$HOME/.asdf/asdf.sh"'  >> ~/.bashrc
echo '. "$HOME/.asdf/completions/asdf.bash"'  >> ~/.bashrc

echo "Source bashrc"
export PATH=~/.asdf/bin:~/.asdf/shims:$PATH
POETRY_VERSION=$(cat .tool-versions|grep 'poetry' | cut -d " " -f 2)
export PATH=/~/.asdf/installs/poetry/${POETRY_VERSION}/bin:$PATH

echo "Install environment"
make install