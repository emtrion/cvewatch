import requests
import gzip
import constant
import xml.etree.ElementTree as Et
import debian.deb822 as deb822
from database import Database
from deb import Deb


def get_debian_sources(codename):
    url = 'http://ftp.debian.org/debian/dists/' + codename + '/main/source/Sources.gz'
    r = requests.get(url)
    return gzip.decompress(r.content)


def add_elbe_xml(project_id):
    db = Database()
    c = db.connect()
    d = Deb()

    sql = "SELECT uploaded_file " \
          "FROM project " \
          "WHERE id = '%s'" % project_id
    file_name = db.read_single_record(c, sql)

    sql = "SELECT users_id " \
          "FROM project " \
          "WHERE id = '%s'" % project_id
    user_id = db.read_single_record(c, sql)

    result = get_project_name(project_id)
    f = constant.UPLOAD_PATH + str(user_id["users_id"]) + "/" + result["project_name"] + "/" + str(
        file_name["uploaded_file"])

    tree = Et.parse(f)
    root = tree.getroot()
    distribution = Et.ElementTree(file=f).find('.//project/suite').text
    sources = get_debian_sources(distribution)

    for pkg in root.findall("./fullpkgs/pkg"):
        # convert binary Package name to source Package name
        for content in deb822.Sources.iter_paragraphs(sources):
            binary_packages = content['Binary']
            package_list = binary_packages.split(", ")
            if pkg.text in package_list:
                source_package_name = content['Package']
                # check if we already have an entry in the db
                sql = "SELECT * " \
                      "FROM debian_package " \
                      "WHERE debian_package_name = '%s' " \
                      "AND version = '%s' " \
                      "AND distribution = '%s' " \
                      "AND project_id = '%s'" \
                      % (source_package_name, pkg.attrib["version"], distribution, project_id)
                result = db.read_all_records(c, sql)
                if not result:
                    sql = "INSERT INTO debian_package " \
                          "(debian_package_name, version, distribution, project_id, is_vulnerable) " \
                          "VALUES ('%s', '%s', '%s', '%s', '%s')" \
                          % (source_package_name, pkg.attrib["version"], distribution, project_id, "false")
                    db.create_record(c, sql)
                    # do a check for each package when initially adding packages from an elbe xml
                    d.check_package(source_package_name, pkg.attrib["version"], distribution, project_id)
                    break


def get_project_id(project_name):
    db = Database()
    c = db.connect()
    sql = "SELECT id " \
          "FROM project " \
          "WHERE project_name = '%s'" % project_name
    return db.read_single_record(c, sql)


def get_project_name(project_id):
    db = Database()
    c = db.connect()
    sql = "SELECT project_name " \
          "FROM project " \
          "WHERE id = '%s'" % project_id
    return db.read_single_record(c, sql)


def get_all_projects():
    db = Database()
    c = db.connect()
    sql = "SELECT id, operating_system " \
          "FROM project"
    return db.read_all_records(c, sql)


def get_cve_id(cve):
    db = Database()
    c = db.connect()
    sql = "SELECT id " \
          "FROM debian_cve " \
          "WHERE cve_id = '%s'" % cve
    return db.read_single_record(c, sql)


def setStatus(project_id, value):
    db = Database()
    c = db.connect()
    sql = "UPDATE project " \
          "SET status_cve_check = '%s'" \
          "WHERE id = '%s'" % (value, project_id)
    db.write_single_record(c, sql)


def getRecipient(project_id):
    db = Database()
    c = db.connect()
    sql = "SELECT email " \
          "FROM users " \
          "WHERE id = (SELECT users_id FROM project WHERE id = '%s')" % project_id
    return db.read_single_record(c, sql)


def setVulnerable(os, project_id, package_name, version):
    db = Database()
    c = db.connect()
    if os == "Debian":
        sql = "UPDATE debian_package " \
              "SET is_vulnerable = '%s' " \
              "WHERE project_id = '%s' " \
              "AND debian_package_name = '%s' " \
              "AND version = '%s' " \
              % ("true", project_id, package_name, version)
        db.write_single_record(c, sql)
    elif os == "Yocto":
        sql = "UPDATE yocto_package " \
              "SET is_vulnerable = '%s' " \
              "WHERE project_id = '%s' " \
              "AND yocto_package_name = '%s' " \
              "AND version = '%s' " \
              % ("true", project_id, package_name, version)
        db.write_single_record(c, sql)
