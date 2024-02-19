#!/bin/bash
echo "Configure ZSH"
# Configure ZSH
mkdir -p ~/.local/share/fonts
curl -fL https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/patched-fonts/DroidSansMono/DroidSansMNerdFontMono-Regular.otf --output ~/.local/share/fonts/DroidSansMNerdFontMono-Regular.otf 
git clone https://github.com/tarjoilija/zgen.git "${HOME}/.zgen"
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
cp .devcontainer/zshrc "${HOME}/.zshrc"
echo ""
echo "Install ASDF"
git clone https://github.com/asdf-vm/asdf.git ~/.asdf
echo '. "$HOME/.asdf/asdf.sh"'  >> ~/.bashrc
echo '. "$HOME/.asdf/completions/asdf.bash"'  >> ~/.bashrc
echo ""
echo "Source bashrc"
export PATH=~/.asdf/bin:~/.asdf/shims:$PATH
POETRY_VERSION=$(cat .tool-versions|grep 'poetry' | cut -d " " -f 2)
export PATH=~/.asdf/installs/poetry/$POETRY_VERSION/bin:$PATH
echo ""
echo "Disable SSL check in Curl"
echo "insecure" >> ${HOME}/.curlrc
sudo update-ca-certificates --fresh
echo ""
echo "Install environment"
make install