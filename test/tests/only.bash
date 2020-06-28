test_description='--only'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/x
'

test_expect_success 'run' '
run_dotbot --only shell <<EOF
- shell:
  - echo "pear" > ~/y
- link:
    ~/x: x
EOF
'

test_expect_success 'test' '
grep "pear" ~/y && ! test -f ~/x
'

test_expect_success 'run 2' '
run_dotbot --only link <<EOF
- shell:
  - echo "pear" > ~/z
- link:
    ~/x: x
'

test_expect_success 'test' '
grep "apple" ~/x && ! test -f ~/z
'
