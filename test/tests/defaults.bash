test_description='defaults setting works'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/f &&
echo "grape" > ~/f &&
ln -s ~/f ~/.f
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
