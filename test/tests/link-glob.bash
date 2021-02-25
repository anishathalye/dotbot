test_description='link glob'
. '../test-lib.bash'

test_expect_success 'setup 1' '
mkdir ${DOTFILES}/bin &&
echo "apple" > ${DOTFILES}/bin/a &&
echo "banana" > ${DOTFILES}/bin/b &&
echo "cherry" > ${DOTFILES}/bin/c
'

test_expect_success 'run 1' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/bin: bin/*
EOF
'

test_expect_success 'test 1' '
grep "apple" ~/bin/a &&
grep "banana" ~/bin/b &&
grep "cherry" ~/bin/c
'

test_expect_success 'setup 2' '
rm -rf ~/bin
'

test_expect_success 'run 2' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/bin/: bin/*
EOF
'

test_expect_success 'test 2' '
grep "apple" ~/bin/a &&
grep "banana" ~/bin/b &&
grep "cherry" ~/bin/c
'

test_expect_success 'setup 3' '
rm -rf ~/bin &&
echo "dot_apple" > ${DOTFILES}/bin/.a &&
echo "dot_banana" > ${DOTFILES}/bin/.b &&
echo "dot_cherry" > ${DOTFILES}/bin/.c
'

test_expect_success 'run 3' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/bin/: bin/.*
EOF
'

test_expect_success 'test 3' '
grep "dot_apple" ~/bin/.a &&
grep "dot_banana" ~/bin/.b &&
grep "dot_cherry" ~/bin/.c
'

test_expect_success 'setup 4' '
rm -rf ~/bin &&
echo "dot_apple" > ${DOTFILES}/.a &&
echo "dot_banana" > ${DOTFILES}/.b &&
echo "dot_cherry" > ${DOTFILES}/.c
'

test_expect_success 'run 4' '
run_dotbot -v <<EOF
- link:
    "~":
      path: .*
      glob: true
EOF
'

test_expect_success 'test 4' '
grep "dot_apple" ~/.a &&
grep "dot_banana" ~/.b &&
grep "dot_cherry" ~/.c
'
