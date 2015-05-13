test_description='link leaves unset environment variables'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/\$ORANGE
'

test_expect_success 'run' '
unset ORANGE &&
run_dotbot <<EOF
- link:
    ~/.f: \$ORANGE
EOF
'

test_expect_success 'test' '
grep "apple" ~/.f
'
