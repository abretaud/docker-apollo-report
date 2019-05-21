#!/bin/bash
set -e

function run_scripts () {
	SCRIPTS_DIR="/scripts/$1.d"
	SCRIPT_FILES_PATTERN="^${SCRIPTS_DIR}/[0-9][0-9][a-zA-Z0-9_-]+$"
	SCRIPTS=$(find "$SCRIPTS_DIR" -type f -uid 0 -executable -regex "$SCRIPT_FILES_PATTERN" | sort)
	if [ -n "$SCRIPTS" ] ; then
		echo "=>> $1-scripts:"
	    for script in $SCRIPTS ; do
	        echo "=> $script"
			. "$script"
	    done
	fi
}

: ${APOLLO_EXT_URL:='$APOLLO_URL'}

export APOLLO_USER APOLLO_PASS ANNOTATION_GROUPS SPLIT_USERS APOLLO_MOUNTPOINT
echo -e "export APOLLO_USER=${APOLLO_USER} APOLLO_PASS=${APOLLO_PASS} ANNOTATION_GROUPS=${ANNOTATION_GROUPS} SPLIT_USERS=${SPLIT_USERS} APOLLO_MOUNTPOINT=${APOLLO_MOUNTPOINT}" >> /etc/profile
echo -e "export APOLLO_USER=${APOLLO_USER} APOLLO_PASS=${APOLLO_PASS} ANNOTATION_GROUPS=${ANNOTATION_GROUPS} SPLIT_USERS=${SPLIT_USERS} APOLLO_MOUNTPOINT=${APOLLO_MOUNTPOINT}" >> /etc/bash.bashrc

run_scripts pre-launch

exec apache2-foreground

exit 1
