DEBUG=${DEBUG:-false}
DOTBOT_EXEC="${BASEDIR}/bin/dotbot"
DOTFILES="/home/$(whoami)/dotfiles"
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

check_env() {
    if [ "${DOTBOT_TEST}" != "true" ]; then
        >&2 echo "test must be run by test driver"
        exit 1
    fi
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
