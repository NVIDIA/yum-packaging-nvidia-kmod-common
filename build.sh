#!/usr/bin/env bash

runfile="$1"
distro="$2"
topdir="$HOME/nvidia-kmod-common"
epoch="3"

[[ -n $distro ]] ||
distro=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
[[ $distro == "main" ]] && distro="rhel8"

drvname=$(basename "$runfile")
arch=$(echo "$drvname" | awk -F "-" '{print $3}')
version=$(echo "$drvname" | sed -e "s|NVIDIA\-Linux\-${arch}\-||" -e 's|\.run$||' -e 's|\-grid$||')
drvbranch=$(echo "$version" | awk -F "." '{print $1}')

err() { echo; echo "ERROR: $*"; exit 1; }
kmd() { echo; echo ">>> $*" | fold -s; eval "$*" || err "at line \`$*\`"; }
dep() { type -p "$1" >/dev/null || err "missing dependency $1"; }

build_rpm()
{
    mkdir -p "$topdir"
    (cd "$topdir" && mkdir -p BUILD BUILDROOT RPMS SRPMS SOURCES SPECS)

    cp -v -- *conf* "$topdir/SOURCES/"
    cp -v -- *.rules "$topdir/SOURCES/"
    cp -v -- *.spec "$topdir/SPECS/"
    cd "$topdir" || err "Unable to cd into $topdir"

    kmd rpmbuild \
        --define "'%_topdir $(pwd)'" \
        --define "'debug_package %{nil}'" \
        --define "'version $version'" \
        --define "'epoch $epoch'" \
        --target "noarch" \
        -v -bb SPECS/nvidia-kmod-common.spec

    cd - || err "Unable to cd into $OLDPWD"
}


# Sanity check
[[ -n $version ]] || err "version could not be determined"

# Build RPMs
empty=$(find "$topdir/RPMS" -maxdepth 0 -type d -empty 2>/dev/null)
found=$(find "$topdir/RPMS" -mindepth 2 -maxdepth 2 -type f -name "*${version}*" 2>/dev/null)
if [[ ! -d "$topdir/RPMS" ]] || [[ $empty ]] || [[ ! $found ]]; then
    echo "topdir: $topdir"
    echo "empty: $empty"
    echo "found: $found"

    echo "==> build_rpm(${version})"
    dep rpmbuild
    build_rpm
else
    echo "[SKIP] build_rpm(${version})"
fi

echo "---"
find "$topdir/RPMS" -mindepth 2 -maxdepth 2 -type f -name "*${version}*"
