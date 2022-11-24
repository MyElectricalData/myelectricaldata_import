import __main__ as app
import os
import subprocess

from InquirerPy import inquirer, prompt
from InquirerPy.base import Choice
from packaging.version import parse as parse_version

docker_compose = "docker-compose -f dev/docker-compose.dev.yaml"


def cmd(cmd, path="./"):
    return subprocess.run(
        cmd.split(),
        env=dict(os.environ, DISPLAY=":0", BROWSER="wslview"),
        cwd=path,
        stdout=subprocess.PIPE,
    )


def wizard():
    app.LOG.title("Wizard Mode")
    skip = ["help"]
    with open("Makefile", "r") as makefile:
        targets = {}
        target_found = False
        doc = ""
        for line in makefile.read().splitlines():
            if target_found:
                name = line.split(":")[0]
                if name not in skip and "_%" not in name:
                    targets[name] = {}
                    if ":" in doc:
                        targets[name]["doc"] = doc.split(" : ")[0]
                        targets[name]["infos"] = doc.split(" : ")[1]
                    else:
                        targets[name]["doc"] = doc
                target_found = False
            elif line.startswith("## "):
                target_found = True
                doc = line.replace("## ", "")
    choices = [Choice("exit", "Exit")]
    for target, data in sorted(targets.items()):
        choices.append(Choice(value=f"{target}", name=f"{target} - {data['doc']}"))
    questions = [
        {
            "type": "fuzzy",
            "message": "Chart version:",
            "choices": choices,
        }
    ]
    target = prompt(questions=questions)[0]
    if target != "exit":
        os.system(f"make {target}")
    else:
        app.LOG.error("Good bye!!")


def run(dev=False, debug=False):
    if debug:
        app.LOG.title(["Boot DynAPI in debug mode", "CTRL + C to exit"])
    else:
        app.LOG.title(["Boot DynAPI", "CTRL + C to exit"])
    mode_debug = ""
    mode_dev = ""
    if debug:
        mode_debug = "-e DEBUG=true"
    if dev:
        mode_dev = "-e DEV=true"
    command = (
        f"{docker_compose} run -p 5000:5000"
        f"{mode_debug} {mode_dev} myelectricaldata_import"
    )
    app.LOG.log(command)
    os.system(command)


def create_release(prerelease=False):
    rebuild_confirm = False

    commit = cmd("git status --porcelain").stdout.decode()
    if commit != "":
        app.LOG.warning("Your code it's not commit!!")
        commit_msg = inquirer.text(message="Commit message").execute()
        os.system("git add --all")
        os.system(f"git commit -m \"{commit_msg}\"")

    app.LOG.title("Get remote tag")
    remote_tag = cmd(f"git ls-remote --tags origin").stdout.decode()
    tags = []
    app.LOG.log("")
    app.LOG.log("Release available on Github")
    for tag in remote_tag.splitlines():
        _release = tag.split()[1].split("/")[2]
        app.LOG.log(f" - {_release}")
        tags.append(_release)
    app.LOG.log("")

    app.LOG.title("Choose your release version :")
    last_version_check = "0.0.0"
    last_version = "0.0.0"
    for version in tags:
        if parse_version(version) > parse_version(last_version_check):
            last_version = version
        last_version_check = version

    # GENERATE NEW RELEASE VERSION
    new_release = last_version.split("-")[0]
    new_version = []
    for idx, digit in enumerate(new_release.split(".")):
        if idx > 0:
            idx = int(idx) * 2
        version = new_release[:idx] + str(int(digit) + 1) + new_release[idx + 1:]
        for idxx, digitt in enumerate(version.split(".")):
            if idxx > 0:
                idxx = int(idxx) * 2
            if idxx > idx:
                version = version[:idxx] + str(0) + version[idxx + 1:]
        last_version = Choice(version, f"NEW : {version}")
        new_version.append(last_version)

    version = inquirer.fuzzy(
        message="Select tag:",
        choices=[*[Choice("custom", "Custom release version")], *new_version, *tags],
    ).execute()

    if version == "custom":
        version = inquirer.text(
            message="Which release would you create ?",
        ).execute()

    if version not in tags:
        prerelease = inquirer.confirm(
            message="It's prerelease ? (deploy in sandbox)",
        ).execute()
        if prerelease:
            version = f"{version}-dev"
        else:
            version = f"{version}-release"

    if version in tags:
        app.LOG.warning("Tag already exist on Github")
        rebuild_confirm = inquirer.confirm(
            message="Would you rebuild this ?",
        ).execute()
        if not rebuild_confirm:
            app.LOG.title_error("No problem!")
            return False

    if rebuild_confirm:
        app.LOG.log(f"Delete release {version} on remote")
        os.system(f"gh release delete {version} -y")
        app.LOG.log(f"Delete tag {version} in local")
        os.system(f"git tag -d {version}")
        app.LOG.log("  => Success")
        app.LOG.log(f"Delete tag {version} on remote")
        print(f"git push --delete origin {version}")
        os.system(f"git push --delete origin {version}")
        app.LOG.log("  => Success")

    app.LOG.log(f"Create {version} in local")
    os.system(f"git tag {version}")
    app.LOG.log("  => Success")
    app.LOG.title(f"Push tag {version}")
    os.system(f"git push origin {version}")
    app.LOG.log("  => Success")
    app.LOG.title(f"Create release {version}")
    prerelease_txt = ""
    if version.endswith("-dev"):
        prerelease_txt = "--prerelease"
    os.system(f"gh release create -t {version} --generate-notes {prerelease_txt} {version}")
    app.LOG.log("  => Success")

    app.LOG.log(f"Release {version} is online!!!!")
