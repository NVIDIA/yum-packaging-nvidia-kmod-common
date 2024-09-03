%global _dracutopts     rd.driver.blacklist=nouveau modprobe.blacklist=nouveau
%global _dracutopts_rm  nomodeset gfxpayload=vga=normal nouveau.modeset=0 nvidia-drm.modeset=1 initcall_blacklist=simpledrm_platform_driver_init
%global _dracut_conf_d  %{_prefix}/lib/dracut/dracut.conf.d
%global _grubby         %{_sbindir}/grubby --update-kernel=ALL

# gsp_*.bin: ELF 64-bit LSB executable, UCB RISC-V
%global _binaries_in_noarch_packages_terminate_build 0
%global __strip /bin/true

Name:           nvidia-kmod-common
Version:        %{?version}%{?!version:550.54.14}
Release:        1%{?dist}
Summary:        Common file for NVIDIA's proprietary driver kernel modules
Epoch:          3
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html

BuildArch:      noarch

Source0:        %{name}-%{version}.tar.xz
Source19:       nvidia-modeset.conf
Source20:       nvidia.conf
Source21:       60-nvidia.rules
Source24:       99-nvidia.conf

BuildRequires:  systemd-rpm-macros

Requires:       grubby
# Owns /usr/lib/firmware:
Requires:       linux-firmware
Requires:       nvidia-modprobe
Requires:       nvidia-kmod = %{?epoch:%{epoch}:}%{version}
Provides:       nvidia-kmod-common = %{?epoch:%{epoch}:}%{version}
Obsoletes:      cuda-nvidia-kmod-common

%description
This package provides the common files required by all NVIDIA kernel module
package variants.
 
%prep
%autosetup

%install
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
type -p grubby && grubby --help >/dev/null
checkGrubby=$?
if [ $checkGrubby -eq 0 ]; then
  %{_grubby} --args='%{_dracutopts}' --remove-args='%{_dracutopts_rm}' &>/dev/null
  %if 0%{?fedora} || 0%{?rhel} >= 7
  if [ ! -f /run/ostree-booted ] && [ -f %{_sysconfdir}/default/grub ]; then
    . %{_sysconfdir}/default/grub
    if [ -z "${GRUB_CMDLINE_LINUX}" ]; then
      echo GRUB_CMDLINE_LINUX=\"%{_dracutopts}\" >> %{_sysconfdir}/default/grub
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
  if [ ! -f /run/ostree-booted ] && [ -f %{_sysconfdir}/default/grub ]; then
    . %{_sysconfdir}/default/grub
    for param in %{_dracutopts}; do
      echo ${GRUB_CMDLINE_LINUX} | grep -q $param
      [ $? -eq 0 ] && GRUB_CMDLINE_LINUX="$(echo ${GRUB_CMDLINE_LINUX} | sed -e "s/$param//g")"
    done
    sed -i -e "s|^GRUB_CMDLINE_LINUX=.*|GRUB_CMDLINE_LINUX=\"${GRUB_CMDLINE_LINUX}\"|g" %{_sysconfdir}/default/grub
  fi
%endif
fi ||:

%files
%{_dracut_conf_d}/99-nvidia.conf
%{_modprobedir}/nvidia.conf
%{_prefix}/lib/firmware/nvidia/%{version}
%config %{_sysconfdir}/modprobe.d/nvidia-modeset.conf
%{_udevrulesdir}/60-nvidia.rules
