test_description='link uses destination if source is null'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/f &&
echo "grape" > ${DOTFILES}/fd
'

test_expect_success 'run' '
run_dotbot <<EOF
- link:
    ~/f:
    ~/.f:
    ~/fd:
        force: false
    ~/.fd:
        force: false
EOF
'

test_expect_success 'test' '
grep "apple" ~/f &&
grep "apple" ~/.f &&
grep "grape" ~/fd &&
grep "grape" ~/.fd
'
