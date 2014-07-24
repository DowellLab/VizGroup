#!/bin/sh
#################################################################################################
#
# LAXUNIX.SH - LaunchAnywhere (tm) version 5.0
#
# (c) Copyright 1999-2002 Zero G Software, Inc., all rights reserved.
#
#  To run this script you will need to have the following:
#	1) a Java VM installed (however, it will handle a lack of Java nicely).
#	2) a Java-style properties file having the same name as this script 
#		with the suffix .lax.  If this script is appended to the
#		self-extractor, it will look for the properties file in the
#		directory specified by $seLaxPath; otherwise, it will look in
#		the same directory that this script is in.
#	3) a Java program in the file "lax.jar".
#
#  The .lax property file must contain at least the following properties:
#	1)  lax.class.path  classpath (do not include the environment variable $CLASSPATH )
#	2)  lax.nl.java.launcher.main.class  (main class of LaunchAnywhere Executable)
#
#################################################################################################

#
# Since USERENV is already set in the self-extractor, if its not set we know
# this is not an installer but a separate launcher. 
# USERENV is just a flag passed from use.sh.
#
IS_INSTALLER=''
[ $USERENV ] && IS_INSTALLER=true

#
# later on we might add things to the PATH, but we want to preserve the PATH
# order for which VMs are the first ones found.
#
VM_SEARCH_PATH="$PATH"

####################################################################################
# Set some constants
if [ "$1" = "LAX_VM" ]; then
	lax_vm="LAX_VM"
	lax_vm_value="$2"
	shift 2
else
	lax_vm=""
fi 
anyVMlist="JDK_J2 D12 JRE_J2 R12 JDK_J1 JRE_J1 JDK JRE ALL" 


####################################################################################
# Format commandline args
# To overcome the problem of quoted args (with internal spaces) to the launcher
# is that they get "unquoted" or separated into discreet args when they are put
# on the cmdline for the application.  This following block makes  sure the stay intact
overrideDefaultUIMode="false"
ignoreMode="false";
uimode="not set"
hasSeenI="false"
tmpArgs=""
origArgs=$@
for arg in "$@"
do
	if [ "$arg" != "" ]; then
		tmpArgs="$tmpArgs \"$arg\""
		if [ "$arg" = "-i" -o "$arg" = "-I" ]; then
			hasSeenI="true"
		elif [ "$hasSeenI" = "true" ]; then
			lowerArg=`echo $arg | tr "[:upper:]" "[:lower:]"`
			if [ "$lowerArg" = "awt" ]; then
				uimode="awt"
				overrideDefaultUIMode="true"
			elif [ "$lowerArg" = "swing" ]; then
				uimode="swing"
				overrideDefaultUIMode="true"
			elif [ "$lowerArg" = "gui" ]; then
				uimode="gui"
				overrideDefaultUIMode="true"
			elif [ "$lowerArg" = "console" ]; then
				uimode="console"
				overrideDefaultUIMode="true"
			elif [ "$lowerArg" = "text" ]; then
				uimode="console"
				overrideDefaultUIMode="true"
			elif [ "$lowerArg" = "silent" ]; then
				uimode="silent"
				overrideDefaultUIMode="true"
			else
				ignoreMode="true"
			fi
		fi
	fi
