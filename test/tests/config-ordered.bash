test_description='config loaded in order'
. '../test-lib.bash'

test_expect_success 'setup' '
mkdir ${DOTFILES}/a &&
mkdir ${DOTFILES}/b &&
mkdir ${DOTFILES}/c
echo "orange" > ${DOTFILES}/d
'

test_expect_success 'run' '
run_dotbot <<EOF
- link:
    ~/.a: a
    ~/.a/b: b
    ~/.a/b/c: c
    ~/.a/b/c/d: d
EOF
'

test_expect_success 'test' '
test -d ~/.a &&
test -d ~/.a/b &&
test -d ~/.a/b/c &&
grep "orange" ~/.a/b/c/d
'
