# yum packaging nvidia kmod common

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Contributing](https://img.shields.io/badge/Contributing-Developer%20Certificate%20of%20Origin-violet)](https://developercertificate.org)

## Overview

Packaging templates for `yum` and `dnf` based Linux distros providing common configuration files for NVIDIA driver packages.

The `main` branch contains this README. The `.spec`, `.conf`, and `.rules` files can be found in the appropriate [rhel7](../../tree/rhel7), [rhel8](../../tree/rhel8), and [fedora](../../tree/fedora) branches.

## Table of Contents

- [Overview](#Overview)
- [Deliverables](#Deliverables)
- [Prerequisites](#Prerequisites)
  * [Clone this git repository](#Clone-this-git-repository)
  * [Install build dependencies](#Install-build-dependencies)
- [Building with script](#Building-with-script)
- [Building Manually](#Building-Manually)
- [Related](#Related)
  * [DKMS nvidia](#DKMS-nvidia)
  * [NVIDIA driver](#NVIDIA-driver)
  * [NVIDIA modprobe](#NVIDIA-modprobe)
  * [NVIDIA persistenced](#NVIDIA-persistenced)
  * [NVIDIA plugin](#NVIDIA-plugin)
  * [NVIDIA precompiled kmod](#NVIDIA-precompiled-kmod)
  * [NVIDIA settings](#NVIDIA-settings)
  * [NVIDIA xconfig](#NVIDIA-xconfig)
- [Contributing](#Contributing)


## Deliverables

This repo contains the `.spec` file used to build the following **RPM** packages:


> _note:_ `XXX` is the first `.` delimited field in the driver version, ex: `460` in `460.32.03`

* **RHEL8** or **Fedora** streams: `XXX`, `XXX-dkms`, `latest`, and `latest-dkms`
 ```shell
 nvidia-kmod-common-${driver}-${rel}.${distro}.noarch.rpm
 > ex: nvidia-kmod-common-460.32.03-1.el8.noarch.rpm
 ```


 * **RHEL7** flavors: `branch-XXX`, `latest`, and `latest-dkms`
  ```shell
  nvidia-kmod-common-${driver}-${rel}.${distro}.${arch}.rpm
  > ex: nvidia-kmod-common-460.32.03-1.el7.x86_64.rpm
  ```


* These common files include:
  ```shell
  - /usr/lib/dracut/dracut.conf.d/99-nvidia.conf
  - /usr/lib/modprobe.d/nvidia.conf
  - /usr/lib/udev/rules.d/60-nvidia.rules
  ```


## Prerequisites

### Clone this git repository:

Supported branches: `rhel7`, `rhel8` & `fedora`

```shell
git clone -b ${branch} https://github.com/NVIDIA/yum-packaging-nvidia-kmod-common
> ex: git clone -b rhel8 https://github.com/NVIDIA/yum-packaging-nvidia-kmod-common
```

### Install build dependencies

```shell
# Packaging
yum install rpm-build
```

## Building with script

### Fetch script from `main` branch

```shell
cd yum-packaging-nvidia-kmod-common
git checkout remotes/origin/main -- build.sh
```

### Usage

> _note:_ runfile is only used to determine version

```shell
./build.sh [$version | path/to/*.run]
> ex: time ./build.sh 450.102.04
> ex: time ./build.sh ~/Downloads/NVIDIA-Linux-x86_64-450.102.04.run
```


## Building Manually

### Packaging

```shell
mkdir BUILD BUILDROOT RPMS SRPMS SOURCES SPECS
cp 60-nvidia.rules SOURCES/
cp 99-nvidia.conf SOURCES/
cp nvidia.conf SOURCES/
cp nvidia-kmod-common.spec SPECS/

rpmbuild \
    --define "%_topdir $(pwd)" \
    --define "debug_package %{nil}" \
    --define "version $version" \
    --define "epoch 3" \
    --target "noarch" \
    -v -bb SPECS/nvidia-kmod-common.spec
```

> _note_: `noarch` as only text files, works for any architecture


## Related

### DKMS nvidia

- dkms-nvidia
  * [https://github.com/NVIDIA/yum-packaging-dkms-nvidia](https://github.com/NVIDIA/yum-packaging-dkms-nvidia)

### NVIDIA driver

- nvidia-driver
  * [https://github.com/NVIDIA/yum-packaging-nvidia-driver](https://github.com/NVIDIA/yum-packaging-nvidia-driver)

### NVIDIA modprobe

- nvidia-modprobe
  * [https://github.com/NVIDIA/yum-packaging-nvidia-modprobe](https://github.com/NVIDIA/yum-packaging-nvidia-modprobe)

### NVIDIA persistenced

- nvidia-persistenced
  * [https://github.com/NVIDIA/yum-packaging-nvidia-persistenced](https://github.com/NVIDIA/yum-packaging-nvidia-persistenced)

### NVIDIA plugin

- _dnf-plugin-nvidia_ & _yum-plugin-nvidia_
  * [https://github.com/NVIDIA/yum-packaging-nvidia-plugin](https://github.com/NVIDIA/yum-packaging-nvidia-plugin)

### NVIDIA precompiled kmod

- Precompiled kernel modules
  * [https://github.com/NVIDIA/yum-packaging-precompiled-kmod](https://github.com/NVIDIA/yum-packaging-precompiled-kmod)

### NVIDIA settings

- nvidia-settings
  * [https://github.com/NVIDIA/yum-packaging-nvidia-settings](https://github.com/NVIDIA/yum-packaging-nvidia-settings)

### NVIDIA xconfig

- nvidia-xconfig
  * [https://github.com/NVIDIA/yum-packaging-nvidia-xconfig](https://github.com/NVIDIA/yum-packaging-nvidia-xconfig)


## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)
