test_description='relink relative does not incorrectly relink file'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/f &&
echo "grape" > ~/.f
'

test_expect_success 'run' '
run_dotbot <<EOF
- link:
    ~/.folder/f:
      path: f
      create: true
      relative: true
EOF
'

# these are done in a single block because they run in a subshell, and it
# wouldn't be possible to access `$mtime` outside of the subshell
test_expect_success 'test' '
mtime=$(stat ~/.folder/f | grep Modify)
run_dotbot <<EOF
- link:
    ~/.folder/f:
      path: f
      create: true
      relative: true
      relink: true
EOF
[[ "$mtime" == "$(stat ~/.folder/f | grep Modify)" ]]
'
