#!/usr/bin/env bash

paths=('~/.profile' '~/.bash_profile' '~/.bashrc' '~/.bash_logout' '~/.gitconfig' '~/.ssh/config' '~/.tmux.conf' '~/.vimrc' '~/.vim/vimrc' '~/.zprofile' '~/.zshenv' '~/.zshrc' '~/bin' '~/.Xmodmap' '~/.Xresources' '~/.Xdefaults' '~/.vimperatorrc' '~/.xinitrc' '~/.i3' '~/.i3status.conf' '~/.config/awesome' '~/.config/pianobar' '~/.config/vimprobable' '~/.config/redshift' '~/.config/openbox' '~/.config/tint2')

setupshell='echo "Setting up DotBot. Please do not ^C."'
dotclean=''
dotlink=''
dotshell=''

echo "Welcome to the configuration generator for DotBot"
echo "Please be aware that if you have a complicated setup, you may need more customization than this script offers."
echo;
echo "At any time, press ^C to quit. No changes will be made until you confirm."
echo;

prefix="~/.dotfiles"
prefixfull="${prefix/\~/${HOME}}"

if ! [ -d $prefixfull ]; then
	echo "${prefix} is not in use."
else
	echo "${prefix} exists and may be in use."
fi


moveon=0;
until [ $moveon -eq 1 ]; do
	read -p "Where do you want your dotfiles repository to be? (~/.dotfiles) " answer
	if echo "$answer" | grep -q "^$" ; then
		moveon=1
	else
		echo "FEATURE NOT YET SUPPORTED."
		echo "Sorry for misleading you."
		echo;
#		prefix=$answer
#		read -p "Press enter to confirm selection, anything else and then enter to try again. " answer
#		moveon=(test "${answer}" == "")
	fi
done

setupshell="${setupshell}; mkdir -p ${prefix}; cd ${prefix}"

moveon=0;
until [ $moveon -eq 1 ]; do
	read -p "Shall we add DotBot as a submodule (a good idea)? (Y/n) " answer
	if echo "$answer" | grep -iq "^y" || echo "$answer" | grep -q "^$" ; then
		echo "Will do."
		setupshell="${setupshell}; git submodule add https://github.com/anishathalye/dotbot; cp dotbot/tools/git-submodule/install ."
		moveon=1
	elif echo "$answer" | grep -iq "^n"; then
		echo "Okay, I shall not. You will need to manually set up your install script."
		moveon=1
	else
		echo "Answer not understood: ${answer}"
	fi
done



moveon=0;
until [ $moveon -eq 1 ]; do
	read -p "Do you want DotBot to clean ~/ of broken links added by DotBot? (recommended) (Y/n) " answer
	if echo "$answer" | grep -iq "^y" || echo "$answer" | grep -q "^$" ; then
		echo "I will ask DotBot to clean."
		dotclean="- clean: ['~']"
		moveon=1
	elif echo "$answer" | grep -iq "^n"; then
		echo "Not asking DotBot to clean."
		moveon=1
	else
		echo "Answer not understood: ${answer}"
	fi
done


i=0;
declare -a linksection

for item in ${paths[*]}
do
	fullname="${item/\~/$HOME}"
	if [ -f $fullname ] || [ -d $fullname ]; then
		moveon=0;
		until [ $moveon -eq 1 ]; do
			read -p "I found ${item}, do you want to dotbot it? (Y/n) " answer
			if echo "$answer" | grep -iq "^y" || echo "$answer" | grep -q "^$" ; then
				linksection[$i]="${item}";
				i=$i+1
				echo "DotBotted!"
				moveon=1
			elif echo "$answer" | grep -iq "^n"; then
				echo "Not added to DotBot."
				moveon=1
			else
				echo "Answer not understood: ${answer}"
			fi
		done
	fi
done

dotlink="- link:"

for item in ${linksection[*]}
do
	dotlink="${dotlink}"$'\f\r'$item
done

echo $dotlink
