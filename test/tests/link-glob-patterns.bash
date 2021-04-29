test_description='link glob, all patterns'
. '../test-lib.bash'

allfruit=(apple apricot banana cherry currant cantalope)

test_expect_success 'glob patterns setup' '
mkdir ${DOTFILES}/conf &&
for fruit in "${allfruit[@]}"; do
  echo "${fruit}" > ${DOTFILES}/conf/${fruit}
  echo "dot-${fruit}" > ${DOTFILES}/conf/.${fruit}
done
'

test_expect_success 'glob patterns: "conf/*"' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/globtest: conf/*
EOF

for fruit in "${allfruit[@]}"; do
  grep "${fruit}" ~/globtest/${fruit} &&
  test \! -e ~/globtest/.${fruit}
done
'

test_expect_success 'reset' 'rm -rf ~/globtest'

test_expect_success 'glob pattern: "conf/.*"' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/globtest: conf/.*
EOF

for fruit in "${allfruit[@]}"; do
  test \! -e ~/globtest/${fruit} &&
  grep "dot-${fruit}" ~/globtest/.${fruit}
done
'

test_expect_success 'reset 2' 'rm -rf ~/globtest'

test_expect_success 'glob pattern: "conf/[bc]*"' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/globtest: conf/[bc]*
EOF

for fruit in "${allfruit[@]}"; do
  [[ $fruit = [bc]* ]] &&
  grep "${fruit}" ~/globtest/${fruit} ||
  test \! -e ~/globtest/${fruit} &&
  test \! -e ~/globtest/.${fruit}
done
'

test_expect_success 'reset 3' 'rm -rf ~/globtest'

test_expect_success 'glob pattern: "conf/*e"' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/globtest: conf/*e
EOF

for fruit in "${allfruit[@]}"; do
  [[ $fruit = *e ]] &&
  grep "${fruit}" ~/globtest/${fruit} ||
  test \! -e ~/globtest/${fruit} &&
  test \! -e ~/globtest/.${fruit}
done
'

test_expect_success 'reset 4' 'rm -rf ~/globtest'

test_expect_success 'glob pattern: "conf/??r*"' '
run_dotbot -v <<EOF
- defaults:
    link:
      glob: true
      create: true
- link:
    ~/globtest: conf/??r*
EOF

for fruit in "${allfruit[@]}"; do
  [[ $fruit = ??r* ]] &&
  grep "${fruit}" ~/globtest/${fruit} ||
  test \! -e ~/globtest/${fruit} &&
  test \! -e ~/globtest/.${fruit}
done
'
