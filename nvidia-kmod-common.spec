%if 0%{?rhel} == 6
# RHEL 6 does not have _udevrulesdir defined:
%global _udevrulesdir   %{_prefix}/lib/udev/rules.d/
%global _dracutopts     nouveau.modeset=0 rdblacklist=nouveau
%global _dracutopts_rm  nomodeset vga=normal
%global _dracut_conf_d	%{_sysconfdir}/dracut.conf.d
%global _modprobe_d     %{_sysconfdir}/modprobe.d/
# It's not _sbindir:
%global _grubby         /sbin/grubby --grub --update-kernel=ALL
%endif

%if 0%{?rhel} == 7
%global _dracutopts     nouveau.modeset=0 rd.driver.blacklist=nouveau nvidia-drm.modeset=1
%global _dracutopts_rm  nomodeset gfxpayload=vga=normal
%global _dracut_conf_d  %{_prefix}/lib/dracut/dracut.conf.d
%global _modprobe_d     %{_prefix}/lib/modprobe.d/
%global _grubby         %{_sbindir}/grubby --update-kernel=ALL
%endif

%if 0%{?fedora} || 0%{?rhel} >= 8
%global _dracutopts     rd.driver.blacklist=nouveau
# Don't disable nouveau at boot. Just matching the driver with OutputClass in
# the X.org configuration is enough to load the whole Nvidia stack or the Mesa
# one:
%global _dracutopts_rm  nomodeset gfxpayload=vga=normal nouveau.modeset=0 nvidia-drm.modeset=1
%global _dracut_conf_d  %{_prefix}/lib/dracut/dracut.conf.d
%global _modprobe_d     %{_prefix}/lib/modprobe.d/
%global _grubby         %{_sbindir}/grubby --update-kernel=ALL
%endif

Name:           nvidia-kmod-common
Version:        435.21
Release:        1%{?dist}
Summary:        Common file for NVIDIA's proprietary driver kernel modules
Epoch:          3
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html

BuildArch:      noarch

Source20:       nvidia.conf
Source21:       60-nvidia.rules
Source24:       99-nvidia.conf

# UDev rule location (_udevrulesdir) and systemd macros:
%if 0%{?fedora} >= 30
BuildRequires:  systemd-rpm-macros
%endif
%if 0%{?fedora} == 29 || 0%{?rhel} == 7 || 0%{?rhel} == 8
BuildRequires:  systemd
%endif

Requires:       grubby
Requires:       nvidia-kmod = %{?epoch:%{epoch}:}%{version}
Provides:       nvidia-kmod-common = %{?epoch:%{epoch}:}%{version}
Requires:       nvidia-driver = %{?epoch:%{epoch}:}%{version}
Obsoletes:      cuda-nvidia-kmod-common

%description
This package provides the common files required by all NVIDIA kernel module
package variants.
 
%prep

%install
mkdir -p %{buildroot}%{_udevrulesdir}
mkdir -p %{buildroot}%{_modprobe_d}/
mkdir -p %{buildroot}%{_dracut_conf_d}/
%if 0%{?fedora} || 0%{?rhel} >= 8
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_presetdir}
%endif

# Blacklist nouveau and load nvidia-uvm:
install -p -m 0644 %{SOURCE20} %{buildroot}%{_modprobe_d}/

# Avoid Nvidia modules getting in the initrd:
install -p -m 0644 %{SOURCE24} %{buildroot}%{_dracut_conf_d}/

# UDev rules:
# https://github.com/NVIDIA/nvidia-modprobe/blob/master/modprobe-utils/nvidia-modprobe-utils.h#L33-L46
# https://github.com/negativo17/nvidia-driver/issues/27
install -p -m 644 %{SOURCE21} %{buildroot}%{_udevrulesdir}

