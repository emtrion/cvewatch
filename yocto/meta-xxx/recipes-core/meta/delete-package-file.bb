SUMMARY = "Delete yocto_packages.csv file on each new build"
LICENSE = "MIT"

INHIBIT_DEFAULT_DEPS = "1"

inherit native

deltask do_unpack
deltask do_patch
deltask do_configure
deltask do_compile
deltask do_install
deltask do_populate_sysroot

PACKAGE_FILE ?= "${DEPLOY_DIR_IMAGE}/yocto_packages.csv"

python do_rm () {
    if os.path.exists(d.getVar('PACKAGE_FILE')):
        bb.utils.remove(d.getVar('PACKAGE_FILE'))
}

addtask rm before do_fetch
do_rm[nostamp] = "1"

EXCLUDE_FROM_WORLD = "1"

