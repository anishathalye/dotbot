test_description='clean ignores nonexistent directories'
. '../test-lib.bash'

test_expect_success 'run' '
run_dotbot <<EOF
- clean: ["~", "~/fake"]
EOF
'
