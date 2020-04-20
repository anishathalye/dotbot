test_description='Test copy with force option'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/apple
echo "banana" > ~/apple
mkdir -p ${DOTFILES}/fruits/box/
mkdir -p ~/fruits/box/
echo "orange" > ~/fruits/box/lemon
echo "guava" > ~/fruits/box/guava
echo "cherry" > ${DOTFILES}/fruits/box/cherry
echo "lemon" > ${DOTFILES}/fruits/box/lemon
'

# test single file

## destination file already exists, do not overwrite it
test_expect_success 'do not overwrite existing file' '
run_dotbot <<EOF
- copy:
    ~/apple:
EOF
'
test_expect_success 'content test(not overwrite file)' '
grep "banana" ~/apple
'

## destination file already exists, but it is not skippable
test_expect_failure 'should fail because not skippable' '
run_dotbot <<EOF
- copy:
    ~/apple:
      skippable: false
EOF
'
test_expect_success 'content test(file not skippable)' '
grep "banana" ~/apple
'

## destination file already exists, use option 'force' to overwrite it
test_expect_success 'copy file with force option' '
run_dotbot <<eof
- copy:
    ~/apple:
      force: true
eof
'
test_expect_success 'content test(force copy file)' '
grep "apple" ~/apple
'

# test single directory

## destination directory already exists, do not overwrite it
test_expect_success 'do not overwrite existing directory' '
run_dotbot <<EOF
- copy:
    ~/fruits:
EOF
'
test_expect_success 'content test(not overwrite directory)' '
grep "orange" ~/fruits/box/lemon &&
grep "guava" ~/fruits/box/guava
'

## destination directory already exists, but it is not skippable
test_expect_failure 'do not overwrite existing directory' '
run_dotbot <<EOF
- copy:
    ~/fruits:
      skippable: false
EOF
'
test_expect_success 'content test(directory not skippable)' '
grep "orange" ~/fruits/box/lemon &&
grep "guava" ~/fruits/box/guava
'

## destination directory already exists, use option 'force' to overwrite it
test_expect_success 'copy directory with force option' '
run_dotbot <<eof
- copy:
    ~/fruits:
      force: true
eof
'
test_expect_success 'content test(force copy directory)' '
grep "lemon" ~/fruits/box/lemon &&
grep "cherry" ~/fruits/box/cherry &&
grep "guava" ~/fruits/box/guava
'

test_expect_success 'tear down' '
rm ~/apple
rm ${DOTFILES}/apple
rm -rf ~/fruits
rm -rf ${DOTFILES}/fruits
'
