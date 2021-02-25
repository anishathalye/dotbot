test_description='linking path canonicalization can be disabled'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/f &&
echo "grape" > ${DOTFILES}/g &&
ln -s dotfiles dotfiles-symlink
'

test_expect_success 'run' '
cat > "${DOTFILES}/${INSTALL_CONF}" <<EOF
- defaults:
    link:
      canonicalize-path: false
- link:
    ~/.f:
      path: f
EOF
${DOTBOT_EXEC} -c ./dotfiles-symlink/${INSTALL_CONF}
'

test_expect_success 'test' '
[ "$(readlink ~/.f | cut -d/ -f5-)" = "dotfiles-symlink/f" ]
'

test_expect_success 'run 2' '
cat > "${DOTFILES}/${INSTALL_CONF}" <<EOF
- defaults:
    link:
      canonicalize: false
- link:
    ~/.g:
      path: g
EOF
${DOTBOT_EXEC} -c ./dotfiles-symlink/${INSTALL_CONF}
'

test_expect_success 'test' '
[ "$(readlink ~/.g | cut -d/ -f5-)" = "dotfiles-symlink/g" ]
'