done
cmdLineArgs="$tmpArgs"
thisScript="$0"
# make sure thisScript is an abs path
case $thisScript in
	/*)
	;;
	*)
		thisScript="`pwd`/$thisScript"
	;;
esac

####################################################################################
#
# WHere does the LAX_DEBUG output go?
#

if [ "$LAX_DEBUG" = "file" ]; then
	jx_log="`pwd`/jx.log"
	rm -f "$jx_log"
	touch "$jx_log"
	if [ "$?" -gt "0" ]; then
		jx_log_ok="false"
		echo "Could not create $jx_log.  Sending debug output to console."
	else 
		jx_log_ok="true"
	fi
fi

debugOut()
{
	case "$LAX_DEBUG" in
		"file" ) 
			if [ "$jx_log_ok" = "true" ]; then
				echo "$1" >> "$jx_log"
			else
				echo "$1"
			fi
		;;
		""     )
			echo "$1" >> /dev/null
		;;
		*      )
			echo "$1"
		;;
	esac
}

####################################################################################
#
# UNIX ENVIRONMENT configuration
#
debugOut ""
debugOut "[7m========= Analyzing UNIX Environment =================================[0m"


# Get os type , note that it is LOWER-CASED.  Used here and later on
osName=`uname -s 2> /dev/null | tr "[:upper:]" "[:lower:]" 2> /dev/null`
debugOut "Setting UNIX ($osName) flavor specifics."
vmScript=".java_wrapper"
case "$osName" in
	*irix*)
		cpuName="unknown"
	;;
	*hp-ux*|*hpux*)
		cpuName=`uname -m 2> /dev/null`
	;;
	*solaris*|*sunos*)
		cpuName=`uname -p 2> /dev/null`
		THREADS_FLAG="";	export THREADS_FLAG 
		PATH=/usr/bin:$PATH;	export PATH
	;;
	*aix*)
		cpuName="unknown"
	;;
	*freebsd*)
		cpuName=`uname -p 2> /dev/null`
	;;
	*linux*)
		cpuName=`uname -m 2> /dev/null`
	;;
	# tlb 2001-09-18 updating to support Darwin
	*rhapsody*|*darwin*)
		cpuName=`uname -p 2> /dev/null`
		vmScript=".java_command"
	;;
	*compaq*|*dg*|*osf*)
		cpuName="unknown"
	;;
	*)
		cpuName="unknown"
	;;
esac


if [ -x /bin/ls ]; then
	lsCMD="/bin/ls"
elif [ -x /usr/bin/ls ]; then
	lsCMD="/usr/bin/ls"
else
	lsCMD="ls"
fi

debugOut "Importing UNIX environment into LAX properties."

####################################################################################
# 
# CREATE ENV.PROPERTIES and figure out if this is being exec'd from an installer
#
# We need POSIX awk. On some systems it's called awk, on others
# nawk. It's most frequently called nawk, so start with that.
#
debugOut "Checking for POSIX awk."
  
AWK=nawk
( $AWK '{}' ) < /dev/null 2>&0 || AWK=awk


if [ -z "$envPropertiesFile" ]
then
	if [ -d /tmp ]
	then
		envPropertiesFile=/tmp/env.properties.$$
	else
		envPropertiesFile="$HOME/env.properties.$$"
	fi
fi

#
# Convert environment variables to LAX properties. The variables
# are also named with alternate case (all upper, all lower).
#
# E.g.
#     export My_Env_Var="abc
#     def"
#
# is converted to:
#     lax.nl.env.exact_case.My_Env_Var=abc def
#     lax.nl.env.MY_ENV_VAR=abc def
#     lax.nl.env.my_env_var=abc def
#
# The second gsub() is used to escape backslashes so that when the properties 
# file is read by the java.util.Properties object, there is not a problem
# with incorrectly interpreted escaped unicode.
#
# This code segment is written in POSIX awk for performance reasons.
#
  
$AWK -v LAX_PREFIX=lax.nl.env. '
END { 
	for (var in ENVIRON) 
	{
		# get variable value
		value = ENVIRON[var]

		# strip newlines
		gsub(/\n/, " ", value)
  
		# convert one backslash to two
		gsub(/\\/, "\\\\", value)
  
		# print as LAX property
		print LAX_PREFIX "exact_case." var "=" value
		print LAX_PREFIX tolower(var) "=" value
		print LAX_PREFIX toupper(var) "=" value
	}
}' < /dev/null > $envPropertiesFile



####################################################################################
#
# Tracing symbolic links to actual launcher location
#

resolveLink()
{
	rl_linked="true"
	rl_operand="$1"
	rl_origDir="`dirname "$1"`"

	# bypass the whole thing if this isnt a link
	rl_ls=`$lsCMD -l "$rl_operand"`
	case "$rl_ls" in
		*"->"*)
		;;
		*)
			resolvedLink="$rl_operand"
			return
		;;
	esac 
	
	while [ "$rl_linked" = "true" ]; do
		# if the operand is not of an abs path, get its abs path
		case "$rl_operand" in
			/*)
				rl_origDir=`dirname "$rl_operand"`
			;;
			\./*)
				rl_origDir=`pwd`
				rl_operand="$rl_origDir/$rl_operand"
			;;
			*)
				rl_operand="$rl_origDir/$rl_operand"
			;;
		esac
		#
		# the prevPrev hack is here because .../java often points to .java_wrapper.
		# at the end of the resolution rl_operand actually points to garbage
		# signifying it is done resolving the link.  So prev is actually .java_wrapper.
		# but we want the one just before that, its the real vm starting poiint we want
		#
		rl_prevOperand="$rl_operand"
		rl_ls=`$lsCMD -l "$rl_operand"`
		# get the output ls into a list
		set x $rl_ls
		# get rid of x and file info from ls -l
		shift 9
		
		#is this a link?
		case "$rl_ls" in
			*"->"*)
				rl_linked="true"
				# is a link, shift past the "->"
				rl_linker=""
				while [ "$1" != "->" -a $# -gt 1 ]; do
					rl_linker="$rl_linker $1"
					shift
				done
	
				if [ "$1" = "->" ]; then
					shift
				fi
			;;
			*)
				# not a link, the rest must be the targets name
				rl_linked="false"
			;;
		esac
		# now grab what's left 
		rl_linkee="$*"

		# debugOut "Following link to LAX $rl_linker -> $rl_linkee"

		if [ "$rl_linked" = "true" -a "`basename "$rl_linkee"`" != "$vmScript" ]; then
			# set to true incase the thing linked to is also a link and we can
			# try again.  The current think linked to now becomes the operand
			rl_operand="$rl_linkee"
			# if the linkee is not abs, make it abs relative to the linker
			case "$rl_operand" in
				/*)
				;;
				*)
					rl_operand="$rl_origDir/$rl_operand"
				;;
			esac
		else
			# otherwise, this operand is not a link itself and we are done
			rl_resolvedLink="$rl_prevOperand"
			# however, do not resolve the last leg of a VMs linked scripts. this will
			# disrupt their scripts.  it is expecting a link to the .java* script
			# let us believe it is not linked and continue on...
			if [ "`basename "$rl_linkee"`" = "$vmScript" ]; then
				rl_linked="false"
			fi
		fi
		# make sure the path returned is absolute
		case "$rl_operand" in
			\.\/*)
				rl_operand="`pwd`/$rl_operand"
			;;
		esac
	done

	# remove "/./" in paths, make it "/"
	# i,e,  "/a/b/./c" becomes "/a/b/c"
	resolvedLink=`echo "$rl_resolvedLink" |  sed 's,/\./,/,'`
}

####################################################################################
#
#  FINDING THE LAX FILE
#
# If this is an installer, use $seLaxPath
#
debugOut ""
debugOut "[7m========= Analyzing LAX ==============================================[0m"
olddir=`pwd`
resolveLink "$thisScript"
absLauncherName="$resolvedLink"
cd "`dirname "$absLauncherName"`"
if [ "$IS_INSTALLER" != "" ]; then
	if [ ! -z "$seLaxPath" ]; then
		propfname="$seLaxPath"
	else
		# legacy for old self-extractors
		propfname="$templaxpath"
	fi 
else
	propfname="$absLauncherName.lax"
fi


if [ ! -r "$propfname" ]; then
	debugOut "The file "$propfname" could"
	debugOut "not be found, and the program cannot be run without it."
	debugOut "Try reinstalling the program."
	exit;
else 
	debugOut "LAX found............................ OK."
fi


####################################################################################
# 
# READING THE LAX FILE
#
OFS="$IFS"
# run prop file through sed calls that do:
# 1. transform first '=' on a line into a control-O
# 2. transform all other ='s to control-F
# 3. transform control-Os back to =
# this is to differentiate the lhs=rhs processing from confusing the first = from other
# = that might be part of the value.  Later on those =-tranformed-to-control-Fs are
# transformed back to = signs.
set x `cat "$propfname" | sed -e 's~^\([^\=]*\)\=\(.*\)~\1\\2~g' -e 's~=~~g' -e 's~~=~g' | grep '='`; shift

while test $# -gt 0; do
	# line separator
	case "x${1}x" in
		*"="* ) BIFS=" "; ;;
		*     ) BIFS="" ; ;;
	esac
	# word separator
	case "x${2}x" in
		*"="* ) AIFS=""; ;;
		*     ) AIFS=""; ;;
	esac
	INPUT="$INPUT$BIFS$1$AIFS"
	shift
done

while test "x$INPUT" != "x"; do
	set x $INPUT; shift
	X="$1"
	shift
	INPUT="$@" 
	IFS="=$AIFS"
	set x $X; shift
	IFS="$OFS"

	lhs="${1}"
	shift
	rhs="$@"

	# transform non lhs=rhs delimiting = signs back from ^F to =
	case "$rhs" in
		**)
		rhs=`echo $rhs | sed 's~~=~g'`
		;;
	esac

	# assing the values
	case $lhs in
		lax.class.path*)
			lax_class_path="$rhs"
		;;
		lax.main.class*)
			lax_main_class="$rhs"
		;;
		lax.nl.java.launcher.main.class*)
			lax_nl_java_launcher_main_class="$rhs"
		;;
		lax.nl.current.vm*)
			lax_nl_current_vm="$rhs"
		;;
		lax.user.dir*)
			lax_user_dir="$rhs"
			lax_user_dir=`echo $lax_user_dir | sed 's;^[ ]*\(.*\)[ ]*$;\1;'`
		;;
		lax.resource.dir*)
			lax_resource_dir="$rhs"
			lax_resource_dir=`echo $lax_resource_dir | sed 's;^[ ]*\(.*\)[ ]*$;\1;'`
		;;
		lax.stdout.redirect*)
			lax_stdout_redirect="$rhs"
		;;
		lax.stderr.redirect*)
			lax_stderr_redirect="$rhs"
		;;
		lax.dir*)
			lax_dir="$rhs"
		;;
		lax.always.ask*)
			lax_always_ask="$rhs"
		;;
		lax.application.name*)
			lax_application_name="$rhs"
		;;
		lax.nl.message.vm.not.loaded*)
			lax_nl_message_vm_loaded="$rhs"
		;;
		lax.nl.valid.vm.list*)
			# transform an blank value to "ALL"
			case "$rhs" in
				"") rhs="ALL"; ;;
			esac
			lax_nl_valid_vm_list="$rhs"
		;;
		lax.nl.java.option.check.source*)
			verify="$rhs"
		;;
		lax.nl.java.option.verify.mode*)
			verify_mode="$rhs"
		;;
		lax.nl.java.option.verbose*)
			verbo="$rhs"
		;;
		lax.nl.java.option.garbage.collection.extent*)
			gcxtnt="$rhs"
		;;
		lax.nl.java.option.garbage.collection.background.thread*)
			gcthrd="$rhs"
		;;
		lax.nl.java.option.native.stack.size.max*)
			nsmax="$rhs"
		;;
		lax.nl.java.option.java.stack.size.max*)
			jsmax="$rhs"
		;;
		lax.nl.java.option.java.heap.size.max*)
			jhmax="$rhs"
		;;
		lax.nl.java.option.java.heap.size.initial*)
			jhinit="$rhs"
		;;
		lax.nl.java.option.debugging*)
			debug="$rhs"
		;;
		lax.nl.$osName.$cpuName.java.compiler*)
			lax_nl_osname_cpuname_java_compiler="$rhs"
		;;
		lax.nl.$osName.java.compiler*)
			lax_nl_osname_java_compiler="$rhs"
		;;
		lax.nl.java.compiler*)
			lax_nl_java_compiler="$rhs"
		;;
		lax.nl.java.option.additional*)
			lax_nl_java_option_additional="$rhs"
		;;
		######################################################
		# tlb 2001-09-18
		# Reading default UI mode for UNIX
		lax.installer.unix.ui.default*)
			lax_installer_unix_ui_default="$rhs"
		;;		
		######################################################
		# JIT overrides
		lax.nl.unix.JDK_J1.java.compiler*)
			lax_nl_unix_JDK_J1_java_compiler="$rhs"
		;;
		lax.nl.unix.JDK_J2.java.compiler*)
			lax_nl_unix_JDK_J2_java_compiler="$rhs"
		;;
		lax.nl.unix.JRE_J1.java.compiler*)
			lax_nl_unix_JRE_J1_java_compiler="$rhs"
		;;
		lax.nl.unix.JRE_J2.java.compiler*)
			lax_nl_unix_JRE_J2_java_compiler="$rhs"
		;;
		lax.nl.unix.J1.java.compiler*)
			lax_nl_unix_J1_java_compiler="$rhs"
		;;
		lax.nl.unix.J2.java.compiler*)
			lax_nl_unix_J2_java_compiler="$rhs"
		;;
		lax.nl.unix.JRE.java.compiler*)
			lax_nl_unix_JRE_java_compiler="$rhs"
		;;
		lax.nl.unix.JDK.java.compiler*)
			lax_nl_unix_JDK_java_compiler="$rhs"
		;;
		lax.nl.unix.ALL.java.compiler*)
			lax_nl_unix_ALL_java_compiler="$rhs"
		;;
		#
		lax.nl.JDK_J1.java.compiler*)
			lax_nl_JDK_J1_java_compiler="$rhs"
		;;
		lax.nl.JDK_J2.java.compiler*)
			lax_nl_JDK_J2_java_compiler="$rhs"
		;;
		lax.nl.JRE_J1.java.compiler*)
			lax_nl_JRE_J1_java_compiler="$rhs"
		;;
		lax.nl.JRE_J2.java.compiler*)
			lax_nl_JRE_J2_java_compiler="$rhs"
		;;
		lax.nl.J1.java.compiler*)
			lax_nl_J1_java_compiler="$rhs"
		;;
		lax.nl.J2.java.compiler*)
			lax_nl_J2_java_compiler="$rhs"
		;;
		lax.nl.JRE.java.compiler*)
			lax_nl_JRE_java_compiler="$rhs"
		;;
		lax.nl.JDK.java.compiler*)
			lax_nl_JDK_java_compiler="$rhs"
		;;
		lax.nl.ALL.java.compiler*)
			lax_nl_ALL_java_compiler="$rhs"
		;;
		#
		lax.nl.$osName.JDK_J1.java.compiler*)
			lax_nl_osname_JDK_J1_java_compiler="$rhs"
		;;
		lax.nl.$osName.JDK_J2.java.compiler*)
			lax_nl_osname_JDK_J2_java_compiler="$rhs"
		;;
		lax.nl.$osName.JRE_J1.java.compiler*)
			lax_nl_osname_JRE_J1_java_compiler="$rhs"
		;;
		lax.nl.$osName.JRE_J2.java.compiler*)
			lax_nl_osname_JRE_J2_java_compiler="$rhs"
		;;
		lax.nl.$osName.J1.java.compiler*)
			lax_nl_osname_J1_java_compiler="$rhs"
		;;
		lax.nl.$osName.J2.java.compiler*)
			lax_nl_osname_J2_java_compiler="$rhs"
		;;
		lax.nl.$osName.JRE.java.compiler*)
			lax_nl_osname_JRE_java_compiler="$rhs"
		;;
		lax.nl.$osName.JDK.java.compiler*)
			lax_nl_osname_JDK_java_compiler="$rhs"
		;;
		lax.nl.$osName.ALL.java.compiler*)
			lax_nl_osname_ALL_java_compiler="$rhs"
		;;
		#
		# JIT overrides
		######################################################
	esac
done

debugOut "LAX properties read.................. OK."

if [ "${lax_class_path:-""}" = "" ]; then
	debugOut "The classpath specified in the LAX properties file"
	debugOut "is invalid.  Try reinstalling the program."	
	exit;
fi
if [ "${lax_nl_java_launcher_main_class:-""}" = "" ]; then
	debugOut "The main class specified in the LAX properties file"
	debugOut "is invalid.  Try reinstalling the program."
	exit;
fi

if [ ! -z "$INSTALLER_OVERRIDE_VMLIST" ]; then
	lax_nl_valid_vm_list="$INSTALLER_OVERRIDE_VMLIST"
fi

###################################################
# tlb 2001-09-18
# Making sure the default UNIX UI mode is honored
# if overrideDefaultUIMode is not set, which means no commandline
# options were entered at the commandline regarding
# ui mode, we will look to the LAX file to set a ui
# mode. If there is no such setting in the LAX,
# which would be an error, we default to GUI.

	if [ "$overrideDefaultUIMode" = "false" ]; then
		if [ -n "$lax_installer_unix_ui_default" -a "$ignoreMode" = "false" ]; then
			if [ $lax_installer_unix_ui_default = SILENT ]; then
				isSilent="true"
				cmdLineArgs="$cmdLineArgs -m SILENT"
				uimode="silent"
			elif [ $lax_installer_unix_ui_default = CONSOLE ]; then
				isConsole="true"
				cmdLineArgs="$cmdLineArgs -m CONSOLE"
				uimode="console"
			elif [ $lax_installer_unix_ui_default = GUI ]; then
# Uncomment the following if statement and comment out the three lines after
# this comment to enable failsafe operation of installers when X is missing
# FAILSAFE
#				if [ -z "$DISPLAY" ]; then
#					isSilent="false"
#					isConsole="true"
#					cmdLineArgs="$cmdLineArgs -m CONSOLE"
#					uimode="console"
#					debugOut "[1mWARNING! DISPLAY variable not set. Will attempt to run installer in CONSOLE mode.[0m"
#				else
#					isSilent="false"
#					isConsole="false"
#					uimode="gui"
#				fi
# comment the following three lines out when changing to FAILSAFE
				isSilent="false"
				isConsole="false"
				uimode="gui"
			fi
		fi
	fi

####################################################################################
#
# if  user.dir != .   then relative paths on the classpath will be broken.  they
# are expecting the pwd to be '.' (meaning the install dir).  If user.dir is
# any other directory, it will break
lax_class_path=`echo "$lax_class_path" | sed 's^;^:^g'`
absInstallDir=`dirname "$absLauncherName"`
OFS="$IFS"
IFS=":"
set x $lax_class_path; shift
IFS="$OFS"
tmp_lcp=""
while test $# -gt 0; do
	case "$1" in
		\/*)
			if [ "$tmp_lcp" = "" ]; then
				tmp_lcp="$1"
			else
				tmp_lcp="$tmp_lcp:$1"
			fi
		;;
		*|*\$ENV_CLASSPATH\$*)
			if [ "$tmp_lcp" = "" ]; then
				tmp_lcp="${absInstallDir}/$1"
			else
				tmp_lcp="$tmp_lcp:${absInstallDir}/$1"
			fi
		;;
	esac
	shift
done
lax_class_path="$tmp_lcp"

# resolve $ENV_CLASSPATH$
OFS="$IFS"
IFS=":"
set x $lax_class_path; shift
IFS="$OFS"
tmp_lcp=""
while test $# -gt 0; do
	case "$1" in
		*\$ENV_CLASSPATH\$*)
			if [ "$tmp_lcp" = "" ]; then
				tmp_lcp="$CLASSPATH"
			else
				tmp_lcp="$tmp_lcp:$CLASSPATH"
			fi
		;;
		*)
			if [ "$tmp_lcp" = "" ]; then
				tmp_lcp="$1"
			else
				tmp_lcp="$tmp_lcp:$1"
			fi
		;;
	esac
	shift
done
lax_class_path="$tmp_lcp"



####################################################################################
# just incase this the lax was written in DOS, be sure to make all ';' path
# separators into :'s or it will fubar the commandline
#
case "$smclp" in
	*\;*)
		oldIFS=$IFS
		IFS=";"
		for smclp_piece in $smclp; do
			tmp_smclp="$tmp_smclp:$smclp_piece"
		done
		IFS=$oldIFS
		clp=$tmp_smclp
	;;
esac

##################################################################
# Setting stdout and stderr redirection
#
if [ "$LAX_DEBUG" = "file" -o "$LAX_DEBUG" = "" ]; then
	echo "lax.stderr.redirect=$lax_stderr_redirect" >> $envPropertiesFile
	echo "lax.stdout.redirect=$lax_stdout_redirect" >> $envPropertiesFile
else
	echo "lax.stderr.redirect=console" >> $envPropertiesFile
	echo "lax.stdout.redirect=console" >> $envPropertiesFile
	lax_stdout_redirect="console"
	lax_stderr_redirect="console"
fi

lax_version="4.5"

validVMtypeList="$lax_nl_valid_vm_list"

# MMA 04.26.2000
#
# Added check for validVMtypeList not being set to any value, in
# which case we should just set the valid list to all. 
#
if [ "$validVMtypeList" = "ALL" -o "$validVMtypeList" = "" ]; then
	validVMtypeList=$anyVMlist
fi


#############################################################
# PICK A VALID VM
#

debugOut "" 
debugOut "[7m========= Finding VM =================================================[0m"
debugOut "[1mValid VM types.......................... $validVMtypeList[0m"

#
# If the vm gets a relative path, we must make it absolute to the Install
#   Directory    tm 3/3
#
if [ ! -z "${lax_nl_current_vm:-""}" ]; then
	# tlb 2001-09-18 updating the LAX to support CD-ROM installations
	# the variable `expr "$lax_nl_current_vm" : '\/'` will evaluate to 1 if the path starts with /
	isAbsPath=`expr "$lax_nl_current_vm" : '\/'`
  	if [ "$isAbsPath" = "0" ]; then
		# When running a CD-ROM installer lax_dir is not set, lax_dir is set by the SEA.
		# We set it to the working directory if it is not set
		if [ -z "$lax_dir" ]; then
			lax_dir=`pwd`
			abs_lax_nl_current_vm="${lax_dir}"/"${lax_nl_current_vm}"
		else
			abs_lax_nl_current_vm="${lax_dir}""${lax_nl_current_vm}"
		fi		
	else
		abs_lax_nl_current_vm="$lax_nl_current_vm"
	fi
	debugOut "Absolute LAX_VM path.................... $abs_lax_nl_current_vm"
fi


#################################################################################
# inspectVM()
#
# param:      a pathname to a potential VM file, maybe a link
#
# returns:    $inspectedVMpath        the real path to the VM file
# returns:    $inspectedVMtype        the type of the VM
# returns:    $inspectedOldVMtype     ?
#
inspectVM()
{
	resolveLink "$1"

	inspectee="$resolvedLink"
	inspecteeDir=`dirname "$inspectee"`
	inspecteeName=`basename "$inspectee"`

	inspectedVMpath="$inspectee"

	#
	# is it JDK1.1 , JDK1.2  or JRE1.2?
	#
	if [ "$inspecteeName" = "oldjava" ]; then
		inspectedOldVMtype="OLDJAVA"
		inspectedVMtype="OLDJAVA"
	elif [ "$inspecteeName" = "java" ]; then

		############################################################
		# Do some OS-specific quirky stuff
		#
		# MacOS X / Rhapsody
		#
		quirk_classesZip=""
		if [ "$osName" = "rhapsody" ]; then
			if [ "`expr "$inspecteeDIR" : ".*JavaVM.framework$"`" != "0" ]; then
				quirk_classesZip="$file/Classes/classes.jar"
				inspecteeDir="$inspecteeDir/Home/bin"
			fi
		fi
		# END OS quirky stuff
		############################################################

		#
		# is it JDK1.1?
		# 
		if [ -r "$inspecteeDir/../lib/classes.zip" -o -r "$quirk_classesZip" ]; then
			inspectedOldVMtype="JDK"
			inspectedVMtype="JDK_J1"
		else
			# JDK1.2
			# 
			# is the "java" JRE1.2 or JDK1.2?
			#
			if [ -r "$inspecteeDir/../lib/dt.jar" ]
			then
				inspectedOldVMtype="D12"
				inspectedVMtype="JDK_J2"
			else
				inspectedOldVMtype="R12"
				inspectedVMtype="JRE_J2"
			fi
		fi
	elif [ "$inspecteeName" = "jre" ]; then
		inspectedOldVMtype="JRE"
		inspectedVMtype="JRE_J1"
	else
		inspectedOldVMtype="UNKNOWN"
		inspectedVMtype="UNKNOWN"
	fi
}
###
### end inspectVM()
###
########################################################################################


# massage valid VM list.  Expand inclusive types (i.e. JRE = JRE_J1 and JRE_J2 )
tmpValidVMlist=""
for type in $validVMtypeList; do
	case $type in
		J1)		tmpValidVMlist="$tmpValidVMlist JRE_J1 JDK_J1" ;;
		J2)		tmpValidVMlist="$tmpValidVMlist JRE_J2 JDK_J2" ;;
		JRE)	tmpValidVMlist="$tmpValidVMlist JRE_J2 R12 JRE_J1" ;;
		JDK)	tmpValidVMlist="$tmpValidVMlist JDK_J2 D12 JDK_J1" ;;
		*)		tmpValidVMlist="$tmpValidVMlist $type " ;;
	esac
done
validVMtypeList="$tmpValidVMlist"
debugOut "[1mExpanded Valid VM types................. $validVMtypeList[0m"

# if a VM was forced on the command line use it otherwise search
if [ "$lax_vm" = "LAX_VM" ]; then
	# Using VM passed in as argument
	inspectVM "$lax_vm_value"
	actvmType="$inspectedVMtype"
	actvm="$lax_vm_value"
	debugOut "* Using VM:.........(LAX_VM)............ $actvm"
else
	# 1st inspect the  lax.nl.current.vm.  As long as it is in the
	# valid vm list it takes precedence over everything else.  
	laxVMisValid="false"
	# is the lax current vm is specifies
	if [ ! -z "$abs_lax_nl_current_vm" -a -x "$abs_lax_nl_current_vm" ]; then
		# inspect it
		inspectVM "$abs_lax_nl_current_vm"
		eval laxVMtype="$inspectedVMtype"
		# if the type of this vm is in the valid list, deem it valid

		case "$validVMtypeList" in
			*$laxVMtype*)
				laxVMisValid="true"
			;;
		esac
	fi
	# if the lax current vm is valid use it
	 overwriteLaxVM="true"
	if [ "$laxVMisValid" = "true" ]; then
		# dont overwrite the lax.nl.current.vm  if this one works just fine
		overwriteLaxVM="false"
		actvm="$abs_lax_nl_current_vm"
		actvmType="$laxVMtype"
		debugOut "* Using VM.....(lax.nl.current.vm)...... $actvm"
	else	
	# other wise search the path
		debugOut "[1mWARNING! No valid lax.nl.current.vm available.[0m"
		# overwrite the lax.nl.current.vm  if the one in there didnt work
		overwriteLaxVM="true"

		# sift through the path to look for VMs

		# unique the PATH to limit the amount of work; see bug #6285.
		debugOut "$VM_SEARCH_PATH"
		uniquedPath=`echo $VM_SEARCH_PATH | tr ':' '\012'`

		vmNumber=0;
		OFS="$IFS"
		IFS=":"
		set x $uniquedPath; shift
		IFS="$OFS"
		debugOut "[1mSearching for VMs in PATH:[0m"
		for pathDir in $*; do
			debugOut "Looking in:............................. $pathDir"
			# For each type of binary vm name
			for binaryName in java jre oldjava; do

				vmPath="$pathDir/$binaryName"

				# if the binary exists, is executable and is not a directory...
				if [ -x "$vmPath" -a \( ! -d "$vmPath" \) ]; then
					debugOut "  Found VM:............................. $vmPath"
					inspectVM "$vmPath"
					# set up a Bourne-style array of VM props using var1, var2, etc...
					eval vmBinary$vmNumber="$inspectedVMpath"
					eval vmType$vmNumber="$inspectedVMtype"
					eval oldVMtype$vmNumber="$inspectedOldVMtype"
					vmNumber=`expr ${vmNumber:-0} + 1`
				fi
			done
		done
	
		#########################################
		# VERIFY VMS against valid types
		#
		actvmType=""
		vmHighNumber="$vmNumber"

		# for each type of valid VM
		for validType in $validVMtypeList; do
			vmNumber="0";

			# run through the list of VMs found
			while [ "$vmNumber" -lt $vmHighNumber ]; do
				eval type="$"vmType$vmNumber""
				eval oldType="$"oldVMtype$vmNumber""
				eval  bin="$"vmBinary$vmNumber""
		
				# if the type of this VM is of '$type' or '$oldType'
				# make it the actual vm (actvm) to use
				case "${type} ${oldType}" in
					*${validType}*)
		
						actvm="$bin"
						actvmType="$type"
						debugOut "[1m* Using VM:............................. $actvm[0m"
						break 2
					;;
				esac
				vmNumber=`expr ${vmNumber:-0} + 1`
			done
		done	
	fi
fi

# If no VMs are found in path
if [ -z "$actvm" ]
then
	echo "No Java virtual machine could be found from your PATH"
	echo "environment variable.  You must install a VM prior to"
	echo "running this program."
	
	# Mikey [5/16/2000] -- If this was SEA'd then remove the temp directory
	if [ "$IS_INSTALLER" = "true" ]; then
		debugOut "Removing temporary installation directory: \"$lax_user_dir\""
		rm -rf "$lax_user_dir"
	fi
	
	cd "$olddir"
	exit
fi

# noLaxBackup is true for self-extractor, and the current vm should not
# be changed if the LAX_VM tag is used
noLaxBackup=${noLaxBackup:="false"}
if [ "$overwriteLaxVM" = "true" -a "$lax_vm" != "LAX_VM" -a "$noLaxBackup" != "true" -a \
 -w "$propfname" ]
then
	sedscript="s;^lax.nl.current.vm.*;lax.nl.current.vm=$actvm;"
	sed $sedscript "$propfname">file.lax 
	mv "$propfname" "$propfname.bak" > /dev/null 2>&1
	mv file.lax "$propfname" > /dev/null 2>&1
	rm "$propfname.bak" > /dev/null 2>&1
fi

# set up a variable to esilty know if we are going to run 1.1 or 1.2 
# for setting up VM cmd line options later on
case "$actvmType" in
	"JRE" | "JDK" | "JRE_J1" | "JDK_J1" )
		actvmVersion="1.1"
	;;
	"R12" | "D12" | "JDK_J2" | "JRE_J2" | "OLDJAVA")
		actvmVersion="1.2"
	;;
	*)
		actvmVersion=""
	;;
esac

#
# end of finding VMs
##########################################################################################

####################################################################################
# Determining VM invocation options to use
#

#
# Verification
#
if [ "$actvmVersion" = "1.1" ]; then
	if [ "$verify" = "off" ]; then
		options="$options -noverify"
	else
		if [ "$verify_mode" = "remote" ]; then
			options="$options -verifyremote"
		elif [ "$verify_mode" = "none" ]; then
			options="$options -noverify"
		elif [ "$verify_mode" = "all" ]; then
			options="$options -verify"
		fi
	fi
fi

verbo=${verbo:="none"}
if [ $verbo = "normal" ]; then
	if [ "$actvmVersion" = "1.1" ]; then
		options="$options -verbose"
	elif [ "$actvmVersion" = "1.2" ]; then
		options="$options -verbose:class"
	fi
elif [ $verbo = "all" ]; then
	if [ "$actvmVersion" = "1.1" ]; then
		options="$options -verbose -verbosegc"
	elif [ "$actvmVersion" = "1.2" ]; then
		options="$options -verbose:class -verbose:gc"
	fi
elif [ $verbo = "gc" ]; then
	if [ "$actvmVersion" = "1.1" ]; then
		options="$options -verbosegc"
	elif [ "$actvmVersion" = "1.2" ]; then
		options="$options -verbose:gc"
	fi	
fi

#
# Memory mgnt
#
gcxtnt=${gcxtnt:="none"}
if [ $gcxtnt = "min" ]
then
	if [ "$actvmVersion" = "1.1" ]; then
		options="$options -noclassgc"
	elif [ "$actvmVersion" = "1.2" ]; then
		options="$options -Xnoclassgc"
	fi
fi

gcthrd=${gcthrd:="none"}
if [ "$actvmVersion" = "1.1" ]; then
	if [ $gcthrd = "off" ]
	then
		options="$options -noasyncgc"
	fi
fi


nsmax=${nsmax:="none"}
if [ "$nsmax" != "none" ]; then
        if [ "$actvmVersion" = "1.1" ]; then
                options="$options -ss$nsmax"
        elif [ "$actvmVersion" = "1.2" ]; then
                options="$options -Xss$nsmax"
        fi
fi

jsmax=${jsmax:="none"}
if [ "$jsmax" != "none" ]; then
        if [ "$actvmVersion" = "1.1" ]; then
                options="$options -oss$jsmax"
        elif [ "$actvmVersion" = "1.2" ]; then
                options="$options -Xoss$jsmax"
        fi
fi


jhmax=${jhmax:="none"}
if [ "$jhmax" != "none" ]; then
	if [ "$actvmVersion" = "1.1" ]; then
		options="$options -mx$jhmax"
	elif [ "$actvmVersion" = "1.2" ]; then
		options="$options -Xmx$jhmax"
	fi
fi

jhinit=${jhinit:="none"}
if [ "$jhinit" != "none" ]; then
	if [ "$actvmVersion" = "1.1" ]; then
		options="$options -ms$jhinit"
	elif [ "$actvmVersion" = "1.2" ]; then
		options="$options -Xms$jhinit"
	fi
fi

debug=${debug:-"off"}
if [ $debug != "off" ]; then
	if [ "$actvmVersion" = "1.1" ]; then
		options="$options -debug"
	elif [ "$actvmVersion" = "1.2" ]; then
		options="$options -Xdebug"
	fi
fi

###############################################################
# JIT options
# Resetting java home and JIT compiler environment variables
#
jitOnOrOff=on;
#
# turn off according to VM type
#
if   [ ! -z "$lax_nl_osname_JDK_J1_java_compiler" -a "$actvmType" = "JDK_J1" ]; then
	jitOnOrOff=$lax_nl_osname_JDK_J1_java_compiler
elif [ ! -z "$lax_nl_osname_JDK_J2_java_compiler" -a "$actvmType" = "JDK_J2" ]; then
	jitOnOrOff=$lax_nl_osname_JDK_J2_java_compiler
elif [ ! -z "$lax_nl_osname_JRE_J1_java_compiler" -a "$actvmType" = "JRE_J1" ]; then
	jitOnOrOff=$lax_nl_osname_JRE_J1_java_compiler
elif [ ! -z "$lax_nl_osname_JRE_J2_java_compiler" -a "$actvmType" = "JRE_J2" ]; then
	jitOnOrOff=$lax_nl_osname_JRE_J2_java_compler
elif [ ! -z "$lax_nl_osname_J1_java_compiler" -a "$actvmType" = "J1" ]; then
	jitOnOrOff=$lax_nl_osname_J1_java_compiler
elif [ ! -z "$lax_nl_osname_J2_java_compiler" -a "$actvmType" = "J2" ]; then
	jitOnOrOff=$lax_nl_osname_J2_java_compiler
elif [ ! -z "$lax_nl_osname_JRE_java_compiler" -a "$actvmType" = "JRE" ]; then
	jitOnOrOff=$lax_nl_osname_JRE_java_compiler
elif [ ! -z "$lax_nl_osname_JDK_java_compiler" -a "$actvmType" = "JDK" ]; then
	jitOnOrOff=$lax_nl_osname_JDK_java_compiler
elif [ ! -z "$lax_nl_osname_ALL_java_compiler" ]; then
	jitOnOrOff=$lax_nl_osname_ALL_java_compiler
#
elif [ ! -z "$lax_nl_unix_JDK_J1_java_compiler" -a "$actvmType" = "JDK_J1" ]; then
	jitOnOrOff=$lax_nl_unix_JDK_J1_java_compiler
elif [ ! -z "$lax_nl_unix_JDK_J2_java_compiler" -a "$actvmType" = "JDK_J2" ]; then
	jitOnOrOff=$lax_nl_unix_JDK_J2_java_compiler
elif [ ! -z "$lax_nl_unix_JRE_J1_java_compiler" -a "$actvmType" = "JRE_J1" ]; then
	jitOnOrOff=$lax_nl_unix_JRE_J1_java_compiler
elif [ ! -z "$lax_nl_unix_JRE_J2_java_compiler" -a "$actvmType" = "JRE_J2" ]; then
	jitOnOrOff=$lax_nl_unix_JRE_J2_java_compler
elif [ ! -z "$lax_nl_unix_J1_java_compiler" -a "$actvmType" = "J1" ]; then
	jitOnOrOff=$lax_nl_unix_J1_java_compiler
elif [ ! -z "$lax_nl_unix_J2_java_compiler" -a "$actvmType" = "J2" ]; then
	jitOnOrOff=$lax_nl_unix_J2_java_compiler
elif [ ! -z "$lax_nl_unix_JRE_java_compiler" -a "$actvmType" = "JRE" ]; then
	jitOnOrOff=$lax_nl_unix_JRE_java_compiler
elif [ ! -z "$lax_nl_unix_JDK_java_compiler" -a "$actvmType" = "JDK" ]; then
	jitOnOrOff=$lax_nl_unix_JDK_java_compiler
elif [ ! -z "$lax_nl_unix_ALL_java_compiler" ]; then
	jitOnOrOff=$lax_nl_unix_ALL_java_compiler
#
elif [ ! -z "$lax_nl_JDK_J1_java_compiler" -a "$actvmType" = "JDK_J1" ]; then
	jitOnOrOff=$lax_nl_JDK_J1_java_compiler
elif [ ! -z "$lax_nl_JDK_J2_java_compiler" -a "$actvmType" = "JDK_J2" ]; then
	jitOnOrOff=$lax_nl_JDK_J2_java_compiler
elif [ ! -z "$lax_nl_JRE_J1_java_compiler" -a "$actvmType" = "JRE_J1" ]; then
	jitOnOrOff=$lax_nl_JRE_J1_java_compiler
elif [ ! -z "$lax_nl_JRE_J2_java_compiler" -a "$actvmType" = "JRE_J2" ]; then
	jitOnOrOff=$lax_nl_JRE_J2_java_compler
elif [ ! -z "$lax_nl_J1_java_compiler" -a "$actvmType" = "J1" ]; then
	jitOnOrOff=$lax_nl_J1_java_compiler
elif [ ! -z "$lax_nl_J2_java_compiler" -a "$actvmType" = "J2" ]; then
	jitOnOrOff=$lax_nl_J2_java_compiler
elif [ ! -z "$lax_nl_JRE_java_compiler" -a "$actvmType" = "JRE" ]; then
	jitOnOrOff=$lax_nl_JRE_java_compiler
elif [ ! -z "$lax_nl_JDK_java_compiler" -a "$actvmType" = "JDK" ]; then
	jitOnOrOff=$lax_nl_JDK_java_compiler
elif [ ! -z "$lax_nl_ALL_java_compiler" ]; then
	jitOnOrOff=$lax_nl_ALL_java_compiler
#
elif [ ! -z "$lax_nl_osname_java_compiler" ]; then
	jitOnOrOff=$lax_nl_osname_java_compiler
elif [ ! -z "$lax_nl_java_compiler" ]; then
	jitOnOrOff=$lax_nl_java_compiler
else
	jitOnOrOff=on
fi

# JIT is ON by default, so we only need to change its status
# the above else-if lists figures it should be OFF
if [ "$jitOnOrOff" = "off" ]; then
	if [ "$actvmVersion" = "1.1" ]; then
		case "$osName" in
			*irix*)
				jitinvoc="-nojit"
				JIT_OPTIONS="-nojit"
				export JIT_OPTIONS
			;;
			*hp-ux*|*hpux*)
				JIT_OPTIONS="-nojit"
				export JIT_OPTIONS
				jitinvoc="-nojit"
			;;
			*solaris*|*sunos*)
				jitinvoc="-Djava.compiler="
			;;
			*aix*)
				JAVA_COMPILER=off
				export JAVA_COMPILER
			;;
			*freebsd*)
				jitinvoc="-Djava.compiler="
			;;
			*linux*)
				jitinvoc="-Djava.compiler="
			;;
			*rhapsody*|*macos*)
			;;
			*compaq*|*dg*|*osf*)
				jitinvoc="-nojit"
			;;
			*)
				debugOut "Unknown OS name (\"$osName\"). Cannot set JIT Options."
			;;
		esac
	elif [ "$actvmVersion" = "1.2" ]; then
		jitinvoc="-Djava.compiler=NONE"
	else
		debugOut "Unknown VM version. Cannot set JIT Options."
	fi
fi

options="$jitinvoc $options"

# set this variable to something so we're guaranteed a value
linux_LD_ASSUME_KERNEL_hack=0;

# work around problem on RedHat Linux 7.1 IA-32
# see Bug Id 4447270 at Sun JDC bug parade
if [ `cat /etc/redhat-release 2>/dev/null | grep "7\.1" | wc -l` = "1" ];
then
    if [ `uname -s` = "Linux" ];
    then
        if [ `uname -m` != "ia64" ];
        then
            case `uname -r` in
            2.[456]*)
								linux_LD_ASSUME_KERNEL_hack=1
                ;;
            esac
        fi
    fi
fi

# LD_ASSUME_KERNEL for Native POSIX Threading Library on some Linux distros
if [ `uname` = "Linux" ]; then
	debugOut "checking for NPTL + JVM vulernability..."
	#check libc to see if it was compiled with NPTL
	nptl="`strings /lib/libc.so.6 | grep -i nptl`"
	if [ "$nptl" ]; then
		debugOut "NPTL detected! checking for vulnerable JVM....";
		
		# I have to set this before I check the JVM version, a-cuz
		# the call will hang, if it -is- vulnerable!
		export LD_ASSUME_KERNEL=2.2.5
		
		eval `$actvm -version 2>&1 | $AWK '
			BEGIN {
				vendor="Sun"
			}
			/"[0-9]\.[0-9]\.[0-9][^"]*"$/ {
				gsub ("[\"]", "", $3)
				split ($3, ver, "[\._-]")
				printf "v_major=%s\nv_minor=%s\nv_patch=%s\n",ver[1],ver[2],ver[3]
			}
			/IBM/ {
				vendor="IBM"
			}
			END {
				printf "v_vendor=%s\n",vendor
			}
		' `

		# unset the LD_ASSUME_KERNEL in cause we don't need it
		unset LD_ASSUME_KERNEL

		debugOut "major : ${v_major}"
		debugOut "minor : ${v_minor}"
		debugOut "patch : ${v_patch}"
		debugOut "vendor: ${v_vendor}"
		
		# check our rules for setting LD_ASSUME_KERNEL
		# currently, we're only setting this for JVMS < 1.4
		# we can add more rules later, if we need to.
		if [ ${v_minor:-0} -lt 4 ]; then
			debugOut "Vulnerable JVM detected... implementing workaround"
			linux_LD_ASSUME_KERNEL_hack=1
		else
			debugOut "Your JVM is OK! Congratulations!"
		fi
	fi
fi

if [ $linux_LD_ASSUME_KERNEL_hack -eq 1 ]; then
	LD_ASSUME_KERNEL=2.2.5
	export LD_ASSUME_KERNEL
fi

##################################################################################
# LAUNCH VM

# Passing in addtional stuff
options="$options $lax_nl_java_option_additional"


# Changing working directory
if [ ! "$lax_user_dir" = "" ]
then
	if [ ! "$lax_user_dir" = "." ];
	then
		cd "$lax_user_dir"
	fi
else
	cd "$olddir"
fi

# Optional printout of all variable values for debugging purposes

debugOut ""
debugOut "[7m========= Virtual Machine Options ====================================[0m"
debugOut "LAX properties incorporated............. OK."
debugOut "classpath............................... \"$lax_class_path\""
debugOut "main class.............................. \"$lax_main_class\""
debugOut ".lax file path.......................... \"$propfname\""
debugOut "user directory.......................... \"$lax_user_dir\""
debugOut "stdout to............................... \"$lax_stdout_redirect\""
debugOut "sterr to................................ \"$lax_stderr_redirect\""
debugOut "install directory....................... \"$lax_dir\""
debugOut "JIT..................................... ${jittype:-"none"}"
debugOut "option (verify)......................... ${verify:-"none"}"
debugOut "option (verbosity)...................... ${verbo:-"none"}"
debugOut "option (garbage collection extent)...... ${gcxtnt:-"none"}"
debugOut "option (garbage collection thread)...... ${gcthrd:-"none"}"
debugOut "option (native stack max size).......... ${nsmax:-"none"}"
debugOut "option (java stack max size)............ ${jsmax:-"none"}"
debugOut "option (java heap max size)............. ${jhmax:-"none"}"
debugOut "option (java heap initial size)......... ${jhinit:-"none"}"
debugOut "option (lax.nl.java.option.additional).. ${lax_nl_java_option_additional:-"none"}"
resolveLink "$actvm"
actvm="$resolvedLink"

actvmBinaryName=`basename "$actvm"`
# get dirname of binary
actvmHome=`dirname "$actvm"`
# is the dir the binary is in named "bin"?
if [ "`basename "$actvmHome"`" = "bin" ]; then
	# if so then the dir above bin is the java home
	JAVA_HOME=`dirname "$actvmHome"`
else
	JAVA_HOME=
fi

# Making $JAVA_HOME available to the application.
export JAVA_HOME

# [RW] reset the locale that what we remember it to be (see use.sh line 22)
if [ "$IS_INSTALLER" = "true" ]; then
	if [ "X$OLD_LANG" = X ]
	then
	 	# no locale was defined prior to running this program
		unset LANG
	else
		# there was a locale: revert back to it
		LANG="$OLD_LANG"
	fi
fi

###########################################################################
# tlb 2001-09-18
# Moving the checking for the DISPLAY variable down here as there are  
# options in the LAX that might override the need for checking the DISPLAY.
# Those options need loading before the check is performed.
# Also making sure we don't report an error when running on Mac OS X.


debugOut ""
debugOut "[7m========= Display settings ===========================================[0m"
#
# check the display
#
isRemoteDisplay="false"
if [ "$IS_INSTALLER" = "true" -a "$isConsole" = "false" -a "$isSilent" = "false" -a ! "$osName" = "darwin" ]; then
	hostname=`hostname`
	isRemoteDisplay="true"
	for display in ${hostname}:0 ${hostname}:0.0 localhost:0 localhost:0.0 unix:0 unix:0.0 :0 :0.0
	do
		if [ "$DISPLAY" = "$display" ]; then
			isRemoteDisplay="false";
		fi
	done
fi

xDisp="local"
if [ "$isRemoteDisplay" = "true" ]; then
	xDisp="remote"
fi
if [  -z "$DISPLAY" ]; then
	xDisp="not set"
fi
debugOut "X display............................... $xDisp"


if [ -z "$DISPLAY" -a "$uimode" = "gui" ]; then
	debugOut "[1mWARNING:  This shell's DISPLAY variable has not been set."
	debugOut "This installer is  configured to run in GUI and will probably"
	debugOut "fail.  Try running this  installer in console or silent mode,"
	debugOut "or on another  UNIX  host which has the DISPLAY variable set,"
	debugOut "if the installer unexpectedly fails.[0m"
else
	if [ "$isRemoteDisplay" = "true" -a "$uimode" = "gui" ]; then
		debugOut "[1mWARNING:  The name  of  this  host ($hostname) and  the setting"
		debugOut "of this  shell's DISPLAY ($DISPLAY) variable do not match."
		debugOut "If this launcher is being displayed to a Microsoft Windows desktop"
		debugOut "through X Windows the Java Virtual Machine might abort. Try running"
		debugOut "this installer locally on the target system or through X Windows to"
		debugOut "another UNIX host if the installer unexpectedly fails.[0m"
	fi
fi

debugOut "UI mode................................. $uimode"


# COMMENT ME TO REMOVE OUTPUT FROM NORMAL INSTALLER EXECUTION
if [ "$IS_INSTALLER" = "true" ]; then
	echo ""
	echo "Launching installer..."
	echo ""
fi

# MMA - clear ENV to address a problem where the shell initialization
# file (.Xshrc) pointed to by ENV may overide the classpath we have just set,
# causing the app to fail.  Drawback is that other environment variables set
# in the init file will not be available in the environment (they will be
# available as Java system properties, however).  Comment out the two lines
# below to change this behavior.
ENV=
export ENV
# I split these up so they would be a bit clearer on the screen.

#debugOut ""
#debugOut "[7m========= VM Command Line ============================================[0m"
#debugOut "CLASSPATH=$lax_class_path"
#debugOut "[1m\"$actvm\" $options $lax_nl_java_launcher_main_class \"$propfname\" \"$envPropertiesFile\" $cmdLineArgs[0m"
#debugOut "[1m$command[0m"
# Here is where we actually run the app in Java:

CLASSPATH="$lax_class_path:$CLASSPATH"; export CLASSPATH
debugOut "[7mCLASSPATH:[0m$CLASSPATH"

if [ "`echo $actvm | grep 'jre$'`" ]; then
	cpArg="-cp"
fi

debugOut ""
unset POSIXLY_CORRECT
if [ $DO_NOT_FORK ]
then
	debugOut "[7m========= Executing JAVA =============================================[0m"
	# this is the original, it's still here for copy/paste purposes
	#eval \"$actvm\" $options $lax_nl_java_launcher_main_class \"$propfname\" \"$envPropertiesFile\" $cmdLineArgs
	
	lax_class_path=\"$lax_class_path\"
	if [ $cpArg ]; then
		command="\"$actvm\" $options $cpArg \"$CLASSPATH\" $lax_nl_java_launcher_main_class \"$propfname\" \"$envPropertiesFile\""
	else
		command="\"$actvm\" $options $lax_nl_java_launcher_main_class \"$propfname\" \"$envPropertiesFile\""
	fi
	eval $command $cmdLineArgs
else
	debugOut "[7m========= Forking JAVA =============================================[0m"
	if [ $cpArg  ]; then
		exec "$actvm" $options $cpArg "$CLASSPATH" $lax_nl_java_launcher_main_class "$propfname" "$envPropertiesFile" $cmdLineArgs
	else
		exec "$actvm" $options $lax_nl_java_launcher_main_class "$propfname" "$envPropertiesFile" $cmdLineArgs
	fi
fi
exitValue=$?
debugOut "[7m========= JAVA Finished ==============================================[0m"
debugOut ""

#  Change back to directory used priory to this script running.

cd "$olddir"

exit $exitValue
