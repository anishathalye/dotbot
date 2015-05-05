test_description='clean ignores files linking outside dotfiles directory'
. '../test-lib.bash'

test_expect_success 'setup' '
ln -s ${DOTFILES}/f ~/.f &&
ln -s ~/g ~/.g
'

test_expect_success 'run' '
run_dotbot <<EOF
- clean: ["~"]
EOF
'

test_expect_success 'test' '
! test -h ~/.f &&
test -h ~/.g
'
