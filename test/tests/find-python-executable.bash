test_description='can find python executable with different names'
. '../test-lib.bash'

# the test machine needs to have a binary named `python`
test_expect_success 'setup' '
mkdir ~/tmp_bin &&
(
    IFS=:
    for p in $PATH; do
        if [ -d $p ]; then
            find $p -maxdepth 1 -mindepth 1 -exec sh -c \
            '"'"'ln -sf {} $HOME/tmp_bin/$(basename {})'"'"' \;
        fi
    done
) &&
rm -f ~/tmp_bin/python &&
rm -f ~/tmp_bin/python2 &&
rm -f ~/tmp_bin/python3
'

test_expect_failure 'run' '
PATH="$HOME/tmp_bin" run_dotbot <<EOF
[]
EOF
'

test_expect_success 'setup 2' '
touch ~/tmp_bin/python &&
chmod +x ~/tmp_bin/python &&
cat >> ~/tmp_bin/python <<EOF
#!$HOME/tmp_bin/bash
exec $(command -v python)
EOF
'

test_expect_success 'run 2' '
PATH="$HOME/tmp_bin" run_dotbot <<EOF
[]
EOF
'

test_expect_success 'setup 3' '
mv ~/tmp_bin/python ~/tmp_bin/python2
'

test_expect_success 'run 3' '
PATH="$HOME/tmp_bin" run_dotbot <<EOF
[]
EOF
'

test_expect_success 'setup 4' '
mv ~/tmp_bin/python2 ~/tmp_bin/python3
'

test_expect_success 'run 4' '
PATH="$HOME/tmp_bin" run_dotbot <<EOF
[]
EOF
'
