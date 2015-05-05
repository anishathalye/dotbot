DEBUG=false
DOTFILES='/home/vagrant/dotfiles'
INSTALL_CONF='install.conf.yaml'

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
    check_vm
    echo "${test_description}"
    mkdir -p "${DOTFILES}"
    cd
}

run_dotbot() {
    (
        cd "${DOTFILES}"
        cat > "${INSTALL_CONF}"
        /dotbot/bin/dotbot -d . -c "${INSTALL_CONF}" "${@}"
    )
}

initialize
