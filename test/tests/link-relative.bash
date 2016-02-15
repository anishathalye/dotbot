test_description='relative linking works'
. '../test-lib.bash'

test_expect_success 'setup' '
echo "apple" > ${DOTFILES}/f &&
mkdir ${DOTFILES}/d &&
echo "grape" > ${DOTFILES}/d/e
'

test_expect_success 'run' '
run_dotbot <<EOF
- link:
    ~/.f:
      path: f
    ~/.frel:
      path: f
      relative: true
    ~/nested/.frel:
      path: f
      create: true
      relative: true
    ~/.d:
      path: d
      relative: true
EOF
'

test_expect_success 'test' '
grep "apple" ~/.f &&
grep "apple" ~/.frel &&
[[ "$(readlink ~/.f)" == "$(readlink -f dotfiles/f)" ]] &&
[[ "$(readlink ~/.frel)" == "dotfiles/f" ]] &&
[[ "$(readlink ~/nested/.frel)" == "../dotfiles/f" ]] &&
grep "grape" ~/.d/e &&
[[ "$(readlink ~/.d)" == "dotfiles/d" ]]
'
