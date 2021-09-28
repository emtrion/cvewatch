> emCVE-Watch - a Web UI for monitoring CVE vulnerabilities for Debian and Yocto installations especially in embedded environments

# Table of Contents

- [Table of Contents](#table-of-contents)
    - [Getting Started](#getting-started)
        - [Requirements](#requirements)
        - [Installation](#installation)
    - [Features](#features)
        - [Check Debian installations](#check-debian-installations)
        - [Check Yocto installations](#check-yocto-installations)
        - [Install daily cron job](#install-daily-cron-job)
    - [Components](#components)
        - [Tested versions](#tested-versions)
        - [External Resources/Plugins](#external-resourcesplugins)
    - [Future Improvements](#future-improvements)
    - [Credits](#credits)
    - [License](#license)

## Getting Started

### Requirements

* PHP
* Python
* Apache
* MySQL/MariaDB
* python3-pymysql

### Installation

1. In these instructions, we assume you clone the repo directly to /var/www/html. As this is the default directory of
   the Apache webserver, don't forget to set the permissions accordingly and to clone as www-data user:

```bash
sudo chown -R www-data:www-data /var/www/html/
sudo su -s /bin/bash -c "git clone https://github.com/emtrion/cvewatch.git /var/www/html/" -g www-data www-data
```

2. Import the file `assets/setup/db.sql` into the current DBMS. The dump file also creates the database (
   named `cvewatch`), so no prior action is needed. If database name needs to be updated, change it in the dump file
   where the database title is declared.

```bash
mysql -u <username> -p < assets/setup/db.sql
```

3. Edit the file `assets/setup/env.php` according to your requirements. The email server (
   and the connected email account) will be used to send confirmation, validation and notification emails. Also the CVE
   reports will be sent to this email account.
4. Edit the file `webapp/constant.py` according to your requirements in order to customize the webapp settings.
5. The database contains an initial admin account. Open http://localhost in your browser, login with the following
   credentials and change admin password and email address via the profile settings:

```php
username: admin
password: aaaaaa
```

## Features

### Check Debian installations

Currently, we support Debian installations built with the well known elbe build system (https://elbe-rfs.org). After a
successful build process a file called source.xml will be generated. It contains all the Debian packages included in the
root filesystem. This file will be used as input for emCVE-Watch. To check a Debian root filesystem, follow these steps:

1. Create a project.
2. Go to the project detail site.
3. Upload Debian elbe XML file.
4. emCVE-Watch will parse the XML, check each package/version combination and send a mail to the email address stored in
   your profile.
5. The vulnerable packages will also be listed in the project view.

### Check Yocto installations

As Yocto does not export a suitable document, we could use as input, we developed a BitBake recipe and a BitBake class
which are needed to check Yocto installations. Further we use the built-in cve-check functionality. You will have to add
those two files found in the folder yocto to your Yocto project, in order to check for CVE vulnerabilities with
emCVE-Watch. Additionally, you will have to add the following to your local.conf:

```bash
# gather package information for remote cve check
INHERIT += "package-list"

# perform cve check
INHERIT += "cve-check"
```

Afterwards put `yocto/meta-xxx/recipes-core/meta/delete-package-file.bb`
and `yocto/meta-xxx/classes/package-list.bbclass` to the corresponding folders in your Yocto project. After the
successful build of your Yocto image, you will find a file called `yocto-packages.csv` in the `DEPLOY_DIR_IMAGE`. Now
you can check your project for vulnerable packages using emCVE-Watch.

1. Create a project.
2. Go to the project detail site.
3. Upload Yocto CSV file.
4. emCVE-Watch will parse the CSV, check each package/version combination and send a mail to the email address stored in
   your profile.
5. The vulnerable packages will also be listed in the project view.

### Install daily cron job

In order to check your projects every day, create a cron job using the provided file webapp/cron.py.

```bash
cat << EOF > /etc/cron.daily/cvewatch
#!/bin/bash
python3 /var/www/html/webapp/cron.py
EOF
```

Make it executable:

```bash
chmod +x /etc/cron.daily/cvewatch
```

## Components

### Tested versions

- PHP 7.4.21
- Python 3.9.2
- Apache 2.4.48
- MariaDB 10.5.11

### External Resources/Plugins

- PHPMailer 6.0.6
- Bootstrap 4.3.1
- Font awesome 5.12.0
- JQuery 3.4.1

## Future Improvements

Currently, Debian CVE checks take a long time to finish. This is due to the fact, that Debian handles CVE reports based
on the source package name. The elbe XML only contains the binary package name. There is no public API or database, that
returns the source package name for a given binary package. Thus, until know we have to get this information for each
package from the Sources.gz file for the specific Debian distribution. It would be a lot faster, if we maintain two
database tables which hold this information. This will be implemented in the future. Of course, feel free to send us
pull requests.

## Credits

Thanks to Muhammad Saad for providing the Web UI framework, on which emCVE-Watch is
based (https://github.com/msaad1999/PHP-Login-System).

## License

This project has been assigned the [MIT License](LICENSE), so go ahead and feel free to use any and/or all parts of this
system and to build on it.
