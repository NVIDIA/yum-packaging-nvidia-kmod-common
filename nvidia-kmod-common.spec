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
# Fallback service tries to load nouveau if nvidia is not loaded, so don't
# disable nouveau at boot. Just matching the driver with OutputClass in the
# X.org configuration is enough to load the whole Nvidia stack or the Mesa one:
%global _dracutopts_rm  nomodeset gfxpayload=vga=normal nouveau.modeset=0 nvidia-drm.modeset=1
%global _dracut_conf_d  %{_prefix}/lib/dracut/dracut.conf.d
%global _modprobe_d     %{_prefix}/lib/modprobe.d/
%global _grubby         %{_sbindir}/grubby --update-kernel=ALL
%endif

Name:           nvidia-kmod-common
Version:        418.56
Release:        1%{?dist}
Summary:        Common file for NVIDIA's proprietary driver kernel modules
Epoch:          3
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html

BuildArch:      noarch

Source20:       nvidia.conf
Source21:       60-nvidia.rules
Source24:       99-nvidia.conf

# Auto-fallback to nouveau, requires server 1.19.0-3+, glvnd enabled mesa:
Source50:       nvidia-fallback.service
Source51:       95-nvidia-fallback.preset

%if 0%{?fedora} || 0%{?rhel} >= 7
# UDev rule location (_udevrulesdir) and systemd macros:
BuildRequires:  systemd
# Nouveau fallback service
%{?systemd_requires}
%endif

Requires:       grubby
Requires:       nvidia-kmod = %{?epoch:%{epoch}:}%{version}
Provides:       nvidia-kmod-common = %{?epoch:%{epoch}:}%{version}
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

%if 0%{?fedora}
# install auto-fallback to nouveau service:
install -p -m 0644 %{SOURCE50} %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE51} %{buildroot}%{_presetdir}
%endif

# UDev rules:
# https://github.com/NVIDIA/nvidia-modprobe/blob/master/modprobe-utils/nvidia-modprobe-utils.h#L33-L46
# https://github.com/negativo17/nvidia-driver/issues/27
install -p -m 644 %{SOURCE21} %{buildroot}%{_udevrulesdir}

# Apply the systemd preset for nvidia-fallback.service when upgrading from
# a version without nvidia-fallback.service, as %%systemd_post only does this
# on fresh installs:
%if 0%{?fedora}
%triggerun -- %{name} < 2:381.22-2
systemctl --no-reload preset nvidia-fallback.service >/dev/null 2>&1 || :
%endif

%post
%{_grubby} --args='%{_dracutopts}' --remove-args='%{_dracutopts_rm}' &>/dev/null
%if 0%{?fedora} || 0%{?rhel} >= 7
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
%endif
%if 0%{?fedora} || 0%{?rhel} >= 8
%systemd_post nvidia-fallback.service
%endif

%preun
if [ "$1" -eq "0" ]; then
  %{_grubby} --remove-args='%{_dracutopts}' &>/dev/null
%if 0%{?fedora} || 0%{?rhel} >= 7
  for param in %{_dracutopts}; do
    echo ${GRUB_CMDLINE_LINUX} | grep -q $param
    [ $? -eq 0 ] && GRUB_CMDLINE_LINUX="$(echo ${GRUB_CMDLINE_LINUX} | sed -e "s/$param//g")"
  done
  sed -i -e "s|^GRUB_CMDLINE_LINUX=.*|GRUB_CMDLINE_LINUX=\"${GRUB_CMDLINE_LINUX}\"|g" %{_sysconfdir}/default/grub
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
%if 0%{?fedora}
%{_unitdir}/nvidia-fallback.service
%{_presetdir}/95-nvidia-fallback.preset
%endif
%{_dracut_conf_d}/99-nvidia.conf
%{_modprobe_d}/nvidia.conf
%{_udevrulesdir}/60-nvidia.rules

%changelog
* Sun Mar 24 2019 Simone Caronni <negativo17@gmail.com> - 3:418.56-1
- Update to 418.56.

* Fri Feb 22 2019 Simone Caronni <negativo17@gmail.com> - 3:418.43-1
- Update to 418.43.

* Wed Feb 06 2019 Simone Caronni <negativo17@gmail.com> - 3:418.30-1
- Update to 418.30.

* Sun Feb 03 2019 Simone Caronni <negativo17@gmail.com> - 3:415.27-1
- First build.
