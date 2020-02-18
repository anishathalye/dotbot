test_description='clean removes recursively'
. '../test-lib.bash'

test_expect_success 'setup' '
mkdir -p ~/a/b
ln -s /nowhere ~/c
ln -s /nowhere ~/a/d
ln -s /nowhere ~/a/b/e
'

test_expect_success 'run' '
run_dotbot <<EOF
- clean:
    ~/:
      force: true
EOF
'

test_expect_success 'test' '
! test -h ~/c && test -h ~/a/d && test -h ~/a/b/e
'

test_expect_success 'run 2' '
run_dotbot <<EOF
- clean:
    ~/:
      force: true
      recursive: true
EOF
'

test_expect_success 'test 2' '
! test -h ~/a/d && ! test -h ~/a/b/e
'
