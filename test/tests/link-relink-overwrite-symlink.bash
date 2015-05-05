test_description='relink overwrites symlink'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/f &&
echo "grape" > ~/f &&
ln -s ~/f ~/.f
'

test_expect_success 'run' '
run_dotbot <<EOF
- link:
    ~/.f:
      path: f
      relink: true
EOF
'

test_expect_success 'test' '
grep "apple" ~/.f
'
