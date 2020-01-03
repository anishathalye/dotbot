test_description='linking canonicalizes path by default'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/f &&
ln -s dotfiles dotfiles-symlink
'

test_expect_success 'run' '
cat > "${DOTFILES}/${INSTALL_CONF}" <<EOF
- link:
    ~/.f:
      path: f
EOF
${DOTBOT_EXEC} -c dotfiles-symlink/${INSTALL_CONF}
'

test_expect_success 'test' '
[ "$(readlink ~/.f | cut -d/ -f4-)" = "dotfiles/f" ]
'
