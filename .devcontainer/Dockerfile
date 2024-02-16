# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT=3-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

# Install docker
RUN apt-get update \
    && apt-get install -y apt-transport-https ca-certificates curl gnupg2 lsb-release \
    && curl -fsSL https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]')/gpg | apt-key add - 2>/dev/null \
    && echo "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce-cli git

# make the LOCAL variable and install it
ARG LOCAL=fr_FR.UTF-8
RUN apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
    && localedef -i $(echo ${LOCAL} | cut -d "." -f1) -c -f $(echo ${LOCAL} | cut -d "." -f2) -A /usr/share/locale/locale.alias ${LOCAL}
ENV LANG ${LOCAL}

# # Install ASDF
# RUN git clone https://github.com/asdf-vm/asdf.git ~/.asdf
# RUN echo '. "$HOME/.asdf/asdf.sh"'  >> ~/.bashrc
# RUN echo '. "$HOME/.asdf/completions/asdf.bash"'  >> ~/.bashrc

# COPY ./ .

# SHELL ["/bin/bash", "-lc"]
# RUN make install

WORKDIR /workspace
RUN ln -s /workspace/app /app
RUN ln -s /workspace/data /data

RUN docker context use default
RUN docker buildx use default