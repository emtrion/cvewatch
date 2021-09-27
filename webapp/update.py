import os
import sqlite3
import urllib
import urllib.request
import urllib.parse
import gzip
import constant
from datetime import date


class Update:
    def debian_db(self):
        url = "https://security-tracker.debian.org/tracker/data/json"
        urllib.request.urlretrieve(url, constant.DOWNLOAD_PATH + constant.DEBIAN_CVE_FILE)

    def yocto_db(self):
        BASE_URL = "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-"
        YEAR_START = 2002

        db_file = constant.DOWNLOAD_PATH + constant.YOCTO_CVE_DB

        # check if db file exists
        if not os.path.isfile(db_file):
            with open(db_file, 'w') as d:
                pass

        # Connect to database
        conn = sqlite3.connect(db_file)
        c = conn.cursor()

        self.initialize_db(c)

        for year in range(YEAR_START, date.today().year + 1):
            year_url = BASE_URL + str(year)
            meta_url = year_url + ".meta"
            json_url = year_url + ".json.gz"

            # Retrieve meta last modified date
            response = urllib.request.urlopen(meta_url)
            if response:
                for l in response.read().decode("utf-8").splitlines():
                    key, value = l.split(":", 1)
                    if key == "lastModifiedDate":
                        last_modified = value
                        break
                else:
                    print("Cannot parse CVE metadata, update failed")
                    return

            # Compare with current db last modified date
            c.execute("select DATE from META where YEAR = ?", (year,))
            meta = c.fetchone()
            if not meta or meta[0] != last_modified:
                # Clear products table entries corresponding to current year
                c.execute("delete from PRODUCTS where ID like ?", ('CVE-%d%%' % year,))

                # Update db with current year json file
                try:
                    response = urllib.request.urlopen(json_url)
                    if response:
                        self.update_db(c, gzip.decompress(response.read()).decode('utf-8'))
                    c.execute("insert or replace into META values (?, ?)", [year, last_modified])
                except urllib.error.URLError as e:
                    print("Warning: CVE db update error, CVE data is outdated.\n\n")
                    print("Cannot parse CVE data (%s), update failed" % e.reason)
                    return

            # Update success, set the date to cve_check file.
            if year == date.today().year:
                print("CVE database update : %s\n\n" % date.today())

        conn.commit()
        conn.close()

    def initialize_db(self, c):
        c.execute("CREATE TABLE IF NOT EXISTS META (YEAR INTEGER UNIQUE, DATE TEXT)")

        c.execute("CREATE TABLE IF NOT EXISTS NVD (ID TEXT UNIQUE, SUMMARY TEXT, \
            SCOREV2 TEXT, SCOREV3 TEXT, MODIFIED INTEGER, VECTOR TEXT)")

        c.execute("CREATE TABLE IF NOT EXISTS PRODUCTS (ID TEXT, \
            VENDOR TEXT, PRODUCT TEXT, VERSION_START TEXT, OPERATOR_START TEXT, \
            VERSION_END TEXT, OPERATOR_END TEXT)")
        c.execute("CREATE INDEX IF NOT EXISTS PRODUCT_ID_IDX on PRODUCTS(ID);")

    def parse_node_and_insert(self, c, node, cveId):
        # Parse children node if needed
        for child in node.get('children', ()):
            self.parse_node_and_insert(c, child, cveId)

        def cpe_generator():
            for cpe in node.get('cpe_match', ()):
                if not cpe['vulnerable']:
                    return
                cpe23 = cpe['cpe23Uri'].split(':')
                vendor = cpe23[3]
                product = cpe23[4]
                version = cpe23[5]

                if version != '*' and version != '-':
                    # Version is defined, this is a '=' match
                    yield [cveId, vendor, product, version, '=', '', '']
                else:
                    # Parse start version, end version and operators
                    op_start = ''
                    op_end = ''
                    v_start = ''
                    v_end = ''

                    if 'versionStartIncluding' in cpe:
                        op_start = '>='
                        v_start = cpe['versionStartIncluding']

                    if 'versionStartExcluding' in cpe:
                        op_start = '>'
                        v_start = cpe['versionStartExcluding']

                    if 'versionEndIncluding' in cpe:
                        op_end = '<='
                        v_end = cpe['versionEndIncluding']

                    if 'versionEndExcluding' in cpe:
                        op_end = '<'
                        v_end = cpe['versionEndExcluding']

                    yield [cveId, vendor, product, v_start, op_start, v_end, op_end]

        c.executemany("insert into PRODUCTS values (?, ?, ?, ?, ?, ?, ?)", cpe_generator())

    def update_db(self, c, jsondata):
        import json
        root = json.loads(jsondata)

        for elt in root['CVE_Items']:
            if not elt['impact']:
                continue

            accessVector = None
            cveId = elt['cve']['CVE_data_meta']['ID']
            cveDesc = elt['cve']['description']['description_data'][0]['value']
            date = elt['lastModifiedDate']
            try:
                accessVector = elt['impact']['baseMetricV2']['cvssV2']['accessVector']
                cvssv2 = elt['impact']['baseMetricV2']['cvssV2']['baseScore']
            except KeyError:
                cvssv2 = 0.0
            try:
                accessVector = accessVector or elt['impact']['baseMetricV3']['cvssV3']['attackVector']
                cvssv3 = elt['impact']['baseMetricV3']['cvssV3']['baseScore']
            except KeyError:
                accessVector = accessVector or "UNKNOWN"
                cvssv3 = 0.0

            c.execute("insert or replace into NVD values (?, ?, ?, ?, ?, ?)",
                      [cveId, cveDesc, cvssv2, cvssv3, date, accessVector])

            configurations = elt['configurations']['nodes']
            for config in configurations:
                self.parse_node_and_insert(c, config, cveId)
