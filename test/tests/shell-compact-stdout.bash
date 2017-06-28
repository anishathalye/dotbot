test_description='shell command stdout works in compact form'
. '../test-lib.bash'

test_expect_success 'run' '
(run_dotbot | grep "^apple") <<EOF
- defaults:
    shell:
      stdout: true
- shell:
  - echo apple
EOF
'

test_expect_success 'run 2' '
(run_dotbot | grep "^apple") <<EOF
- defaults:
    shell:
      stdout: true
- shell:
  - [echo apple, "echoing message"]
EOF
'
