test_description='link expands environment variables in target'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/f &&
echo "grape" > ${DOTFILES}/h
'

test_expect_success 'run' '
export ORANGE=".config" &&
export BANANA="g" &&
unset PEAR &&
run_dotbot <<EOF
- link:
    ~/\${ORANGE}/\$BANANA:
      path: f
      create: true
    ~/\$PEAR: h
EOF
'

test_expect_success 'test' '
grep "apple" ~/.config/g &&
grep "grape" ~/\$PEAR
'
