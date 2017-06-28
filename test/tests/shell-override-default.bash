test_description='shell command can override default'
. '../test-lib.bash'

test_expect_success 'run' '
(run_dotbot | (! grep "^apple")) <<EOF
- defaults:
    shell:
      stdout: true
- shell:
  -
    command: echo apple
    stdout: false
EOF
'
