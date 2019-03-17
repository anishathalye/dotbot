test_description='link creates target and links file when target nonexistent'
. '../test-lib.bash'

test_expect_success 'setup' '
mkdir ~/dir &&
touch ~/file
'

test_expect_success 'run' '
run_dotbot <<EOF
- link:
    ~/dir:
      path: dir
      force: true
    ~/file:
      path: file
      force: true
EOF
'

test_expect_success 'test' '
test -L ~/dir &&
test -L ~/file &&
test -d ${DOTFILES}/dir &&
test -f ${DOTFILES}/file
'
