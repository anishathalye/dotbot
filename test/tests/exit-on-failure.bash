test_description='test exit on failure'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/f
'

test_expect_failure 'run' '
run_dotbot -x <<EOF
- shell:
    - "this_is_not_a_command"
- link:
    ~/f:
EOF
'

test_expect_success 'test' '
[[ ! -f ~/f ]]
'
