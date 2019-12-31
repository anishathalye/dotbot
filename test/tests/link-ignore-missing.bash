test_description='link is created even if source is missing'
. '../test-lib.bash'

test_expect_failure 'run' '
run_dotbot <<EOF
- link:
    ~/missing_link:
        path: missing
EOF
'

test_expect_success 'run 2' '
run_dotbot <<EOF
- link:
    ~/missing_link:
        path: missing
        ignore-missing: true
EOF
'

test_expect_success 'test' '
test -L ~/missing_link
'
