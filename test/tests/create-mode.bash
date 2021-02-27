test_description='create mode'
. '../test-lib.bash'

test_expect_success 'run' '
run_dotbot -v <<EOF
- defaults:
    create:
      mode: 0755
- create:
    - ~/downloads
    - ~/.vim/undo-history
- create:
    ~/.ssh:
      mode: 0700
    ~/projects:
EOF
'

test_expect_success 'test' '
[ -d ~/downloads ] &&
[ -d ~/.vim/undo-history ] &&
[ -d ~/.ssh ] &&
[ -d ~/projects ] &&
[ "$(stat -c %a ~/.ssh)" = "700" ] &&
[ "$(stat -c %a ~/downloads)" = "755" ]
'
