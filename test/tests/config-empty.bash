test_description='empty config allowed'
. '../test-lib.bash'

test_expect_success 'run' '
run_dotbot <<EOF
EOF
'
