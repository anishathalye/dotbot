DEBUG=${DEBUG:-false}
USE_VAGRANT=${USE_VAGRANT:-true}
DOTBOT_EXEC=${DOTBOT_EXEC:-"/dotbot/bin/dotbot"}
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

check_vm() {
    if [ "$(whoami)" != "vagrant" ]; then
        >&2 echo "test can't run outside vm!"
        exit 1
    fi
}

initialize() {
    if ${USE_VAGRANT}; then
        check_vm
    fi
    echo "${test_description}"
    mkdir -p "${DOTFILES}"
    cd
}

run_dotbot() {
    (
        cd "${DOTFILES}"
        cat > "${INSTALL_CONF}"
        ${DOTBOT_EXEC} -d . -c "${INSTALL_CONF}" "${@}"
    )
}

run_dotbot_json() {
    (
        cd "${DOTFILES}"
        cat > "${INSTALL_CONF_JSON}"
        ${DOTBOT_EXEC} -d . -c "${INSTALL_CONF_JSON}" "${@}"
    )
}

initialize
