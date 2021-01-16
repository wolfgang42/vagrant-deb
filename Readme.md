# Deprecated!
Use the new [offical repository](https://www.hashicorp.com/blog/announcing-the-hashicorp-linux-repository) instead.

This unofficial repository will be supported until April 30, 2021, after which time the repository will be unavailable.

There will also be periodic brownouts (see `brownouts.txt` for dates) during which attempting `apt-get update` will return 503 Service Unavailable, to give advance notice before the repo goes permanently offline.

# About
HashiCorp provides Debian packages for Vagrant,
but they don't provide a repository so you have to download the packages
and reinstall them manually every time there's an update.
The [feature request to add a repository](https://github.com/mitchellh/vagrant-installers/issues/12)
is not a particularly high priority for them,
so as a public service I made a repository and set it up at
[vagrant-deb.linestarve.com](https://vagrant-deb.linestarve.com).

Originally, I was using [Aptly](https://www.aptly.info/)
to generate the repository.
However, this required downloading and serving the deb package,
which was annoying because I have a fairly small disk on my server
and the packages were taking up an awful lot of room.

This version generates the repository directly from the
[HashiCorp releases page](http://releases.hashicorp.com/)
and provides redirects to the actual packages.
This has a number of benefits:
* I can publish every version of Vagrant, not just the ones that fit on my disk.
* Package files will be downloaded directly from HashiCorp, alleviating concerns about tampering.
* Increased integrity verification: the SHA256 in the `Packages` file comes directly from their API,
  and the signature of the `SHA256SUMS` file is now checked against the
  [HashiCorp GPG key](https://www.hashicorp.com/security/).

# Development
The code is intended to be run in a Docker container.
You will need to make a GPG key and export it as `signing.private.key`;
it will be embedded in the generated Docker image.

To run:
```
docker build -t vagrant-deb .
docker run --rm -v $(pwd)/public_html/:/app/public_html/ -v $(pwd)/cache/:/app/cache/ vagrant-deb
```

This will create a `cache/` folder (see below) as well as a `public_html/` folder
to be served. The `public_html/` folder will also contain `redirects-{amd64,i386}.conf`
files which should be `include`d in the Nginx configuration, to publish the repository's pool.

# Code Overview
This program creates all of the repository files from scratch,
without using any of the usual helper programs.
This is because they all expect that you have a package and want to publish it yourself;
since I *don't* want to download the packages this won't work.
The documentation on the
[Debian repository format](https://wiki.debian.org/DebianRepository/Format)
will probably be very helpful in trying to understand how all of the pieces fit together.

`update.sh` is the main script, which handles orchestrating all of the various pieces.
It delegates to various Python scripts to actually generate the files,
then handles compressing, signing, and so on.
It avoids touching files that haven't changed, so that they can be cached and
don't need to be re-downloaded.
It has four main steps:
1. Create various folders and download `releases.json`
2. Update the files for each architecture.
3. Update the `Release` files for the repository.
4. Update `index.html` with the latest version and update time.

`build-packages.py` generates a `Packages` file for each architecture,
as well as the redirects file for that architecture's `/pool/`.
It leans heavily on `releaseinfo.py`, which provides various library routines
for extracting information about individual Vagrant versions.
(See the comments in that file for details on each of the functions.)

`build-release-checksums.py` generates the checksum portion of the `Release` file.

`index.tpl` is a template for `index.html`; it contains various placeholders
which `envsubst` will replace during the update process.
