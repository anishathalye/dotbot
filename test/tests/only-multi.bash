test_description='--only with multiple arguments'
. '../test-lib.bash'

test_expect_success 'setup' '
ln -s ${DOTFILES}/nonexistent ~/bad && touch ${DOTFILES}/y
'

test_expect_success 'run' '
run_dotbot --only clean shell <<EOF
- clean: ["~"]
- shell:
  - echo "x" > ~/x
- link:
    ~/y: y
EOF
'

test_expect_success 'test' '
! test -f ~/bad && grep "x" ~/x && ! test -f ~/y
'
