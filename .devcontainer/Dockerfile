# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT=3-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

# Install docker
RUN apt-get update \
    && apt-get install -y apt-transport-https ca-certificates curl gnupg2 lsb-release \
    && curl -fsSL https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]')/gpg | apt-key add - 2>/dev/null \
    && echo "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce-cli zsh git software-properties-common grc wget curl

# make the LOCAL variable and install it
ARG LOCAL=fr_FR.UTF-8
RUN apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
    && localedef -i $(echo ${LOCAL} | cut -d "." -f1) -c -f $(echo ${LOCAL} | cut -d "." -f2) -A /usr/share/locale/locale.alias ${LOCAL}
ENV LANG ${LOCAL}

RUN docker context use default
RUN docker buildx use default

ARG home=/home/vscode

USER vscode

COPY ./ /workspace

# ZSH
RUN mkdir -p ${home}/.local/share/fonts
RUN curl -fL https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/patched-fonts/DroidSansMono/DroidSansMNerdFontMono-Regular.otf --output ${home}/.local/share/fonts/DroidSansMNerdFontMono-Regular.otf 
RUN git clone https://github.com/tarjoilija/zgen.git "${home}/.zgen"
RUN git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-${home}/.oh-my-zsh/custom}/themes/powerlevel10k
RUN cp /workspace/.devcontainer/zshrc ${home}/.zshrc

# ASDF
RUN git clone https://github.com/asdf-vm/asdf.git ${home}/.asdf
RUN echo '. "$HOME/.asdf/asdf.sh"'  >> ${home}/.bashrc
RUN echo '. "$HOME/.asdf/completions/asdf.bash"'  >> ${home}/.bashrc
RUN echo '. "$HOME/.asdf/asdf.sh"'  >> ${home}/.zshrc
RUN echo '. "$HOME/.asdf/completions/asdf.bash"'  >> ${home}/.zshrc
RUN export PATH=~/.asdf/bin:~/.asdf/shims:$PATH

# CURL SSL DISABLE
RUN sudo update-ca-certificates --fresh
RUN echo "insecure" >> ${home}/.curlrc

# RUN POETRY_VERSION=$(cat .tool-versions|grep 'poetry' | cut -d " " -f 2) && export PATH=${home}/.asdf/installs/poetry/$POETRY_VERSION/bin:$PATH

RUN sudo chown -Rf vscode:vscode ${home}
RUN sudo chown -Rf vscode:vscode /workspace

WORKDIR /workspace

SHELL ["/bin/bash", "-c"]
RUN source ${home}/.asdf/asdf.sh && make install
RUN sudo rm -rf /workspace
