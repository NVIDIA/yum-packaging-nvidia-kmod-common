%global _dracut_conf_d  %{_prefix}/lib/dracut/dracut.conf.d

# gsp_*.bin: ELF 64-bit LSB executable, UCB RISC-V
%global _binaries_in_noarch_packages_terminate_build 0
%global __strip /bin/true

Name:           nvidia-kmod-common
Version:        570.00
Release:        1%{?dist}
Summary:        Common file for NVIDIA's proprietary driver kernel modules
Epoch:          3
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html

BuildArch:      noarch

Source0:        %{name}-%{version}.tar.xz
Source1:        nvidia-boot-update
Source19:       nvidia-modeset.conf
Source20:       nvidia.conf
Source21:       60-nvidia.rules
Source24:       99-nvidia.conf

# UDev rule location (_udevrulesdir) and systemd macros:
BuildRequires:  systemd-rpm-macros

# Owns /usr/lib/firmware:
Requires:       linux-firmware
Requires:       nvidia-modprobe
Requires:       nvidia-kmod = %{?epoch:%{epoch}:}%{version}
Provides:       nvidia-kmod-common = %{?epoch:%{epoch}:}%{version}
%if 0%{?fedora} >= 41 || 0%{?rhel} >= 10
Recommends:     kmod-nvidia-open-dkms = %{?epoch:%{epoch}:}%{version}
%endif

%description
This package provides the common files required by all NVIDIA kernel module
package variants.
 
%prep
%autosetup

%install
# Script for post/preun tasks
install -p -m 0755 -D %{SOURCE1} %{buildroot}%{_sbindir}/nvidia-boot-update

# Nvidia modesetting support:
install -p -m 0644 -D %{SOURCE19} %{buildroot}%{_sysconfdir}/modprobe.d/nvidia-modeset.conf

# Load nvidia-uvm, enable complete power management:
install -p -m 0644 -D %{SOURCE20} %{buildroot}%{_modprobedir}/nvidia.conf

# Avoid Nvidia modules getting in the initrd:
install -p -m 0644 -D %{SOURCE24} %{buildroot}%{_dracut_conf_d}/99-nvidia.conf

# UDev rules:
# https://github.com/NVIDIA/nvidia-modprobe/blob/master/modprobe-utils/nvidia-modprobe-utils.h#L33-L46
# https://github.com/negativo17/nvidia-kmod-common/issues/11
# https://github.com/negativo17/nvidia-driver/issues/27
install -p -m 644 -D %{SOURCE21} %{buildroot}%{_udevrulesdir}/60-nvidia.rules

# Firmware files:
mkdir -p %{buildroot}%{_prefix}/lib/firmware/nvidia/%{version}/
install -p -m 644 firmware/* %{buildroot}%{_prefix}/lib/firmware/nvidia/%{version}

%post
%{_sbindir}/nvidia-boot-update post

%preun
if [ "$1" -eq "0" ]; then
  %{_sbindir}/nvidia-boot-update preun
fi ||:

%files
%{_dracut_conf_d}/99-nvidia.conf
%{_modprobedir}/nvidia.conf
%{_prefix}/lib/firmware/nvidia/%{version}
%{_sbindir}/nvidia-boot-update
%config %{_sysconfdir}/modprobe.d/nvidia-modeset.conf
%{_udevrulesdir}/60-nvidia.rules

%changelog
