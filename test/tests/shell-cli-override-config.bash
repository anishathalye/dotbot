test_description='cli options can override config file'
. '../test-lib.bash'

test_expect_success 'run 1' '
(run_dotbot -vv | (grep "^apple")) <<EOF
- shell:
  -
    command: echo apple
EOF
'

test_expect_success 'run 2' '
(run_dotbot -vv | (grep "^apple")) <<EOF
- shell:
  -
    command: echo apple
    stdout: false
EOF
'

test_expect_success 'run 3' '
(run_dotbot -vv | (grep "^apple")) <<EOF
- defaults:
    shell:
      stdout: false
- shell:
  - command: echo apple
EOF
'

# Control to make sure stderr redirection is working as expected
test_expect_failure 'run 4' '
(run_dotbot -vv | (grep "^apple")) <<EOF
- shell:
  - command: echo apple >&2
EOF
'

test_expect_success 'run 5' '
(run_dotbot -vv 2>&1 | (grep "^apple")) <<EOF
- shell:
  - command: echo apple >&2
EOF
'

test_expect_success 'run 6' '
(run_dotbot -vv 2>&1 | (grep "^apple")) <<EOF
- shell:
  -
    command: echo apple >&2
    stdout: false
EOF
'

test_expect_success 'run 7' '
(run_dotbot -vv 2>&1 | (grep "^apple")) <<EOF
- defaults:
    shell:
      stdout: false
- shell:
  - command: echo apple >&2
EOF
'

# Make sure that we must use verbose level 2
# This preserves backwards compatability
test_expect_failure 'run 8' '
(run_dotbot -v | (grep "^apple")) <<EOF
- shell:
  - command: echo apple
EOF
'

test_expect_failure 'run 9' '
(run_dotbot -v | (grep "^apple")) <<EOF
- shell:
  - command: echo apple >&2
EOF
'
