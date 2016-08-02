test_description='link expands environment variables in extended config syntax'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "grape" > ${DOTFILES}/h
'

test_expect_success 'run' '
export APPLE="h" &&
run_dotbot <<EOF
- link:
    ~/.i:
      path: \$APPLE
      relink: true
EOF
'

test_expect_success 'test' '
grep "grape" ~/.i
'
