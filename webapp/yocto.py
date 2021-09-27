import os
import sqlite3
import utils
import constant
from update import Update
from database import Database
from mail import Mail
from distutils.version import LooseVersion


class Yocto:
    def do_check(self, project_id):
        db = Database()
        c = db.connect()

        # if cve db does not exist yet, download it
        if not os.path.isfile(constant.DOWNLOAD_PATH + constant.YOCTO_CVE_DB):
            u = Update()
            u.yocto_db()

        sql = "SELECT uploaded_file " \
              "FROM project " \
              "WHERE id = '%s'" % project_id
        file_name = db.read_single_record(c, sql)

        sql = "SELECT users_id " \
              "FROM project " \
              "WHERE id = '%s'" % project_id
        user_id = db.read_single_record(c, sql)

        # Parse the packages in the CSV file
        result = utils.get_project_name(project_id)
        f = constant.UPLOAD_PATH + str(user_id["users_id"]) + "/" + result["project_name"] + "/" + str(
            file_name["uploaded_file"])

        lines = sorted(set(open(f, 'r').readlines()))
        packages = []

        for line in lines:
            packages.append(line.rstrip().split(';'))

        for i in packages[:]:
            if ' ' in i[1]:
                i[1] = i[1].split(' ')[0]
            i[2] = i[2].split('+')[0]

        # call check_cves()
        for i in packages:
            if i[1] == 'CVE_PRODUCT_NONE':
                # if there is no CVE_PRODUCT, skip the package
                continue
            else:
                p = i[1]

            if i[3] == 'CVE_CHECK_WHITELIST_NONE':
                i[3] = ''

            if i[4] == 'PATCHED_CVES_NONE':
                i[4] = set()
            else:
                i[4] = i[4].replace('{', '').replace('}', '').replace("'", '')
                i[4] = [k.strip() for k in i[4].split(',')]
                i[4] = set(i[4])

            patched, unpatched = self.check_cves(p, i[2], i[3], i[4])

            if patched or unpatched:
                cve_data = self.get_cve_info(patched + unpatched)
                self.cve_write_data(p, i[2], patched, cve_data, project_id)

    def check_cves(self, p, pv, whitelist, patched_cves):
        cves_unpatched = []
        # CVE_PRODUCT can contain more than one product (eg. curl/libcurl)
        products = p.split()
        # If this has been unset then we're not scanning for CVEs here (for example, image recipes)
        if not products:
            return [], []

        db_file = constant.DOWNLOAD_PATH + constant.YOCTO_CVE_DB
        conn = sqlite3.connect(db_file, uri=True)

        # For each of the known product names (e.g. curl has CPEs using curl and libcurl)...
        for product in products:
            if ":" in product:
                vendor, product = product.split(":", 1)
            else:
                vendor = "%"

            # Find all relevant CVE IDs.
            for cverow in conn.execute("SELECT DISTINCT ID FROM PRODUCTS WHERE PRODUCT IS ? AND VENDOR LIKE ?",
                                       (product, vendor)):
                cve = cverow[0]

                if cve in whitelist:
                    # TODO: this should be in the report as 'whitelisted'
                    patched_cves.add(cve)
                    continue
                elif cve in patched_cves:
                    continue

                vulnerable = False
                for row in conn.execute("SELECT * FROM PRODUCTS WHERE ID IS ? AND PRODUCT IS ? AND VENDOR LIKE ?",
                                        (cve, product, vendor)):
                    (_, _, _, version_start, operator_start, version_end, operator_end) = row

                    if (operator_start == '=' and pv == version_start) or version_start == '-':
                        vulnerable = True
                    else:
                        if operator_start:
                            try:
                                vulnerable_start = (
                                        operator_start == '>=' and LooseVersion(pv) >= LooseVersion(version_start))
                                vulnerable_start |= (
                                        operator_start == '>' and LooseVersion(pv) > LooseVersion(version_start))
                            except:
                                vulnerable_start = False
                        else:
                            vulnerable_start = False

                        if operator_end:
                            try:
                                vulnerable_end = (
                                        operator_end == '<=' and LooseVersion(pv) <= LooseVersion(version_end))
                                vulnerable_end |= (operator_end == '<' and LooseVersion(pv) < LooseVersion(version_end))
                            except:
                                vulnerable_end = False
                        else:
                            vulnerable_end = False

                        if operator_start and operator_end:
                            vulnerable = vulnerable_start and vulnerable_end
                        else:
                            vulnerable = vulnerable_start or vulnerable_end

                    if vulnerable:
                        cves_unpatched.append(cve)
                        break

                if not vulnerable:
                    # TODO: not patched but not vulnerable
                    patched_cves.add(cve)

        conn.close()

        return list(patched_cves), cves_unpatched

    def get_cve_info(self, cves):
        cve_data = {}
        db_file = constant.DOWNLOAD_PATH + constant.YOCTO_CVE_DB
        conn = sqlite3.connect(db_file, uri=True)

        for cve in cves:
            for row in conn.execute("SELECT * FROM NVD WHERE ID IS ?", (cve,)):
                cve_data[row[0]] = {}
                cve_data[row[0]]["summary"] = row[1]
                cve_data[row[0]]["scorev2"] = row[2]
                cve_data[row[0]]["scorev3"] = row[3]
                cve_data[row[0]]["modified"] = row[4]
                cve_data[row[0]]["vector"] = row[5]

        conn.close()
        return cve_data

    def cve_write_data(self, p, v, patched, cve_data, project_id):
        m = Mail()
        db = Database()
        c = db.connect()

        unpatched_cves = []

        for cve in sorted(cve_data):
            if cve not in patched:
                unpatched_cves.append(cve)

        if unpatched_cves:
            # check if there already is an entry for this package and version
            sql = "SELECT * " \
                  "FROM yocto_package " \
                  "WHERE yocto_package_name = '%s' " \
                  "AND version = '%s' " \
                  "AND project_id = '%s' " % (p, v, project_id)
            result = db.read_single_record(c, sql)

            # if package is not yet in database, create one
            if not result:
                sql = "INSERT INTO yocto_package " \
                      "(yocto_package_name, version, project_id, is_vulnerable) " \
                      "VALUES ('%s', '%s', '%s', '%s')" % (p, v, project_id, "true")
                db.create_record(c, sql)

                # create cve entries
                for i in unpatched_cves:
                    link = "https://nvd.nist.gov/vuln/detail/" + i
                    # check if there already is an entry for this cve
                    sql = "SELECT cve_id " \
                          "FROM yocto_cve " \
                          "WHERE cve_id = '%s'" % i
                    result = db.read_single_record(c, sql)
                    if not result:
                        sql = "INSERT INTO yocto_cve " \
                              "(cve_id, summary, scorev2, scorev3, link) " \
                              "VALUES ('%s', '%s', '%s', '%s', '%s')" % (i, '', '', '', link)
                        db.create_record(c, sql)

                    # create package_cve entries
                    sql = "INSERT INTO yocto_package_cve " \
                          "(yocto_package_id, yocto_cve_id) " \
                          "VALUES " \
                          "(" \
                          "(SELECT id FROM yocto_package " \
                          "WHERE yocto_package_name = '%s' " \
                          "AND version = '%s' " \
                          "AND project_id = '%s' ), " \
                          "(SELECT id " \
                          "FROM yocto_cve " \
                          "WHERE cve_id = '%s')" \
                          ")" % (p, v, project_id, i)
                    db.create_record(c, sql)

                # send out a mail
                result = utils.get_project_name(project_id)
                subject = "[emCVE-Watch: " + result["project_name"] + "] %s %s has unpatched CVE(s)" \
                          % (p, v)
                body = "%s %s has unpatched CVE(s): \n\n" % (p, v)
                for i in unpatched_cves:
                    link = "https://nvd.nist.gov/vuln/detail/" + i
                    body += link + '\n'
                recipient = utils.getRecipient(project_id)
                m.send_mail(recipient["email"], subject, body)

                # mark package as vulnerable
                utils.setVulnerable("Yocto", project_id, p, v)

            # if there already is an entry, check if there is a new cve
            else:
                sql = "SELECT yocto_cve.cve_id " \
                      "FROM yocto_cve " \
                      "INNER JOIN yocto_package_cve " \
                      "ON yocto_cve.id = yocto_package_cve.yocto_cve_id " \
                      "INNER JOIN yocto_package " \
                      "ON yocto_package.id = yocto_package_cve.yocto_package_id " \
                      "WHERE yocto_package_name = '%s' " \
                      "AND version = '%s' " \
                      "AND project_id = '%s' " % (p, v, project_id)
                # get all cve entries for the package/version
                known_cve = [d['cve_id'] for d in db.read_all_records(c, sql)]
                # let's see if we have new unpatched cves
                new_cve = [x for x in unpatched_cves if x not in known_cve]
                if new_cve:
                    # create cve entries
                    for i in new_cve:
                        link = "https://nvd.nist.gov/vuln/detail/" + i
                        sql = "INSERT INTO yocto_cve (cve_id, summary, scorev2, scorev3, link) " \
                              "VALUES ('%s', '%s', '%s', '%s', '%s')" % (i, '', '', '', link)
                        db.create_record(c, sql)

                        # create package_cve entries
                        sql = "INSERT INTO yocto_package_cve " \
                              "(yocto_package_id, yocto_cve_id) " \
                              "VALUES " \
                              "(" \
                              "(SELECT id FROM yocto_package " \
                              "WHERE yocto_package_name = '%s' " \
                              "AND version = '%s' " \
                              "AND project_id = '%s' ), " \
                              "(SELECT id " \
                              "FROM yocto_cve " \
                              "WHERE cve_id = '%s')" \
                              ")" % (p, v, project_id, i)
                        db.create_record(c, sql)
                    # send out a mail
                    result = utils.get_project_name(project_id)
                    subject = "[emCVE-Watch: " + result["project_name"] + "] %s %s has unpatched CVE(s)" \
                              % (p, v)
                    body = "%s %s has unpatched CVE(s): \n\n" % (p, v)
                    for i in new_cve:
                        link = "https://nvd.nist.gov/vuln/detail/" + i
                        body += link + '\n'

                    recipient = utils.getRecipient(project_id)
                    m.send_mail(recipient["email"], subject, body)

                    # mark package as vulnerable
                    utils.setVulnerable("Yocto", project_id, p, v)
