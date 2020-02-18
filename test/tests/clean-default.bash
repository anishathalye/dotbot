test_description='clean uses default unless overridden'
. '../test-lib.bash'

test_expect_success 'setup' '
ln -s /nowhere ~/.g
'

test_expect_success 'run' '
run_dotbot <<EOF
- clean:
    ~/nonexistent:
      force: true
    ~/:
EOF
'

test_expect_success 'test' '
test -h ~/.g
'
