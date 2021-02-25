test_description='--only does not skip defaults'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/x
'

test_expect_success 'run' '
run_dotbot --only link <<EOF
- defaults:
    link:
      create: true
- shell:
  - echo "pear" > ~/z
- link:
    ~/d/x: x
EOF
'

test_expect_success 'test' '
grep "apple" ~/d/x && ! test -f ~/z
'
