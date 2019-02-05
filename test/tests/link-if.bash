test_description='link if'
. '../test-lib.bash'

test_expect_success 'setup' '
mkdir ~/d
echo "apple" > ${DOTFILES}/f
'

test_expect_success 'run' '
run_dotbot <<EOF
- link:
    ~/.f:
        path: f
        if: "true"
    ~/.g:
        path: f
        if: "false"
    ~/.h:
        path: f
        if: "[[ -d ~/d ]]"
    ~/.i:
        path: f
        if: "badcommand"
EOF
'

test_expect_success 'test' '
grep "apple" ~/.f &&
! test -f ~/.g &&
grep "apple" ~/.h &&
! test -f ~/.i
'

test_expect_success 'run 2' '
run_dotbot <<EOF
- defaults:
    link:
      if: "false"
- link:
    ~/.j:
        path: f
        if: "true"
    ~/.k:
        path: f
EOF
'

test_expect_success 'test 2' '
grep "apple" ~/.j &&
! test -f ~/.k
'
