DOTBOT_EXEC="${BASEDIR}/bin/dotbot"
DOTFILES="${HOME}/dotfiles"
INSTALL_CONF='install.conf.yaml'
INSTALL_CONF_JSON='install.conf.json'

test_run_() {
    if ! ${DEBUG}; then
        (eval "$*") >/dev/null 2>&1
    else
        (eval "$*")
    fi
}

test_expect_success() {
    local tag=${1} && shift
    if ! test_run_ "$@"; then
        >&2 echo "- ${tag} failed."
        exit 1
    fi
}

test_expect_failure() {
    local tag=${1} && shift
    if test_run_ "$@"; then
        >&2 echo "- ${tag} failed."
        exit 1
    fi
}

skip_tests() {
  # exit with special exit code picked up by driver-lib.bash
  exit 42
}

check_env() {
    if [ "${DOTBOT_TEST}" != "true" ]; then
        >&2 echo "test must be run by test driver"
        exit 1
    fi
}

# run comparison check on python version; args:
#   $1 - comparison operator (e.g. '>=')
#   $2 - version number, to be passed to python (e.g. '3', '3.5', '3.6.4')
# status code will reflect if comparison is true/false
# e.g. `check_python_version '>=' 3.5`
check_python_version() {
    check="$1"
    version="$(echo "$2" | tr . , )"
    # this call to just `python` will work in the Vagrant-based testing VM
    # because `pyenv` will always create a link to the "right" version.
    python -c "import sys; exit( not (sys.version_info ${check} (${version})) )"
}

initialize() {
    check_env
    echo "${test_description}"
    mkdir -p "${DOTFILES}"
    cd
}

run_dotbot() {
    (
        cat > "${DOTFILES}/${INSTALL_CONF}"
        ${DOTBOT_EXEC} -c "${DOTFILES}/${INSTALL_CONF}" "${@}"
    )
}

run_dotbot_json() {
    (
        cat > "${DOTFILES}/${INSTALL_CONF_JSON}"
        ${DOTBOT_EXEC} -c "${DOTFILES}/${INSTALL_CONF_JSON}" "${@}"
    )
}

initialize
