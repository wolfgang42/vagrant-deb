<!DOCTYPE html>
<html><head>
	<title>Unofficial Vagrant Debian Repository</title>
</head><body>
<h1>Unofficial Vagrant Debian Repository</h1>

<h2>About</h2>
	<p>This is an unofficial Debian repository for <a href="http://vagrantup.com/">Vagrant</a>, hosted by <a href="http://www.linestarve.com/">Wolfgang Faust</a>.
	You can see the code <a href="https://github.com/wolfgang42/vagrant-deb">on GitHub</a>.
	For questions/comments/complaints/praise/etc, open an issue there or email me at <a href="mailto:wolfgangmcq+vagrant-deb@gmail.com">wolfgangmcq+vagrant-deb@gmail.com</a>.</p>

	<p>This service provides the Apt index only; the actual Debian packages will be downloaded from the
	<a href="https://releases.hashicorp.com/vagrant/">HashiCorp releases server</a>.
	Releases are checked against the
	<a href="https://www.hashicorp.com/security">HashiCorp security key</a>,
	and then resigned with my own automatic signing key.
	(This is necessary because I need to sign the Apt index I generate.)
	If you need it, here is the PGP public key I use to sign the repository:
	<a href="/vagrant-deb.asc"><code>vagrant-deb.asc</code></a></p>

<p>The current Vagrant version is <b>${VERSION}</b>; the last check was ${NOW}.</p>

<h2>How do I use it?</h2>
	You'll need to add the repository to your APT sources:
	<pre>
	sudo bash -c 'echo deb https://vagrant-deb.linestarve.com/ any main > /etc/apt/sources.list.d/wolfgang42-vagrant.list'
	sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key ${GPG_KEY}
	sudo apt-get update
	</pre>
	Now install as usual:
	<pre>
	sudo apt-get install vagrant
	</pre>

</body></html>
