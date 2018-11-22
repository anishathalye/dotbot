test_description='shell command can be suppressed in output'
. '../test-lib.bash'

# when not quiet, expect to see command that was run
test_expect_success 'run' '
(run_dotbot | grep "echo banana") <<EOF
- shell:
  - command: echo banana
    description: echoing a thing...
EOF
'

# when quiet, expect command to be suppressed
test_expect_success 'run 2' '
(run_dotbot | (! grep "echo banana")) <<EOF
- shell:
  - command: echo banana
    description: echoing a thing...
    quiet: true
EOF
'

# when no description, expect to see command
test_expect_success 'run 3' '
(run_dotbot | grep "echo banana") <<EOF
- shell:
  - command: echo banana
    quiet: true
EOF
'
