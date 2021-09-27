import syslog
import utils
from update import Update
from deb import Deb
from yocto import Yocto

# Update CVE databases
u = Update()

syslog.syslog('cvewatch: Updating Debian CVE database')
u.debian_db()

syslog.syslog('cvewatch: Updating Yocto CVE database')
u.yocto_db()

# Run CVE check for every project
projects = utils.get_all_projects()

for p in projects:
    syslog.syslog('cvewatch: Checking project for new CVEs')
    if p["operating_system"] == "Debian":
        d = Deb()
        d.do_check(p["id"])
    else:
        y = Yocto()
        y.do_check(p["id"])
