#!/usr/bin/env bash
echoerr() { echo "$@" >&2; }
appendshell() {
	case "$1" in
		start)
			add='echo "Setting up DotBot. Please do not ^C." >&2;'
			;;
		mkprefix)
			add="mkdir -p $2; cd $2;"
			;;
		gitinit)
			add='git init;'
			;;
		gitaddsub)
			add='git submodule add https://github.com/anishathalye/dotbot;'
			;;
		gitinstallinstall)
			add='cp dotbot/tools/git-submodule/install .;'
			;;
		ensureparentdirs)
			add="mkdir -p $2; rmdir $2;"
			;;
		mv)
			add="mv $2 $3;"
			;;
		echoconfig)
			add='echo -e "'$2'" > '$3';'
			;;
		runinstaller)
			add='./install;'
			;;
		gitinitialcommit)
			add='git add -A; git commit -m "Initial commit";'
			;;

	esac
	setupshell=$setupshell' '$add
}

testmode=0;
verboseconf=0;
dumpconf=0;
preview=1;

while [ $# -ne 0 ]; do
	case "$1" in
		test)
			testmode=1;
			echoerr "Test mode enabled."
			;;
		no-test)
			testmode=0;
			echoerr "Test mode disabled."
			;;
		verbose-config)
			verboseconf=1;
			echoerr "Verbose configuration file active."
			;;
		no-verbose-config)
			verboseconf=0;
			echoerr "Concise configuration file active."
			;;
		dump-config)
			dumpconf=1;
			echoerr "Will dump config to stdout."
			;;
		no-dump-config)
			dumpconf=0;
			echoerr "Will not dump config to stdout."
			;;
		preview)
			preview=1;
			echoerr "Will show commands to be executed."
			;;
		no-preview)
			preview=0;
			echoerr "Will not show commands to be executed."
			;;
		*)
			echoerr "Unfamiliar configuration option"
	esac
	shift
done

paths=('~/.profile' '~/.bash_profile' '~/.bashrc' '~/.bash_logout' '~/.gitconfig' '~/.ssh/config' '~/.tmux.conf' '~/.vimrc' '~/.vim/vimrc' '~/.zprofile' '~/.zshenv' '~/.zshrc' '~/bin' '~/.Xmodmap' '~/.Xresources' '~/.Xdefaults' '~/.vimperatorrc' '~/.xinitrc' '~/.i3' '~/.i3status.conf' '~/.config/awesome' '~/.config/pianobar' '~/.config/vimprobable' '~/.config/redshift' '~/.config/openbox' '~/.config/tint2')

setupshell=''
dotclean=''
dotlink=''
dotshell=''
installerrun=1;

echoerr "Welcome to the configuration generator for DotBot"
echoerr "Please be aware that if you have a complicated setup, you may need more customization than this script offers."
echoerr;
echoerr "At any time, press ^C to quit. No changes will be made until you confirm."
echoerr;

appendshell start

prefix="~/.dotfiles"
prefixfull="${prefix/\~/${HOME}}"

if ! [ -d $prefixfull ]; then
	echoerr "${prefix} is not in use."
else
	echoerr "${prefix} exists and may have another purpose than ours."
fi


while true; do
	read -p "Where do you want your dotfiles repository to be? ($prefix) " answer
	if [ -z $answer ]; then
		break
	else
		echoerr "FEATURE NOT YET SUPPORTED."
		echoerr "Sorry for misleading you."
		echoerr;
	fi
done

appendshell mkprefix $prefix
appendshell gitinit

while true; do
	read -p "Shall we add DotBot as a submodule (a good idea)? (Y/n) " answer
	if [ -z $answer ]; then
		answer='y'
	fi
	case "$answer" in
		Y*|y*)
			echoerr "Will do."
			appendshell gitaddsub
			appendshell gitinstallinstall
			break
			;;
		N*|n*)
			echoerr "Okay, I shall not. You will need to manually set up your install script."
			installerrun=0;
			break
			;;
		*)
			echoerr "Answer not understood: ${answer}"
			;;
	esac
