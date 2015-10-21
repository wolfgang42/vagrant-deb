#!/bin/bash
set -u
set -e

# Dependencies: jq git aptly realpath wget gettext-base
# Setup: aptly repo create -config=/path/to/aptly.conf --distribution=any --component=main vagrant-deb
GPG_KEY=AD319E0F7CFFA38B4D9F6E55CE3F3DE92099F7A4

BASEDIR=$(dirname $(realpath $0))
VERSION=$(wget -q -O - https://bintray.com/api/v1/packages/mitchellh/vagrant/vagrant/ | jq -r .latest_version)

# The choice of aptly was entirely arbitrary, but works fine.
aptly="aptly -config=$BASEDIR/aptly.conf"

if ! $aptly snapshot list | grep vagrant-$VERSION > /dev/null; then
	mkdir /tmp/vagrant-$VERSION
	cd /tmp/vagrant-$VERSION
	
	# Download the packages
	for package in vagrant_${VERSION}_{x86_64,i686}.deb; do
		wget -nv https://dl.bintray.com/mitchellh/vagrant/$package
	done
	
	# Add the packages to aptly
	$aptly repo add vagrant-deb .
	$aptly snapshot create vagrant-$VERSION from repo vagrant-deb

	$aptly publish switch any vagrant-$VERSION
	
	# Clean up after ourselves
	cd
	rm /tmp/vagrant-$VERSION/*
	rmdir /tmp/vagrant-$VERSION
fi

# Export variables for templating
export VERSION
export NOW=$(date +%F)
export GPG_KEY
cat $BASEDIR/index.tpl | envsubst > $BASEDIR/public_html/index.html
