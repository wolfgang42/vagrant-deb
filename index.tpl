<!DOCTYPE html>
<html><head>
	<title>Unofficial Vagrant .deb Repository</title>
</head><body>
<h1>Unofficial Vagrant .deb Repository</h1>
	
<h2>About</h2>
	<p>This is an unofficial .deb repository for <a href="http://vagrantup.com/">Vagrant</a>, hosted by <a href="http://www.linestarve.com/">Wolfgang Faust</a>.
	It makes the official deb packages available as a repository for convenience. The current version is <b>${VERSION}</b>; the last check was ${NOW}.</p>
	<p>You can see the code <a href="https://github.com/wolfgang42/vagrant-deb">on GitHub</a>.
	For questions/comments/complaints/praise/etc, open an issue there or email me at <a href="mailto:wolfgangmcq+vagrant-deb@gmail.com">wolfgangmcq+vagrant-deb@gmail.com</a>.</p>

<h2>How do I use it?</h2>
	You'll need to add the repository to your APT sources:
	<pre>
	sudo bash -c 'echo deb http://vagrant-deb.linestarve.com/ any main > /etc/apt/sources.list.d/wolfgang42-vagrant.list'
	gpg --keyserver pgp.mit.edu --recv-keys ${GPG_KEY}
	gpg -a --export ${GPG_KEY} | sudo apt-key add --
	sudo apt-get update
	</pre>
	Now install as usual:
	<pre>
	sudo apt-get install vagrant
	</pre>

<hr/>
<div style="text-align:center;font-size:smaller">
<div>Hosted by Wolfgang Faust</div>
<div>Bitcoin:  <code>1Lb2sANPquQxVYBWqWJFYqPRj14YUUxdjF</code></div>
</div>
</body></html>
