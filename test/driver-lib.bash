red() {
    if [ -t 1 ]; then
        printf "\033[31m%s\033[0m\n" "$*"
    else
        printf "%s\n" "$*"
    fi
}

green() {
    if [ -t 1 ]; then
        printf "\033[32m%s\033[0m\n" "$*"
    else
        printf "%s\n" "$*"
    fi
}

yellow() {
    if [ -t 1 ]; then
        printf "\033[33m%s\033[0m\n" "$*"
    else
        printf "%s\n" "$*"
    fi
}


check_env() {
    if [[ "$(whoami)" != "vagrant" && ( "${TRAVIS}" != true || "${CI}" != true ) ]]; then
        die "tests must be run inside Travis or Vagrant"
    fi
}

cleanup() {
    (
    if [ "$(whoami)" == "vagrant" ]; then
        cd $HOME
        find . -not \( \
            -path './.pyenv' -o \
            -path './.pyenv/*' -o \
            -path './.bashrc' -o \
            -path './.profile' -o \
            -path './.ssh' -o \
            -path './.ssh/*' \
            \) -delete >/dev/null 2>&1
    else
        find ~ -mindepth 1 -newermt "${date_stamp}" \
            -not \( -path ~ -o -path "${BASEDIR}/*" \
                -o -path ~/dotfiles \) \
            -exec rm -rf {} +
    fi
    ) || true
}

initialize() {
    echo "initializing."
    tests_run=0
    tests_passed=0
    tests_failed=0
    tests_total="${1}"
    local plural="" && [ "${tests_total}" -gt 1 ] && plural="s"
    printf -- "running %d test%s...\n\n" "${tests_total}" "${plural}"
}

pass() {
    tests_passed=$((tests_passed + 1))
    green "-> ok."
    echo
}

fail() {
    tests_failed=$((tests_failed + 1))
    yellow "-> fail!"
    echo
}

run_test() {
    tests_run=$((tests_run + 1))
    printf '[%d/%d] (%s)\n' "${tests_run}" "${tests_total}" "${1}"
    cleanup
    if (cd "${BASEDIR}/test/tests" && DOTBOT_TEST=true bash "${1}"); then
        pass
    else
        fail
    fi
}

report() {
    printf -- "test report\n"
    printf -- "-----------\n"
    printf -- "- %3d run\n" ${tests_run}
    printf -- "- %3d passed\n" ${tests_passed}
    if [ ${tests_failed} -gt 0 ]; then
        printf -- "- %3d failed\n" ${tests_failed}
        echo
        red "==> not ok!"
        return 1
    else
        echo
        green "==> all ok."
        return 0
    fi
}

die() {
    >&2 echo $@
    >&2 echo "terminating..."
    exit 1
}
