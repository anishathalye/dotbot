test_description='defaults setting works'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/f &&
echo "grape" > ~/f &&
ln -s ~/f ~/.f &&
ln -s /nowhere ~/.g
'

test_expect_failure 'run-fail' '
run_dotbot <<EOF
- link:
    ~/.f: f
EOF
'

test_expect_failure 'test-fail' '
grep "apple" ~/.f
'

test_expect_success 'run' '
run_dotbot <<EOF
- defaults:
    link:
      relink: true

- link:
    ~/.f: f
EOF
'

test_expect_success 'test' '
grep "apple" ~/.f
'

test_expect_success 'run-fail 2' '
run_dotbot <<EOF
- clean: ["~"]
EOF
'

test_expect_failure 'test-fail 2' '
! test -h ~/.g
'

test_expect_success 'run 2' '
run_dotbot <<EOF
- defaults:
    clean:
      force: true

- clean: ["~"]
EOF
'

test_expect_success 'test 2' '
! test -h ~/.g
'