%post
type -p grubby && grubby --help >/dev/null
checkGrubby=$?
if [ $checkGrubby -eq 0 ]; then
  %{_grubby} --args='%{_dracutopts}' --remove-args='%{_dracutopts_rm}' &>/dev/null
  %if 0%{?fedora} || 0%{?rhel} >= 7
  if [ ! -f /run/ostree-booted ]; then
    . %{_sysconfdir}/default/grub
    if [ -z "${GRUB_CMDLINE_LINUX}" ]; then
      echo GRUB_CMDLINE_LINUX="%{_dracutopts}" >> %{_sysconfdir}/default/grub
    else
      for param in %{_dracutopts}; do
        echo ${GRUB_CMDLINE_LINUX} | grep -q $param
        [ $? -eq 1 ] && GRUB_CMDLINE_LINUX="${GRUB_CMDLINE_LINUX} ${param}"
      done
      for param in %{_dracutopts_rm}; do
        echo ${GRUB_CMDLINE_LINUX} | grep -q $param
        [ $? -eq 0 ] && GRUB_CMDLINE_LINUX="$(echo ${GRUB_CMDLINE_LINUX} | sed -e "s/$param//g")"
      done
      sed -i -e "s|^GRUB_CMDLINE_LINUX=.*|GRUB_CMDLINE_LINUX=\"${GRUB_CMDLINE_LINUX}\"|g" %{_sysconfdir}/default/grub
    fi
  fi
else
  echo "Skipping grubby, running in Anaconda"
fi
%endif

%preun
if [ "$1" -eq "0" ]; then
  %{_grubby} --remove-args='%{_dracutopts}' &>/dev/null
%if 0%{?fedora} || 0%{?rhel} >= 7
  if [ ! -f /run/ostree-booted ]; then
    for param in %{_dracutopts}; do
      echo ${GRUB_CMDLINE_LINUX} | grep -q $param
      [ $? -eq 0 ] && GRUB_CMDLINE_LINUX="$(echo ${GRUB_CMDLINE_LINUX} | sed -e "s/$param//g")"
    done
    sed -i -e "s|^GRUB_CMDLINE_LINUX=.*|GRUB_CMDLINE_LINUX=\"${GRUB_CMDLINE_LINUX}\"|g" %{_sysconfdir}/default/grub
  fi
%endif
fi ||:
%if 0%{?fedora} || 0%{?rhel} >= 8
%systemd_preun nvidia-fallback.service
%endif

%if 0%{?fedora} || 0%{?rhel} >= 8
%postun
%systemd_postun nvidia-fallback.service
%endif

%files
%{_dracut_conf_d}/99-nvidia.conf
%{_modprobe_d}/nvidia.conf
%{_udevrulesdir}/60-nvidia.rules

%changelog
* Tue Oct 01 2019 Simone Caronni <negativo17@gmail.com> - 3:435.21-3
- Remove workaround for onboard GPU devices.
- Fix typo on udev character device rules (thanks tbaederr).

* Tue Oct 01 2019 Simone Caronni <negativo17@gmail.com> - 3:435.21-2
- Fix build on CentOS/RHEL 8

* Tue Sep 03 2019 Simone Caronni <negativo17@gmail.com> - 3:435.21-1
- Update to 435.21.

* Thu Aug 22 2019 Simone Caronni <negativo17@gmail.com> - 3:435.17-1
- Update to 435.17.
- Add power management functions as per documentation.
- Require systemd-rpm-macros instead of systemd on Fedora/RHEL 8+.

* Wed Jul 31 2019 Simone Caronni <negativo17@gmail.com> - 3:430.40-1
- Update to 430.40.

* Fri Jul 12 2019 Simone Caronni <negativo17@gmail.com> - 3:430.34-1
- Update to 430.34.

* Wed Jun 12 2019 Simone Caronni <negativo17@gmail.com> - 3:430.26-1
- Update to 430.26.

* Thu Jun 06 2019 Simone Caronni <negativo17@gmail.com> - 3:430.14-2
- Do not run post/preun scriptlets on Atomic/Silverblue.

* Sat May 18 2019 Simone Caronni <negativo17@gmail.com> - 3:430.14-1
- Update to 430.14.

* Thu May 09 2019 Simone Caronni <negativo17@gmail.com> - 3:418.74-1
- Update to 418.74.
- Remove fallback scenario (thanks Karol Herbst).

* Thu Apr 18 2019 Simone Caronni <negativo17@gmail.com> - 3:418.56-2
- Obsoletes cuda-nvidia-kmod-common (thanks Timm).

* Sun Mar 24 2019 Simone Caronni <negativo17@gmail.com> - 3:418.56-1
- Update to 418.56.

* Fri Feb 22 2019 Simone Caronni <negativo17@gmail.com> - 3:418.43-1
- Update to 418.43.

* Wed Feb 06 2019 Simone Caronni <negativo17@gmail.com> - 3:418.30-1
- Update to 418.30.

* Sun Feb 03 2019 Simone Caronni <negativo17@gmail.com> - 3:415.27-1
- First build.
