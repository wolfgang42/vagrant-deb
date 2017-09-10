<!DOCTYPE html>
<html><head>
	<title>Unofficial Vagrant Debian Repository</title>
</head><body>
<h1>Unofficial Vagrant Debian Repository</h1>
	
<h2>About</h2>
	<p>This is an unofficial Debian repository for <a href="http://vagrantup.com/">Vagrant</a>, hosted by <a href="http://www.linestarve.com/">Wolfgang Faust</a>.
	It provides the Apt index only; the actual Debian packages will be downloaded from the
	<a href="https://releases.hashicorp.com/vagrant/">HashiCorp releases server</a>.
	You can see the code <a href="https://github.com/wolfgang42/vagrant-deb">on GitHub</a>.
	For questions/comments/complaints/praise/etc, open an issue there or email me at <a href="mailto:wolfgangmcq+vagrant-deb@gmail.com">wolfgangmcq+vagrant-deb@gmail.com</a>.</p>
	<p>I've recently updated the way the repository is generated.
	If you have any problems with it please let me know.</p>

<p>The current Vagrant version is <b>${VERSION}</b>; the last check was ${NOW}.</p>

<h2>How do I use it?</h2>
	You'll need to add the repository to your APT sources:
	<pre>
	sudo bash -c 'echo deb https://vagrant-deb.linestarve.com/ any main > /etc/apt/sources.list.d/wolfgang42-vagrant.list'
	sudo apt-key adv --keyserver pgp.mit.edu --recv-key ${GPG_KEY}
	sudo apt-get update
	</pre>
	Now install as usual:
	<pre>
	sudo apt-get install vagrant
	</pre>

</body></html>
