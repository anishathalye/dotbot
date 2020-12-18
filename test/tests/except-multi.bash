test_description='--except with multiple arguments'
. '../test-lib.bash'

test_expect_success 'setup' '
ln -s ${DOTFILES}/nonexistent ~/bad && touch ${DOTFILES}/y
'

test_expect_success 'run' '
run_dotbot --except clean shell <<EOF
- clean: ["~"]
- shell:
  - echo "x" > ~/x
- link:
    ~/y: y
EOF
'

test_expect_success 'test' '
[ "$(readlink ~/bad | cut -d/ -f5-)" = "dotfiles/nonexistent" ] &&
    ! test -f ~/x && test -f ~/y
'
