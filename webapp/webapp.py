import sys
import syslog
import utils
from yocto import Yocto

syslog.syslog('cvewatch: Start check for CVEs')

os = sys.argv[1]
project_id = sys.argv[2]

if os == "Debian":
    syslog.syslog('cvewatch: Checking Debian packages')
    # convert debian elbe xml to database and check for vulnerabilities
    utils.add_elbe_xml(project_id)
elif os == "Yocto":
    syslog.syslog('cvewatch: Checking Yocto packages')
    # check packages for vulnerabilities
    y = Yocto()
    y.do_check(project_id)

# set status to successfully finished
utils.setStatus(project_id, "Finished successfully")

# finished successfully
syslog.syslog('cvewatch: Check finished successfully')
sys.exit(0)
