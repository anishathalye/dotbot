test_description='shell command stdout works'
. '../test-lib.bash'

test_expect_success 'run' '
(run_dotbot | grep "^apple") <<EOF
- shell:
  -
    command: echo apple
    stdout: true
EOF
'
