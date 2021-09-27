import json
import os.path
import apt_pkg
import utils
import syslog
import constant
from database import Database
from mail import Mail
from update import Update


class Deb:
    def get_unpatched_cves(self, package_name, version, distribution):
        unpatched_cves = []
        apt_pkg.init_system()

        if os.path.isfile(constant.DOWNLOAD_PATH + constant.DEBIAN_CVE_FILE):
            with open(constant.DOWNLOAD_PATH + constant.DEBIAN_CVE_FILE) as json_file:
                data = json.load(json_file)
        else:
            u = Update()
            u.debian_db()
        for a, b in data.items():
            if a == package_name:
                for c, d in b.items():
                    if distribution in d["releases"]:
                        if "fixed_version" in d["releases"][distribution]:
                            if "fixed_version" == "0":
                                # we ignore this case, as it's not relevant
                                pass
                            else:
                                vc = apt_pkg.version_compare(d["releases"][distribution]["fixed_version"], version)
                                if vc > 0:
                                    unpatched_cves.append(c)
                return unpatched_cves

    def do_check(self, project_id):
        db = Database()
        c = db.connect()

        sql = "SELECT debian_package_name, version, distribution " \
              "FROM debian_package " \
              "WHERE project_id = '%s'" % project_id
        packages = db.read_all_records(c, sql)

        # for each Package and version, check for vulnerability
        for i in packages:
            self.check_package(i["debian_package_name"], i["version"], i["distribution"], project_id)

    def check_package(self, package_name, version, distribution, project_id):
        m = Mail()
        db = Database()
        c = db.connect()

        syslog.syslog(syslog.LOG_INFO, "cvewatch: check package " + package_name)

        # get all unpatched cves for current Package
        unpatched_cves = self.get_unpatched_cves(package_name, version, distribution)

        if unpatched_cves:
            # check if there already is an entry for this package and version
            sql = "SELECT * " \
                  "FROM debian_package " \
                  "WHERE debian_package_name = '%s' " \
                  "AND version = '%s'" \
                  "AND project_id = '%s' " % (package_name, version, project_id)
            result = db.read_single_record(c, sql)

            # if package is not yet in database, create one
            if not result:
                sql = "INSERT INTO debian_package " \
                      "(debian_package_name, version, distribution, project_id, is_vulnerable) " \
                      "VALUES ('%s', '%s', '%s', %s, %s)" \
                      % (package_name, version, distribution, project_id, "true")
                db.create_record(c, sql)

                # create cve entries
                for cve in unpatched_cves:
                    link = "https://nvd.nist.gov/vuln/detail/" + cve
                    # check if there already is an entry for this cve
                    sql = "SELECT cve_id " \
                          "FROM debian_cve " \
                          "WHERE cve_id = '%s'" % cve
                    result = db.read_single_record(c, sql)
                    if not result:
                        sql = "INSERT INTO debian_cve " \
                              "(cve_id, summary, scorev2, scorev3, link) " \
                              "VALUES ('%s', '%s', '%s', '%s', '%s')" % (cve, '', '', '', link)
                        db.create_record(c, sql)

                    # find out debian_package_id of debian Package
                    sql = "SELECT id " \
                          "FROM debian_package " \
                          "WHERE debian_package_name = '%s' " \
                          "AND version = '%s' " \
                          "AND distribution = '%s' " \
                          "AND project_id = '%s'" % (package_name, version, distribution, project_id)
                    debian_package_id = db.read_single_record(c, sql)

                    # find out cve_id of cve
                    cve_id = utils.get_cve_id(cve)

                    # create debian_package_cve entries
                    sql = "INSERT INTO debian_package_cve (debian_package_id, cve_id) " \
                          "VALUES ('%s', '%s')" % (debian_package_id["id"], cve_id["id"])
                    db.create_record(c, sql)

                # as this entry is the first one, send a mail
                recipient = utils.getRecipient(project_id)
                subject = "[emCVE-Watch: " + recipient["email"] + "] %s %s has unpatched CVE(s)" % (
                    package_name, version)
                body = "%s %s has unpatched CVE(s): \n\n" % (package_name, version)
                for i in unpatched_cves:
                    link = "https://security-tracker.debian.org/tracker/" + i
                    body += link + '\n'
                recipient = utils.getRecipient(recipient["email"])
                m.send_mail(recipient, subject, body)

                # mark package as vulnerable
                utils.setVulnerable("Debian", project_id, package_name, version)

            # if there already is an entry, check if there is a new cve
            else:
                sql = "SELECT debian_cve.cve_id " \
                      "FROM debian_cve " \
                      "INNER JOIN debian_package_cve " \
                      "ON debian_cve.id = debian_package_cve.cve_id " \
                      "INNER JOIN debian_package " \
                      "ON debian_package.id = debian_package_cve.debian_package_id " \
                      "WHERE debian_package_name = '%s' " \
                      "AND version = '%s' " \
                      "AND project_id = '%s' " % (package_name, version, project_id)
                # get all cve entries for the Package/version
                known_cve = [d['cve_id'] for d in db.read_all_records(c, sql)]
                # let's see if we have new unpatched cves
                new_cve = [x for x in unpatched_cves if x not in known_cve]
                if new_cve:
                    # create cve entries
                    for cve in new_cve:
                        link = "https://nvd.nist.gov/vuln/detail/" + cve
                        sql = "INSERT INTO debian_cve (cve_id, summary, scorev2, scorev3, link) " \
                              "VALUES ('%s', '%s', '%s', '%s', '%s')" % (cve, '', '', '', link)
                        db.create_record(c, sql)

                        # find out debian_package_id of debian Package
                        sql = "SELECT id " \
                              "FROM debian_package " \
                              "WHERE debian_package_name = '%s' " \
                              "AND version = '%s' " \
                              "AND distribution = '%s' " \
                              "AND project_id = '%s'" % (package_name, version, distribution, project_id)
                        debian_package_id = db.read_single_record(c, sql)

                        # find out cve_id of cve
                        cve_id = utils.get_cve_id(cve)

                        # create debian_package_cve entries
                        sql = "INSERT INTO debian_package_cve (debian_package_id, cve_id) " \
                              "VALUES ('%s', '%s')" % (debian_package_id["id"], cve_id["id"])
                        db.create_record(c, sql)

                    # send a mail
                    name = utils.get_project_name(project_id)
                    subject = "[emCVE-Watch: " + name["project_name"] + "] %s %s has unpatched CVE(s)" % (
                        package_name, version)
                    body = "%s %s has unpatched CVE(s): \n\n" % (package_name, version)
                    for i in new_cve:
                        link = "https://security-tracker.debian.org/tracker/" + i
                        body += link + '\n'
                    recipient = utils.getRecipient(project_id)
                    m.send_mail(recipient["email"], subject, body)

                    # mark package as vulnerable
                    utils.setVulnerable("Debian", project_id, package_name, version)
