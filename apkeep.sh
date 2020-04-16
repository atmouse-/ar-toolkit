#!/bin/bash


TEMP_DIR=/tmp/androidkeep_tmp
mkdir -p $TEMP_DIR
PKGLIST=`pwd`/pkglist
PKGLIST_INSTALLED=$TEMP_DIR/pkglist_installed
PKGSAVE=/mnt/backup/android_backup
mkdir -p $PKGSAVE/data/data
mkdir -p $PKGSAVE/sdcard/Android/obb

function is_adb_root() {
	_ID=$(/usr/bin/adb </dev/null shell id -u)
	[ $_ID -eq 0 ] && return 0
	return 1
}

function get_package_all() {
	/usr/bin/adb </dev/null shell pm list packages >$PKGLIST_INSTALLED
}

function is_package_exist() {
	cat $PKGLIST_INSTALLED | grep $1
}

function get_package_uid() {
	/usr/bin/adb </dev/null shell dumpsys package $1 | grep userId | awk -F= '{print $2}'
}

function pkg_clean_data() {
	if [ x"$1" = "x" ];then
		echo "arguments error" >&2
		exit 1
	fi
	/usr/bin/adb </dev/null shell rm -rf /data/data/$1
	/usr/bin/adb </dev/null shell rm -rf /sdcard/Android/data/$1
	/usr/bin/adb </dev/null shell rm -rf /sdcard/Android/obb/$1
}

function pkg_restore() {
	if [ x"$1" = "x" ];then
		echo "arguments error" >&2
		exit 1
	fi
	is_package_exist $1 || return 1
	_ID=$(get_package_uid $1)
	_ID_CACHE=$(expr $_ID + 10000)
	pkg_clean_data $1
	/usr/bin/adb </dev/null push $PKGSAVE/data/data/$1 /data/data/$1
	/usr/bin/adb </dev/null shell rm -rf /data/data/$1/cache
	/usr/bin/adb </dev/null shell rm -rf /data/data/$1/code_cache
	/usr/bin/adb </dev/null push $PKGSAVE/sdcard/Android/data/$1 /sdcard/Android/data/$1
	/usr/bin/adb </dev/null push $PKGSAVE/sdcard/Android/obb/$1 /sdcard/Android/obb/$1
	/usr/bin/adb </dev/null shell chown -R $_ID:$_ID /data/data/$1
	#/usr/bin/adb </dev/null shell chown -R $_ID:$_ID_CACHE /data/data/$1/cache
	#/usr/bin/adb </dev/null shell chown -R $_ID:$_ID_CACHE /data/data/$1/code_cache
	/usr/bin/adb </dev/null shell chmod -R o-rw /data/data/$1
	#/usr/bin/adb </dev/null shell chmod g+s /data/data/$1/cache
	#/usr/bin/adb </dev/null shell chmod g+s /data/data/$1/code_cache
	/usr/bin/adb </dev/null shell chmod -R og-rwx /data/data/$1/app_webview
	/usr/bin/adb </dev/null shell chown -R $_ID:sdcard_rw /sdcard/Android/data/$1
	/usr/bin/adb </dev/null shell chown -R $_ID:sdcard_rw /sdcard/Android/obb/$1
	/usr/bin/adb </dev/null shell chmod -R og-rw /sdcard/Android/data/$1
	/usr/bin/adb </dev/null shell chmod -R og-rw /sdcard/Android/obb/$1
	/usr/bin/adb </dev/null shell restorecon -Rv /data/data/$1
	/usr/bin/adb </dev/null shell restorecon -Rv /sdcard/Android/data/$1
	/usr/bin/adb </dev/null shell restorecon -Rv /sdcard/Android/obb/$1
	return 0
}

function pkg_save() {
	[ -e $PKGSAVE/data/data/$1 ] && return 1
	/usr/bin/adb </dev/null pull -a /data/data/$1 $PKGSAVE/data/data/$1
	/usr/bin/adb </dev/null pull -a /sdcard/Android/data/$1 $PKGSAVE/sdcard/Android/data/$1
	/usr/bin/adb </dev/null pull -a /sdcard/Android/obb/$1 $PKGSAVE/sdcard/Android/obb/$1
}

function pkg_compare_all() {
	get_package_all
	cat $PKGLIST | while read line
	do
		is_package_exist $line >/dev/null 2>&1
		if [ $? -ne 0 ]
		then
			echo "$line not exist" >&2
		fi
	done
}

function pkg_restore_all() {
	cat $PKGLIST | while read xline
	do
		pkg_restore $xline
	done
}

function pkg_save_all() {
	cat $PKGLIST | while read xline
	do
		pkg_save $xline
	done
}

case $1 in
	compare)
		is_adb_root || exit 13
		[ -e $PKGLIST ] || exit 2
		pkg_compare_all
		;;
	restore)
		is_adb_root || exit 13
		[ -e $PKGLIST ] || exit 2
		pkg_restore_all
		;;
	save)
		is_adb_root || exit 13
		[ -e $PKGLIST ] || exit 2
		pkg_save_all
		;;
	*)
		echo "Usage:" >&2
		echo "    $0 compare		check if package not exist in android os" >&2
		echo "    $0 restore		restore backup app data into android os" >&2
		echo "    $0 save		backup android apps to current pc" >&2
		echo "" >&2
		echo "Important: need default pkglist file contain appname" >&2
		echo "Important: edit PKGSAVE var before you start" >&2
		;;
esac
