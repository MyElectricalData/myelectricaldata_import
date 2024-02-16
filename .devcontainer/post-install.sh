#!/bin/bash
echo "Install ASDF"
git clone https://github.com/asdf-vm/asdf.git ~/.asdf
echo '. "$HOME/.asdf/asdf.sh"'  >> ~/.bashrc
echo '. "$HOME/.asdf/asdf.sh"'  >> ~/.zshrc
echo '. "$HOME/.asdf/completions/asdf.bash"'  >> ~/.bashrc
echo '. "$HOME/.asdf/completions/asdf.bash"'  >> ~/.zshrc
echo ""
echo "Source bashrc"
export PATH=~/.asdf/bin:~/.asdf/shims:$PATH
POETRY_VERSION=$(cat .tool-versions|grep 'poetry' | cut -d " " -f 2)
export PATH=~/.asdf/installs/poetry/$POETRY_VERSION/bin:$PATH
echo ""
echo "Disable SSL check in Curl (DKT Fix)"
echo "insecure" >> ${HOME}/.curlrc
# echo ""
# echo "Update SSL certificates"
# update-ca-certificates
echo ""
echo "Install environment"
make install

eval "$(ssh-agent -s)"
cat >> ~/.bashrc <<- EOM
if [ -z "\$SSH_AUTH_SOCK" ]; then
   # Check for a currently running instance of the agent
   RUNNING_AGENT="`ps -ax | grep 'ssh-agent -s' | grep -v grep | wc -l | tr -d '[:space:]'`"
   if [ "\$RUNNING_AGENT" = "0" ]; then
        # Launch a new instance of the agent
        ssh-agent -s &> \$HOME/.ssh/ssh-agent
   fi
   eval `cat \$HOME/.ssh/ssh-agent`
fi
EOM