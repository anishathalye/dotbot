test_description='link expands environment variables in source'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "grape" > ${DOTFILES}/h
'

test_expect_success 'run' '
export APPLE="h" &&
run_dotbot <<EOF
- link:
    ~/.i: \$APPLE
EOF
'

test_expect_success 'test' '
grep "grape" ~/.i
'
