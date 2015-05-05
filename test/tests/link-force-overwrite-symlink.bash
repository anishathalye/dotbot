test_description='force overwrites symlinked directory'
. '../test-lib.bash'

test_expect_success 'setup' '
mkdir ${DOTFILES}/dir ~/dir &&
touch ${DOTFILES}/dir/f &&
ln -s ~/ ~/.dir
'

test_expect_success 'run' '
run_dotbot <<EOF
- link:
    ~/.dir:
      path: dir
      force: true
EOF
'

test_expect_success 'test' '
test -f ~/.dir/f
'
