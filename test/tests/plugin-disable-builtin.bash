test_description='can disable built-in plugins'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/f
'

test_expect_failure 'run' '
run_dotbot --disable-built-in-plugins <<EOF
- link:
    ~/.f: f
EOF
'

test_expect_failure 'test' '
test -f ~/.f
'
