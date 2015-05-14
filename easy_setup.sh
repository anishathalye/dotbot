#!/usr/bin/env bash

paths=('~/.profile' '~/.bash_profile' '~/.bashrc' '~/.bash_logout' '~/.gitconfig' '~/.ssh/config' '~/.tmux.conf' '~/.vimrc' '~/.vim/vimrc' '~/.zprofile' '~/.zshenv' '~/.zshrc' '~/bin' '~/.Xmodmap' '~/.Xresources' '~/.Xdefaults' '~/.vimperatorrc' '~/.xinitrc' '~/.i3' '~/.i3status.conf' '~/.config/awesome' '~/.config/pianobar' '~/.config/vimprobable' '~/.config/redshift' '~/.config/openbox' '~/.config/tint2')

echo "Welcome to the configuration generator for DotBot"
echo "Please be aware that if you have a complicated setup, you may need more customization than this script offers."


for item in ${paths[*]}
do
	fullname="${item/\~/$HOME}"
	if [ -f $fullname ] || [ -d $fullname ]; then
		moveon=0;
		until [ $moveon -eq 1 ]; do
			read -p "I found ${item}, do you want to dotbot it? (Y/n) " answer
			if echo "$answer" | grep -iq "^y" || echo "$answer" | grep -q "^$" ; then
				echo "Dotbotted!"
				moveon=1
			elif echo "$answer" | grep -iq "^n"; then
				echo "Not!"
				moveon=1
			else
				echo "Answer not understood: ${answer}"
			fi
		done
	fi
done

