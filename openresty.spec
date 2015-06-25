# Define github anchors
%define owner_name	joniknsk
%define project_name	openresty-rpm
%define branch_name	master

# Define system names
%define resty_user	nginx
%define resty_group	nginx
%define resty_loggroup	adm
%define package_name	ngx_openresty

# Define default files and directories
%define homedir %{_usr}/local/%{name}
%define logdir	%{_var}/log
%define rundir	%{_var}/run
%define sysdir	%{project_name}-%{branch_name}

%define pidfile  %{rundir}/%{name}.pid
%define lockfile %{rundir}/%{name}.lock
%define conffile %{homedir}/nginx/conf/nginx.conf
%define sbinfile %{homedir}/nginx/sbin/nginx

# Define system init system
%define use_systemd	(0%{?rhel} && 0%{?rhel} >= 7)

# Define basic RPM tags
Name:		openresty
Version:	1.7.7.2
Release:	1%{?dist}
Epoch:		1
Summary:	OpenResty - fast web app server by extending nginx
Group:		Productivity/Networking/Web/Servers
License:	BSD
URL:		http://openresty.org/
Source0:	http://openresty.org/download/%{package_name}-%{version}.tar.gz
Source1:	https://github.com/%{owner_name}/%{project_name}/archive/%{branch_name}.tar.gz

BuildRequires:	sed openssl-devel pcre-devel readline-devel
Requires:	openssl pcre readline
Requires(pre):	shadow-utils

%description
OpenResty (aka. ngx_openresty) is a full-fledged web application server by bundling the standard Nginx core, lots of 3rd-party Nginx modules, as well as most of their external dependencies.

%prep

%setup -n %{package_name}-%{version}
%setup -a 1 -n %{package_name}-%{version}

%build

# Set additional configure parameters
./configure \
    --user=%{resty_user} \
    --group=%{resty_group} \
    --pid-path=%{pidfile} \
    --lock-path=%{lockfile} \
    --error-log-path=%{logdir}/%{name}/error.log \
    --http-log-path=%{logdir}/%{name}/access.log \
    --with-file-aio \
    --with-ipv6 \
    --with-pcre-jit \
    --with-luajit \
    --with-http_ssl_module \
    --with-http_gunzip_module \
    --with-http_secure_link_module \
    --with-http_postgres_module \
    --with-http_realip_module \
    --with-http_sub_module \
    --with-http_auth_request_module \
    --with-http_stub_status_module \
    --with-cc-opt="%{optflags} $(pcre-config --cflags)"

make %{?_smp_mflags}


%pre

# Check if exists system user and group
getent group %{resty_group} || groupadd -f -r %{resty_group}
getent passwd %{resty_user} || useradd -M -d %{homedir} -g %{resty_group} -c "%{resty_user} user" -s /bin/nologin %{resty_user}
exit 0

%post

# Register the service
if [ $1 -eq 1 ]; then
%if %{use_systemd}
/usr/bin/systemctl preset %{name}.service >/dev/null 2>&1 ||:
%else
/sbin/chkconfig --add %{name}
%endif
fi

%install

# Clean destination and install main application
%{__rm} -rf %{buildroot}
make install DESTDIR=%{buildroot}

# Prepare templates to install
for file in $( ls -1 %{sysdir}/templates )
do
%{__sed} \
    -e 's|_NAME_|%{name}|g' \
    -e 's|_SBINFILE_|%{sbinfile}|g'  \
    -e 's|_CONFFILE_|%{conffile}|g'  \
    -e 's|_PIDFILE_|%{pidfile}|g'  \
    -e 's|_LOCKFILE_|%{lockfile}|g' \
    -e 's|_ENVFILE_|%{_sysconfdir}/sysconfig/%{name}|g' \
    -e 's|_USER_|%{resty_user}|g'  \
    -e 's|_GROUP_|%{resty_group}|g'  \
    -e 's|_LOGGROUP_|%{resty_loggroup}|g' \
    -e 's|_LOGDIR_|%{logdir}/%{name}|g'  \
    -e 's|_HOMEDIR_|%{homedir}|g' \
    < %{sysdir}/templates/${file} > %{sysdir}/${file/template/%{name}}
done
%{__mkdir_p} %{buildroot}%{homedir}/doc/%{project_name}
%{__cp} -r %{sysdir}/* %{buildroot}%{homedir}/doc/%{project_name}
# Install sysconfig file
%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m 644 %{sysdir}/%{name}.sysconf %{buildroot}%{_sysconfdir}/sysconfig/%{name}

# Install system service
%if %{use_systemd}
# install systemd-specific files
%{__mkdir_p} %{buildroot}%{_unitdir}
%{__install} -m 644 %{sysdir}/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
# install legacy upgrade action support
%{__mkdir_p} %{buildroot}%{_libexecdir}/initscripts/legacy-actions/%{name}
%{__install} -m 755 %{sysdir}/%{name}.upgrade %{buildroot}%{_libexecdir}/initscripts/legacy-actions/%{name}/upgrade
%else
# install SYSV init files
%{__mkdir_p} %{buildroot}%{_initrddir}
%{__install} -m 755 %{sysdir}/%{name}.init %{buildroot}%{_initrddir}/%{name}
%endif

# install log rotation files
%{__mkdir_p} %{buildroot}%{_sysconfdir}/logrotate.d
%{__install} -m 644 %{sysdir}/%{name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)

%if %{use_systemd}
%{_unitdir}/%{name}.service
%dir %{_libexecdir}/initscripts/legacy-actions/%{name}
%{_libexecdir}/initscripts/legacy-actions/%{name}/*
%else
%{_initrddir}/%{name}
%endif

%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}

%config(noreplace) %{homedir}/nginx/conf/fastcgi.conf
%config(noreplace) %{homedir}/nginx/conf/fastcgi_params
%config(noreplace) %{homedir}/nginx/conf/koi-utf
%config(noreplace) %{homedir}/nginx/conf/koi-win
%config(noreplace) %{homedir}/nginx/conf/mime.types
%config(noreplace) %{homedir}/nginx/conf/nginx.conf
%config(noreplace) %{homedir}/nginx/conf/scgi_params
%config(noreplace) %{homedir}/nginx/conf/uwsgi_params
%config(noreplace) %{homedir}/nginx/conf/win-utf

%{homedir}/luajit/*
%{homedir}/lualib/*
%{homedir}/nginx
%{homedir}/bin/resty
%{logdir}/%{name}
%doc %{homedir}/doc

%preun

if [ $1 -eq 0 ]; then
%if %{use_systemd}
/usr/bin/systemctl --no-reload disable %{name}.service >/dev/null 2>&1 ||:
/usr/bin/systemctl stop %{name}.service >/dev/null 2>&1 ||:
%else
/sbin/service %{name} stop > /dev/null 2>&1
/sbin/chkconfig --del %{name}
%endif
fi

%postun

%if %{use_systemd}
/usr/bin/systemctl daemon-reload >/dev/null 2>&1 ||:
%endif
if [ $1 -ge 1 ]; then
/sbin/service %{name} status  >/dev/null 2>&1 || exit 0
/sbin/service %{name} upgrade >/dev/null 2>&1 || echo \
"Binary upgrade failed, please check error.log"
fi

%changelog

* Tue Jun 23 2015 Eugene Peregudov <eugene.peregudov@gmail.com>
- ngx_openresty spec file repackaged
- 1.7.7.2 version added
- service name added
- support for EL7 added
