test_description='create folders'
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

test_expect_success 'run 2' '
run_dotbot <<EOF
- create:
    - ~/somedir
    - ~/nested/somedir
EOF
'
