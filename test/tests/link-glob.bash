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
