test_description='link expands user in target'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ~/f
'

test_expect_success 'run' '
run_dotbot <<EOF
- link:
    ~/g: ~/f
EOF
'

test_expect_success 'test' '
grep "apple" ~/g
'
