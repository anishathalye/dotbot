test_description='force leaves file when target nonexistent'
. '../test-lib.bash'

test_expect_success 'setup' '
mkdir ~/dir &&
touch ~/file
'

test_expect_failure 'run' '
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
test -d ~/dir &&
test -f ~/file
'
