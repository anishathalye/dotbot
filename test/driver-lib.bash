MAXRETRY=5
TIMEOUT=1

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


check_prereqs() {
    if ! (vagrant ssh -c 'exit') >/dev/null 2>&1; then
        >&2 echo "vagrant vm must be running."
        return 1
    fi
    if ! (vagrant plugin list | grep '^sahara\s\+') >/dev/null 2>&1; then
        >&2 echo "vagrant plugin 'sahara' is not installed."
        return 1
    fi
}

until_success() {
    local timeout=${TIMEOUT}
    local attempt=0
    while [ $attempt -lt $MAXRETRY ]; do
        if ($@) >/dev/null 2>&1; then
            return 0
        fi
        sleep $timeout
        timeout=$((timeout * 2))
        attempt=$((attempt + 1))
    done

    return 1
}

wait_for_vagrant() {
    until_success vagrant ssh -c 'exit'
}

rollback() {
    vagrant sandbox rollback >/dev/null 2>&1 &&
        wait_for_vagrant &&
        vagrant rsync >/dev/null 2>&1
}

initialize() {
    echo "initializing."
    vagrant sandbox on >/dev/null 2>&1
    if ! vagrant ssh -c "pyenv local ${2}" >/dev/null 2>&1; then
        wait_for_vagrant && vagrant sandbox rollback >/dev/null 2>&1
        wait_for_vagrant
        if ! vagrant ssh -c "pyenv install -s ${2} && pyenv local ${2}" >/dev/null 2>&1; then
            die "could not install python ${2}"
        fi
        vagrant sandbox commit >/dev/null 2>&1
    fi
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
    rollback || die "unable to rollback vm." # start with a clean slate
    vagrant ssh -c "pyenv local ${2}" >/dev/null 2>&1
    if vagrant ssh -c "cd /dotbot/test/tests && bash ${1}" 2>/dev/null; then
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
