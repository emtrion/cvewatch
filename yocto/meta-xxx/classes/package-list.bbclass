inherit cve-check

PACKAGE_FILE ?= "${DEPLOY_DIR_IMAGE}/yocto_packages.csv"

python do_package_check () {
    file = d.getVar('PACKAGE_FILE')

    # if no CVE_PRODUCT exists, we flag it with NONE
    if not d.getVar('CVE_PRODUCT'):
        cve_product = 'CVE_PRODUCT_NONE'
    else:
        cve_product = d.getVar('CVE_PRODUCT')

    # if no cve patches exist, we flag it with NONE
    patched_cves = get_patches_cves(d)
    if len(patched_cves) == 0:
        patched_cves = 'PATCHED_CVES_NONE'
    else:
        patched_cves = str(patched_cves)

    # if no cves exist on the whitelist, we flag it with NONE
    if not d.getVar('CVE_CHECK_WHITELIST'):
        cve_whitelist = 'CVE_CHECK_WHITELIST_NONE'
    else:
        cve_whitelist = str(d.getVar('CVE_CHECK_WHITELIST').split())

    if not os.path.exists(d.getVar('DEPLOY_DIR_IMAGE')):
        os.makedirs(d.getVar('DEPLOY_DIR_IMAGE'))

    with open(file, 'a') as f:
        f.write(d.getVar('BPN') + ";" + cve_product + ";" + d.getVar('CVE_VERSION') + ";" + cve_whitelist + ";" + patched_cves + '\n')
}

addtask package_check before do_build
do_package_check[depends] = "delete-package-file:do_rm"
do_package_check[nostamp] = "1"
