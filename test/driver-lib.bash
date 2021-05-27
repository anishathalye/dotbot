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
    if [[ "$(whoami)" != "vagrant" && "${CI}" != true ]]; then
        die "tests must be run inside Vagrant or CI"
    fi
}

cleanup() {
    rm -rf ~/fakehome
    mkdir -p ~/fakehome
}

initialize() {
    echo "initializing."
    tests_run=0
    tests_passed=0
    tests_failed=0
    tests_skipped=0
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
    red "-> fail!"
    echo
}

skip() {
    tests_skipped=$((tests_skipped + 1))
    yellow "-> skipped."
    echo
}

run_test() {
    tests_run=$((tests_run + 1))
    printf '[%d/%d] (%s)\n' "${tests_run}" "${tests_total}" "${1}"
    cleanup
    if (cd "${BASEDIR}/test/tests" && HOME=~/fakehome DEBUG=${2} DOTBOT_TEST=true bash "${1}"); then
        pass
    elif [ $? -eq 42 ]; then
        skip
    else
        fail
    fi
}

report() {
    printf -- "test report\n"
    printf -- "-----------\n"
    printf -- "- %3d run\n" ${tests_run}
    printf -- "- %3d passed\n" ${tests_passed}
    printf -- "- %3d skipped\n" ${tests_skipped}
    printf -- "- %3d failed\n" ${tests_failed}
    if [ ${tests_failed} -gt 0 ]; then
        red "==> FAIL! "
        return 1
    else
        green "==> PASS. "
        return 0
    fi
}

die() {
    >&2 echo $@
    >&2 echo "terminating..."
    exit 1
}