done

while true; do
	read -p "Do you want DotBot to clean ~/ of broken links added by DotBot? (recommended) (Y/n) " answer
	if [ -z $answer ]; then
		answer='y'
	fi
	case "$answer" in
		Y*|y*)
			echoerr "I will ask DotBot to clean."
			dotclean="- clean: ['~']"
			break
			;;
		N*|n*)
			echoerr "Not asking DotBot to clean."
			break
			;;
		*)
			echoerr "Answer not understood: ${answer}"
			;;
	esac
done


declare -a linksection;
declare -i i;

echoerr "Going to iterate items"
for item in ${paths[*]}
do
	fullname="${item/\~/$HOME}"
	if [ -f $fullname ] || [ -d $fullname ]; then
		while true; do
			read -p "I found ${item}, do you want to DotBot it? (Y/n) " answer
			if [ -z $answer ]; then
				answer='y'
			fi
			case "$answer" in
				Y*|y*)
					linksection[$i]=$item;
					i=$i+1
					echoerr "DotBotted!"
					break
					;;
				N*|n*)
					echoerr "Not added to DotBot."
					break
					;;
				*)
					echoerr "Answer not understood: ${answer}"
			esac
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
	nextslash=`expr index "$itempath" /`
	if [[ $nextslash -gt 0 ]]; then
		entryisdir='true';
	else
		entryisdir='false';
	fi
	if (( $verboseconf )); then
		new_entry=$newline$hspace$item':'
		new_entry=$new_entry$newline$hspace$hspace'path: '$itempath
		new_entry=$new_entry$newline$hspace$hspace'create: '$entryisdir
		new_entry=$new_entry$newline$hspace$hspace'relink: false'
		new_entry=$new_entry$newline$hspace$hspace'force: false'
	elif [[ $entryisdir = 'false' ]]; then
		new_entry=$newline$hspace$item': '$itempath
	else
		new_entry=$newline$hspace$item':'
		new_entry=$new_entry$newline$hspace$hspace'path: '$itempath
		new_entry=$new_entry$newline$hspace$hspace'create: '$entryisdir
	fi

	appendshell ensureparentdirs $itempath;
	appendshell mv $item $itempath
	dotlink="$dotlink$new_entry"
done

export installconfyaml="$dotclean$newline$newline$dotlink$newline$newline$dotshell"

appendshell echoconfig "$installconfyaml" 'install.conf.yaml'


while (( $installerrun )); do
	read -p "Shall I run the installer? (Necessary to git commit) (Y/n) " answer
	if [ -z $answer ]; then
		answer='y'
	fi
	case "$answer" in
		Y*|y*)
			echoerr "Will do."
			appendshell runinstaller
			break
			;;
		N*|n*)
			echoerr "Okay, I shall not. You will need to take care of that yourself."
			installerrun=0;
			break
			;;
		*)
			echoerr "Answer not understood: ${answer}"
			;;
	esac
done

while (( $installerrun )); do
	read -p "Shall I make the initial commit? (Y/n) " answer
	if [ -z $answer ]; then
		answer='y'
	fi
	case "$answer" in
		Y*|y*)
			echoerr "Will do."
			appendshell gitinitialcommit
			break
			;;
		N*|n*)
			echoerr "Okay, I shall not. You will need to take care of that yourself."
			break
			;;
		*)
			echoerr "Answer not understood: ${answer}"
			;;
	esac
done

echoerr;
if (( $dumpconf )); then
	echo -e "$dotlink"
	echoerr
fi
echoerr "The below are the actions that will be taken to setup DotBot."
if (( $testmode )); then
	echoerr "Just kidding. They won't be."
fi

if (( $preview )); then
	echoerr $setupshell
	warningmessage='If you do not see a problem with the above commands, press enter. '
else
	warningmessage=''
fi

read -p "${warningmessage}This is your last chance to press ^C before actions are taken that should not be interrupted. "

if ! (( $testmode )); then
	eval $setupshell
fi
