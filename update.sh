#!/bin/bash
set -u
set -e
set -o pipefail

BASEDIR=$(dirname $(realpath $0))

mkdir -p cache/{control,shasums,size}/
mkdir -p public_html/dists/any/main/binary-{i386,amd64}/
curl -s https://releases.hashicorp.com/index.json > cache/releases.json

for arch in i386 amd64; do
	$BASEDIR/build-packages.py $arch > public_html/dists/any/main/binary-$arch/Packages.new
	pushd public_html/dists/any/main/binary-$arch/ > /dev/null
	if cmp -s Packages Packages.new; then
		rm Packages.new
	else
		echo "Updated Packages for $arch"
		mv Packages.new Packages
		gzip -kf Packages
		bzip2 -kf Packages
	fi
	if [ ! -e Release ]; then
		echo "Created Release for $arch"
		echo 'Archive: any' >> Release
		echo 'Component: main' >> Release
		echo "Architecture: $arch" >> Release
	fi
	popd > /dev/null
done

pushd public_html/dists/any/ > /dev/null
rm -f Release.new
echo 'Suite: any' >> Release.new
echo 'Codename: any' >> Release.new
echo 'Components: main' >> Release.new
echo 'Architectures: i386 amd64' >> Release.new
$BASEDIR/build-release-checksums.py main/binary-{amd64,i386}/{Release,Packages{,.gz,.bz2}} >> Release.new
echo 'Date:' $(date -R -u) >> Release.new
echo 'Valid-Until:' $(date -R -u -d@$(( $(date '+%s') + 60*60*24*2))) >> Release.new # +2 days
mv Release.new Release
rm -f InRelease Release.gpg
gpg --clearsign -a -s -o InRelease Release
gpg -a -b -s -o Release.gpg Release
popd > /dev/null

# Brownouts
if grep "$(date +%F)" brownouts.txt; then
	cat << HERE >> public_html/redirects-i386.conf
location /dists/any {
	return 503; # Service Unavailable
}
HERE
fi

# Export variables for templating
export VERSION=$(cat cache/releases.json | jq -r '.vagrant.versions | keys | .[]' | sort --version-sort | tail -n1)
export NOW=$(date +%F)
export GPG_KEY=$(gpg -K --with-colons --with-fingerprint | grep '^fpr:' | cut -d: -f10)
cp vagrant-deb.asc public_html/
cat $BASEDIR/index.tpl | envsubst > $BASEDIR/public_html/index.html
