test_description='shell command stdout disabled by default'
. '../test-lib.bash'

test_expect_success 'run' '
(run_dotbot | (! grep "^banana")) <<EOF
- shell:
  - echo banana
EOF
'
