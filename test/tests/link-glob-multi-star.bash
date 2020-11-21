test_description='link glob multi star'
. '../test-lib.bash'

test_expect_success 'setup' '
mkdir ${DOTFILES}/config &&
mkdir ${DOTFILES}/config/foo &&
mkdir ${DOTFILES}/config/bar &&
echo "apple" > ${DOTFILES}/config/foo/a &&
echo "banana" > ${DOTFILES}/config/bar/b &&
echo "cherry" > ${DOTFILES}/config/bar/c
'

test_expect_success 'run' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/.config/: config/*/*
EOF
'

test_expect_success 'test' '
! readlink ~/.config/ &&
! readlink ~/.config/foo &&
readlink ~/.config/foo/a &&
grep "apple" ~/.config/foo/a &&
grep "banana" ~/.config/bar/b &&
grep "cherry" ~/.config/bar/c
'
