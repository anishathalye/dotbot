test_description='link glob ambiguous'
. '../test-lib.bash'

test_expect_success 'setup' '
mkdir ${DOTFILES}/bin
'

test_expect_failure 'run 1' '
run_dotbot <<EOF
- link:
    ~/bin/:
        path: bin
        glob: true
EOF
'

test_expect_failure 'test 1' '
test -d ~/bin
'

test_expect_failure 'run 2' '
run_dotbot <<EOF
- link:
    ~/bin/:
        path: bin/
        glob: true
EOF
'

test_expect_failure 'test 2' '
test -d ~/bin
'

test_expect_success 'run 3' '
run_dotbot <<EOF
- link:
    ~/bin:
        path: bin
        glob: true
EOF
'

test_expect_success 'test 3' '
test -d ~/bin
'
