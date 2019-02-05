test_description='clean expands environment variables'
. '../test-lib.bash'

test_expect_success 'setup' '
ln -s ${DOTFILES}/f ~/.f
'

test_expect_success 'run' '
run_dotbot <<EOF
- clean: ["\$HOME"]
EOF
'

test_expect_success 'test' '
! test -h ~/.f
'
