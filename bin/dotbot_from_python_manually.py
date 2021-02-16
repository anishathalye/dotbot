ARGS_TO_SCRIPT = (
    "python  >/dev/null /c/Users/Matt/dotfiles/dotbot/bin/dotbot -d /c/Users/Matt/dotfiles -c install.conf.yaml"
)
# These arguments are only linux/ bash safe


"""Script port from  /c/Users/Matt/dotfiles/dotbot/bin/dotbot"""
import sys, os

DOTFILE_DIR = os.path.normpath(os.path.expandvars("%USERPROFILE%/dotfiles/"))

DIRECTORY_ARG = os.path.normpath(DOTFILE_DIR)
CONFIG_FILE_ARG = "install.conf.yaml"

sys.path.append(DOTFILE_DIR)
print(DOTFILE_DIR)
os.chdir(DOTFILE_DIR)

# PROJECT_ROOT_DIRECTORY = os.path.dirname(
#     os.path.dirname(os.path.realpath(__file__)))
# print(PROJECT_ROOT_DIRECTORY)
PROJECT_ROOT_DIRECTORY = DOTFILE_DIR


def inject(lib_path):
    path = os.path.join(PROJECT_ROOT_DIRECTORY, "lib", lib_path)
    sys.path.insert(0, path)


# version dependent libraries
if sys.version_info[0] >= 3:
    inject("pyyaml/lib3")
else:
    inject("pyyaml/lib")

if os.path.exists(os.path.join(PROJECT_ROOT_DIRECTORY, "dotbot")):
    if PROJECT_ROOT_DIRECTORY not in sys.path:
        sys.path.insert(0, PROJECT_ROOT_DIRECTORY)
        os.putenv("PYTHONPATH", PROJECT_ROOT_DIRECTORY)

import dotbot


def main():
    dotbot.cli.main(additional_args=["-d", DIRECTORY_ARG, "-c", CONFIG_FILE_ARG])


if __name__ == "__main__":
    main()
