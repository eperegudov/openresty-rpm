
# RPM Spec for OpenResty
========================

[OpenResty](http://openresty.org) (ngx_openresty) is a full-fledged web application server by bundling the standard [Nginx](http://nginx.org) core, lots of 3rd-party Nginx modules, as well as most of their external dependencies. This spec file will build an RPM for OpenResty.

## RPM structure

* Prefix: `/usr/local/openresty/`
* Binary: `/usr/local/openresty/bin/resty`
* Core:   `/usr/local/openresty/nginx/`
* Core binary: `/usr/local/openresty/nginx/sbin/nginx`
* Core config: `/usr/local/openresty/nginx/conf/`
* Logs: `/var/log/openresty/`
* Sysconfig: `/etc/sysconfig/openresty`
* SYSV script: `/etc/rc.d/init.d/openresty`
* Systemd service: `/usr/lib/systemd/system/openresty.service`
* Logrotate service: `/etc/logrotate.d/openresty`
* Docs: `/usr/local/openresty/doc/`

## Distro support

This RPM package must build and working on RedHat-like distributions el5, el6, el7 versions and it's derivatives:

* RHEL/CentOS 7 x86_64
* RHEL/CentOS 6 x86_64/i386
* RHEL/CentOS 5 x86_64/i386
* Fedora 19 x86_64/i386 and upwards
    
Notes:

* This spec is tested under el7, el6 and el5 only 
* When you try to build on el5, must enable the EPEL repository
* Not tested on Fedora (as sane as I could test for)

openresty-rpm
=============

## Build

To build the RPM, you'll first need to set up your build environment. Typically, this means creating some directories and installing some packages:

* Install development tools for RPM (`rpmdevtools`,  `rpm-build`) and C\C++ (`make`, `gcc`, `gcc-c++`):

    ```
    	sudo yum -y install rpmdevtools rpm-build make gcc gcc-c++ 
    ```

Do it manually by building the RPM as a non-root user from your home directory:
	
* Set up your rpmbuild directory tree:
    ```
	rpmdev-setuptree
    ```

* Download the spec file:
    ```
	cd ~/rpmbuild/SPECS/
	wget https://github.com/joniknsk/openresty-rpm/raw/master/openresty.spec
    ```
* Get the relevant files into your tree (replacing `version` with the appropriate version string in spec file):
	```
	Version:        1.7.7.2
    ```
	
* Download remote source files with `spectool`. Spectool may fail if your distribution has an older version of `curl` - if so, use `wget` instead:
    ```
	spectool -g -R ~/rpmbuild/SPECS/openresty.spec
    ```
    or
    ```
	cd ~/rpmbuild/SOURCES/
	wget http://openresty.org/download/ngx_openresty-{version}.tar.gz
	wget https://github.com/joniknsk/openresty-rpm/archive/master.zip
    ```
	
* Install devel-packages to resolve `openresty` build dependencies:
    ```
	sudo yum -y install zlib-devel openssl-devel pcre-devel readline-devel postgresql-devel
    ```

* Then just build the RPM:
    ```
	rpmbuild -ba ~/rpmbuild/SPECS/openresty.spec
    ```

## Result

The RPM will be in `~/rpmbuild/RPMS/{platform}/` and the SRPM will be in `~/rpmbuild/SRPMS/`.

* If you need binary package only, run `rpmbuild` with `-bb` arguments:
    ```
	rpmbuild -bb ~/rpmbuild/SPECS/openresty.spec
    ```

## Run

* Install the RPM with `sudo yum localinstall openresty*.rpm` or `rpm -Uhv openresty*.rpm`
* Edit configuration files in `/usr/local/openresty/nginx/conf/`
* Change daemon command line arguments (if needed) in `/etc/sysconfig/openresty`
* Enable openresty service with `chkconfig openresty on` (el5, el6) or `systemctl enable openresty.service` (el7 and upwards :)
* Start the service `service openresty start` or `systemctl start openresty.service` and check the logs in `/var/log/openresty/`

## Config

Config files are loaded from the `/usr/local/openresty/nginx/conf`. Some sample configs are not provided.

## More info

See the [Nginx](http://nginx.org) and [OpenResty](http://openresty.org) websites for detailed documentation.
