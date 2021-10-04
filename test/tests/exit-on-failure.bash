test_description='test exit on failure'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/f1 &&
echo "orange" > ${DOTFILES}/f2 &&
echo "pineapple" > ${DOTFILES}/f3
'

test_expect_failure 'run_case1' '
run_dotbot -x <<EOF
- shell:
    - "this_is_not_a_command"
- link:
    ~/f1:
EOF
'

test_expect_failure 'run_case2' '
run_dotbot -x <<EOF
- link:
    ~/f2:
- shell:
    - "this_is_not_a_command"
- link:
    ~/f3:
EOF
'

test_expect_success 'test' '
[[ ! -f ~/f1 ]] && [[ -f ~/f2 ]] && [[ ! -f ~/f3 ]]
'
