#!/usr/bin/env bash
echoerr() { echo "$@" >&2; }

paths=('~/.profile' '~/.bash_profile' '~/.bashrc' '~/.bash_logout' '~/.gitconfig' '~/.ssh/config' '~/.tmux.conf' '~/.vimrc' '~/.vim/vimrc' '~/.zprofile' '~/.zshenv' '~/.zshrc' '~/bin' '~/.Xmodmap' '~/.Xresources' '~/.Xdefaults' '~/.vimperatorrc' '~/.xinitrc' '~/.i3' '~/.i3status.conf' '~/.config/awesome' '~/.config/pianobar' '~/.config/vimprobable' '~/.config/redshift' '~/.config/openbox' '~/.config/tint2')

setupshell='echo "Setting up DotBot. Please do not ^C." >&2'
dotclean=''
dotlink=''
dotshell=''

echoerr "Welcome to the configuration generator for DotBot"
echoerr "Please be aware that if you have a complicated setup, you may need more customization than this script offers."
echoerr;
echoerr "At any time, press ^C to quit. No changes will be made until you confirm."
echoerr;

prefix="~/.dotfiles"
prefixfull="${prefix/\~/${HOME}}"

if ! [ -d $prefixfull ]; then
	echoerr "${prefix} is not in use."
else
	echoerr "${prefix} exists and may have another purpose than ours."
fi


moveon=0;
until (( $moveon )); do
	read -p "Where do you want your dotfiles repository to be? ($prefix) " answer
	if echo "$answer" | grep -q "^$" ; then
		moveon=1
	else
		echoerr "FEATURE NOT YET SUPPORTED."
		echoerr "Sorry for misleading you."
		echoerr;
	fi
done

setupshell=$setupshell'; mkdir -p '$prefix'; cd '$prefix'; git init'

moveon=0;
until (( $moveon )); do
	read -p "Shall we add DotBot as a submodule (a good idea)? (Y/n) " answer
	if echo "$answer" | grep -iq "^y" || echo "$answer" | grep -q "^$" ; then
		echoerr "Will do."
		setupshell=$setupshell'; git submodule add https://github.com/anishathalye/dotbot; cp dotbot/tools/git-submodule/install .'
		moveon=1
	elif echo "$answer" | grep -iq "^n"; then
		echoerr "Okay, I shall not. You will need to manually set up your install script."
		moveon=1
	else
		echoerr "Answer not understood: ${answer}"
	fi
done

moveon=0;
until (( $moveon )); do
	read -p "Do you want DotBot to clean ~/ of broken links added by DotBot? (recommended) (Y/n) " answer
	if echo "$answer" | grep -iq "^y" || echo "$answer" | grep -q "^$" ; then
		echoerr "I will ask DotBot to clean."
		dotclean="- clean: ['~']"
		moveon=1
	elif echo "$answer" | grep -iq "^n"; then
		echoerr "Not asking DotBot to clean."
		moveon=1
	else
		echoerr "Answer not understood: ${answer}"
	fi
done


declare -a linksection;
declare -i i;

echoerr "Going to iterate items"
for item in ${paths[*]}
do
	fullname="${item/\~/$HOME}"
	if [ -f $fullname ] || [ -d $fullname ]; then
		echoerr "Found one!"
		moveon=0;
		until (( $moveon )); do
			read -p "I found ${item}, do you want to DotBot it? (Y/n) " answer
			if echo "$answer" | grep -iq "^y" || echo "$answer" | grep -q "^$" ; then
				linksection[$i]=$item;
				i=$i+1
				echoerr "DotBotted!"
				moveon=1
			elif echo "$answer" | grep -iq "^n"; then
				echoerr "Not added to DotBot."
				moveon=1
			else
				echoerr "Answer not understood: ${answer}"
			fi
		done
	fi
done

dotlink='- link:'
newline='\n'
hspace='\x20\x20\x20\x20'

for item in ${linksection[*]}
do
	fullname="${item/\~/$HOME}"
	firstdot=`expr index "$item" .`
	firstslash=`expr index "$item" /`
	if [ -d $fullname ]; then
		itempath=$item'/'
	else
		itempath=$item
	fi
	if [[ $firstdot -gt $firstslash ]] ; then
		itempath=${itempath:$firstdot};
	else
		itempath=${itempath:$firstslash};
	fi
	new_entry=$newline$hspace$item':'
	new_entry=$new_entry$newline$hspace$hspace'path: '$itempath
	new_entry=$new_entry$newline$hspace$hspace'create: true'
	new_entry=$new_entry$newline$hspace$hspace'relink: false'
	new_entry=$new_entry$newline$hspace$hspace'force: false'

	setupshell=$setupshell'; mkdir -p '$itempath'; rmdir '$itempath'; mv '$item' '$itempath
	dotlink="$dotlink$new_entry"
done

export installconfyaml="$dotclean$newline$newline$dotlink$newline$newline$dotshell"

setupshell=$setupshell'; echo -e "'$installconfyaml'" > install.conf.yaml'


moveon=0;
until (( $moveon )); do
	read -p "Shall I make the initial commit? (Y/n) " answer
	if echo "$answer" | grep -iq "^y" || echo "$answer" | grep -q "^$" ; then
		echoerr "Will do."
		setupshell=$setupshell'; git add -A; git commit -m "Initial commit"'
		moveon=1
	elif echo "$answer" | grep -iq "^n"; then
		echoerr "Okay, I shall not. You will need to take care of that yourself."
		moveon=1
	else
		echoerr "Answer not understood: ${answer}"
	fi
done

echoerr;
echo $dotlink
echoerr
echoerr "The below are the actions that will be taken to setup DotBot."

echoerr $setupshell

read -p "If you do not see a problem with the above commands, press enter. This is your last chance to press ^C before actions are taken that should not be interrupted. "

eval $setupshell
