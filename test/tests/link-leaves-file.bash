test_description='relink does not overwrite file'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/f &&
echo "grape" > ~/.f
'

test_expect_failure 'run' '
run_dotbot <<EOF
- link:
    ~/.f: f
EOF
'

test_expect_success 'test' '
grep "grape" ~/.f
'
