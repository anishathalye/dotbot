test_description='install shim works'
. '../test-lib.bash'

test_expect_success 'setup' '
cd ${DOTFILES}
git init
if ${USE_VAGRANT}; then
    git submodule add /dotbot dotbot
else
    git submodule add ${BASEDIR} dotbot
fi
cp ./dotbot/tools/git-submodule/install .
echo "pear" > ${DOTFILES}/foo
'

test_expect_success 'run' '
cat > ${DOTFILES}/install.conf.yaml <<EOF
- link:
    ~/.foo: foo
EOF
if ! ${USE_VAGRANT}; then
    sed -i "" "1 s/sh$/python/" ${DOTFILES}/dotbot/bin/dotbot
fi
${DOTFILES}/install
'

test_expect_success 'test' '
grep "pear" ~/.foo
'
