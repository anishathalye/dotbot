test_description='link glob exclude'
. '../test-lib.bash'

test_expect_success 'setup 1' '
mkdir -p ${DOTFILES}/config/{foo,bar,baz} &&
echo "apple" > ${DOTFILES}/config/foo/a &&
echo "banana" > ${DOTFILES}/config/bar/b &&
echo "cherry" > ${DOTFILES}/config/bar/c &&
echo "donut" > ${DOTFILES}/config/baz/d
'

test_expect_success 'run 1' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/.config/:
      path: config/*
      exclude: [config/baz]
EOF
'

test_expect_success 'test 1' '
! readlink ~/.config/ &&
readlink ~/.config/foo &&
! readlink ~/.config/baz &&
grep "apple" ~/.config/foo/a &&
grep "banana" ~/.config/bar/b &&
grep "cherry" ~/.config/bar/c
'

test_expect_success 'setup 2' '
rm -rf ~/.config &&
mkdir ${DOTFILES}/config/baz/buzz &&
echo "egg" > ${DOTFILES}/config/baz/buzz/e
'

test_expect_success 'run 2' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/.config/:
      path: config/*/*
      exclude: [config/baz/*]
EOF
'

test_expect_success 'test 2' '
! readlink ~/.config/ &&
! readlink ~/.config/foo &&
[ ! -d ~/.config/baz ] &&
readlink ~/.config/foo/a &&
grep "apple" ~/.config/foo/a &&
grep "banana" ~/.config/bar/b &&
grep "cherry" ~/.config/bar/c
'

test_expect_success 'setup 3' '
rm -rf ~/.config &&
mkdir ${DOTFILES}/config/baz/bizz &&
echo "grape" > ${DOTFILES}/config/baz/bizz/g
'

test_expect_success 'run 3' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/.config/:
      path: config/*/*
      exclude: [config/baz/buzz]
EOF
'

test_expect_success 'test 3' '
! readlink ~/.config/ &&
! readlink ~/.config/foo &&
readlink ~/.config/foo/a &&
! readlink ~/.config/baz/buzz &&
readlink ~/.config/baz/bizz &&
grep "apple" ~/.config/foo/a &&
grep "banana" ~/.config/bar/b &&
grep "cherry" ~/.config/bar/c &&
grep "donut" ~/.config/baz/d &&
grep "grape" ~/.config/baz/bizz/g
'

test_expect_success 'setup 4' '
rm -rf ~/.config &&
mkdir ${DOTFILES}/config/fiz &&
echo "fig" > ${DOTFILES}/config/fiz/f
'

test_expect_success 'run 4' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/.config/:
      path: config/*/*
      exclude: [config/baz/*, config/fiz/*]
EOF
'

test_expect_success 'test 4' '
! readlink ~/.config/ &&
! readlink ~/.config/foo &&
[ ! -d ~/.config/baz ] &&
[ ! -d ~/.config/fiz ] &&
readlink ~/.config/foo/a &&
grep "apple" ~/.config/foo/a &&
grep "banana" ~/.config/bar/b &&
grep "cherry" ~/.config/bar/c
'