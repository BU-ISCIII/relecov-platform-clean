# relecov-platform

[![python_lint](https://github.com/BU-ISCIII/relecov-tools/actions/workflows/python_lint.yml/badge.svg)](https://github.com/BU-ISCIII/relecov-tools/actions/workflows/python_lint.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Django](https://img.shields.io/static/v1?label=Django&message=3.2.17&color=blue?style=plastic&logo=django)](https://github.com/django/django)
[![Python](https://img.shields.io/static/v1?label=Python&message=3.9.10&color=green?style=plastic&logo=Python)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-v5.0-blueviolet?style=plastic&logo=Bootstrap)](https://getbootstrap.com)
[![version](https://img.shields.io/badge/version-1.0.0-orange?style=plastic&logo=GitHub)](https://github.com/BU-ISCIII/relecov-platform.git)

> THIS REPO IS IN ACTIVE DEVELOPMENT.
>
## Table of contents

* [Installation](#installation)
* [Upgrade new release](#upgrade-to-new-release)
* [Documentation](#documentation)

# Installation

## Relecov docker installation

SOME MODIFICATIONS
SOME MORE MODIFICATIONS
MORE MODIFICATIONS

## Install relecov-platform in your server (RedHat / CentOs / Ubuntu)

Before starting the installation check :

* You have **sudo privileges** to install the additional software packets that relecov-platform needs.
* Database (MySQL/MariaDB) is running
* Local server configured for sending emails
* Apache server is running on local server
* Dependencies:
  * lsb_release:
     RedHat/CentOS: ```yum install redhat-lsb-core```

### Create relecov database and grant permissions

1. Create a new database named "relecov" (this is mandatory)
2. Create a new user with permission to read and modify that database.
3. Write down user, passwd and db server info.

### Clone github repository

Open a linux terminal and move to a directory where relecov code will be downloaded

```bash
cd <your personal folder>
git clone https://github.com/BU-ISCIII/relecov-platform.git relecov-platform
cd relecov_platform
```

### Configuration settings

Copy the initial setting template into a file named install_settings.txt

```bash
cp conf/template_install_settings.txt install_settings.txt
```

Open with your favourite editor the configuration file to set your own values for
database ,email settings and the local IP of the server where relecov-platform will run.

```bash
nano install_settings.txt
```

### Run installation script

Relecov-platform should be installed on the "/opt" directory. In order to handle different installation responsibilities inside the organization, where you may not be the person with root privileges, our instalation script has these options in ```--install``` parameter:

* dep: to install the software packages as well as python packages inside the virtual environment. Root is needed.
* app: to install only the iSkyLIMS application software without need of being root.
* full: if you directly have root permissions you can install both deps and app at the same time with this option.

Execute one of the following commands in a linux terminal to install, according as
above description.

```bash
# to install only software packages dependences
sudo bash install.sh --install dep

# to install only iSkyLIMS application
bash install.sh --install app --git_revision main --tables

# to install both software
sudo bash install.sh --install full --git_revision main --tables
```

## Install nextstrain

The Nextstrain CLI ties together all necesary pieces to provide a consistent way to run pathogen workflows, access Nextstrain tools like Augur and Auspice across computing environments such as Docker, Conda, and AWS Batch, and publish datasets to nextstrain.org.

### Download installer

Move to the installation path and download installer

```
mkdir -p /opt/nextstrain
cd /opt/nextstrain
curl -fsSL --proto '=https' https://nextstrain.org/cli/installer/linux > nexstrain_installer_$(date "+%Y%m%d").sh
```

Set NEXSTRAIN_HOME env variable and run installer

```
export NEXTSTRAIN_HOME=/opt/nextstrain
bash nexstrain_installer_$(date "+%Y%m%d").sh
```

Set conda as default run-time.This will install the nexstrain conda env with all deps using micromamba.

```
/opt/nextstrain/cli-standalone/nextstrain setup --set-default conda
```

Copy service file to `/usr/lib/systemd/system`

```
cp ./conf/nextstrain.service /etc/systemd/system
```

Copy auspice dataset to datasets folder. This contains all the data that should be rendered by nextstrain app. This is created using the [nexstrain_relecov workflow](https://github.com/BU-ISCIII/nexstrain_relecov)

```
mkdir -p /opt/nextstrain/dataset/sars-cov-2
cp -r /path/to/auspice /opt/nextstrain/dataset/sars-cov-2
```

## Upgrade

### Running upgrade script

If your organization requires that dependencies / stuff that needs root are installed by a different person that install the application the you can use the install script in several steps as follows.

First you need to rename the folder app name in the installation folder (`/opt/iSkyLIMS`):

#### Steps requiring root

Make sure that the installation folder has the correct permissions so the person installing the app can write in that folder.

```bash
# In case you have a script for this task. You'll need to adjust this script according to the name changing: /opt/iSkyLIMS to /opt/iskylims
/scripts/hardening.sh
```

From the previous release software dependences (Python packages) must be updated to the releases defined in the requirement.txt file.

In the linux terminal execute the following command-

```bash
# to upgrade only software packages dependences. NEEDS ROOT.
sudo bash install.sh --upgrade dep
```

#### Steps not requiring root

Next you need to upgrade iskylims app. Please use one of the commands below:

If you are using the library pool, you must indicate in the installation script the file
you already backup and execute the following command.

```bash
# to upgrade iSkyLIMS application including changes required in this release. DOES NOT NEED ROOT.
bash install.sh --upgrade app --script <your_selected_folder/backup_lib_pool.sql>  --git_revision main --tables
```

If restauration of libary preparation is not required then execute the following command

```bash
# to upgrade iSkyLIMS application including changes required in this release. DOES NOT NEED ROOT.
bash install.sh --upgrade app ---git_revision main  -tables
```

Make sure that the installation folder has the correct permissions.

```bash
# In case you have a script for this task. Some paths have changed in this version, so you may need to adjust your hardening script.
/scripts/hardening.sh
```

# Documentation

Relecov usage documentation is included in the platform.

In the menu, click on **Documentation**.
