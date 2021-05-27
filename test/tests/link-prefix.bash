test_description='link prefix'
. '../test-lib.bash'

test_expect_success 'setup' '
mkdir ${DOTFILES}/conf &&
echo "apple" > ${DOTFILES}/conf/a &&
echo "banana" > ${DOTFILES}/conf/b &&
echo "cherry" > ${DOTFILES}/conf/c
'

test_expect_success 'test glob w/ prefix' '
run_dotbot -v <<EOF
- link:
    ~/:
      glob: true
      path: conf/*
      prefix: '.'
EOF

grep "apple" ~/.a &&
grep "banana" ~/.b &&
grep "cherry" ~/.c
'
