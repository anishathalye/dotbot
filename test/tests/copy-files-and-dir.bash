test_description='Basic copy test'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/apple
echo "watermelon" > ${DOTFILES}/water
echo "grape" > ${DOTFILES}/grape
mkdir -p ${DOTFILES}/more/fruits
echo "guava" > ${DOTFILES}/more/fruits/guava
'

test_expect_success 'run by conf' '
run_dotbot <<EOF
- copy:
    ~/apple:
    ~/melon: water
    ~/grape:
    ~/.fruits:
        path: more/fruits
EOF
'

test_expect_success 'content test' '
grep "apple" ~/apple &&
grep "watermelon" ~/melon &&
grep "grape" ~/grape &&
grep "guava" ~/.fruits/guava
'

test_expect_success 'tear down' '
rm ~/apple
rm ~/melon
rm ~/grape
rm -rf ~/.fruits
rm ${DOTFILES}/apple
rm ${DOTFILES}/water
rm ${DOTFILES}/grape
rm -rf ${DOTFILES}/fruits
'
