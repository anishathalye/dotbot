test_description='link glob ambiguous'
. '../test-lib.bash'

test_expect_success 'setup' '
mkdir ${DOTFILES}/foo
'

test_expect_failure 'run 1' '
run_dotbot <<EOF
- link:
    ~/foo/:
        path: foo
        glob: true
EOF
'

test_expect_failure 'test 1' '
test -d ~/foo
'

test_expect_failure 'run 2' '
run_dotbot <<EOF
- link:
    ~/foo/:
        path: foo/
        glob: true
EOF
'

test_expect_failure 'test 2' '
test -d ~/foo
'

test_expect_success 'run 3' '
run_dotbot <<EOF
- link:
    ~/foo:
        path: foo
        glob: true
EOF
'

test_expect_success 'test 3' '
test -d ~/foo
'
