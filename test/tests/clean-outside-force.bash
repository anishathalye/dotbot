test_description='clean forced to remove files linking outside dotfiles directory'
. '../test-lib.bash'

test_expect_success 'setup' '
ln -s /nowhere ~/.g
'

test_expect_success 'run' '
run_dotbot <<EOF
- clean:
    ~/:
      force: true
EOF
'

test_expect_success 'test' '
! test -h ~/.g
'
