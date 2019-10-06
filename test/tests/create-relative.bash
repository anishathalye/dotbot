test_description='relative creating works'
. '../test-lib.bash'

test_expect_success 'run' '
run_dotbot <<EOF
- create:
    - ~/somedir
    - ~/nested/somedir
EOF
'

test_expect_success 'test' '
[ -d ~/somedir ] &&
[ -d ~/nested/somedir ]
'
