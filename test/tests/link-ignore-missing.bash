test_description='link is created even if source is missing'
. '../test-lib.bash'

test_expect_success 'run' '
run_dotbot <<EOF
- link:
    missing_link:
        source: missing
        ignore-missing: true
EOF
'
test_expect_success 'test' '
test -L missing_link
'
