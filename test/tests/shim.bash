test_description='install shim works'
. '../test-lib.bash'

test_expect_success 'setup' '
cd ${DOTFILES}
git init
git submodule add ${BASEDIR} dotbot
cp ./dotbot/tools/git-submodule/install .
echo "pear" > ${DOTFILES}/foo
'

test_expect_success 'run' '
cat > ${DOTFILES}/install.conf.yaml <<EOF
- link:
    ~/.foo: foo
EOF
${DOTFILES}/install
'

test_expect_success 'test' '
grep "pear" ~/.foo
'
