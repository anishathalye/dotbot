test_description='link glob recursive'
. '../test-lib.bash'

check_python_version ">=" 3.5 \
  || test_expect_failure 'expect-fail' '
run_dotbot -v <<EOF
- link:
    ~/.config/:
      glob: true
      path: bogus/**
EOF
'

# Skip remaining tests if not supported
check_python_version ">=" 3.5 \
  || skip_tests

test_expect_success 'setup' '
mkdir -p ${DOTFILES}/config/foo/bar &&
echo "apple" > ${DOTFILES}/config/foo/bar/a &&
echo "banana" > ${DOTFILES}/config/foo/bar/b &&
echo "cherry" > ${DOTFILES}/config/foo/bar/c
'

test_expect_success 'run' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/.config/:
      path: config/**
      exclude: [config/**/b]
EOF
'

test_expect_success 'test' '
! readlink ~/.config/ &&
! readlink ~/.config/foo &&
! readlink ~/.config/foo/bar &&
readlink ~/.config/foo/bar/a &&
grep "apple" ~/.config/foo/bar/a &&
test \! -e ~/.config/foo/bar/b &&
grep "cherry" ~/.config/foo/bar/c
'
