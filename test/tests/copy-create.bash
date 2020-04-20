test_description='Basic copy test'
. '../test-lib.bash'

test_expect_success 'setup' '
mkdir -p ${DOTFILES}/box
echo "apple" > ${DOTFILES}/apple
echo "banana" > ${DOTFILES}/box/banana
'

test_expect_failure 'copy file should fail without create option' '
run_dotbot <<EOF
- copy:
    ~/more/fruits/apple:
        path: apple
EOF
'
test_expect_failure 'copy directory should fail without create option' '
run_dotbot <<EOF
- copy:
    ~/more/fruits/in:
        path: box
EOF
'

test_expect_success 'run with create option' '
run_dotbot <<EOF
- copy:
    ~/more/fruits/apple:
        path: apple
        create: true
    ~/more/fruits/unbox/:
        path: box
        create: true
EOF
'
test_expect_success 'content test' '
grep "apple" ~/more/fruits/apple &&
grep "banana" ~/more/fruits/unbox/banana
'

test_expect_success 'tear down' '
rm -rf ~/more
rm ${DOTFILES}/apple
rm -rf ${DOTFILES}/box
'
