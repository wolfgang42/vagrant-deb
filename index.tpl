<!DOCTYPE html>
<html><head>
	<title>Unofficial Vagrant Debian Repository</title>
</head><body>
<h1>Unofficial Vagrant Debian Repository</h1>

<h2>This repository is deprecated</h2>
<p>HashiCorp <a href="https://www.hashicorp.com/blog/announcing-the-hashicorp-linux-repository">now has an official repository</a> which includes packages for Vagrant. This unofficial repository will be supported <strong>until April 30, 2021</strong>, after which time it will no longer be available. There will also be <a href="https://github.com/wolfgang42/vagrant-deb/blob/master/brownouts.txt">periodic brownouts</a> during which attempting <code>apt-get update</code> will return 503 Service Unavailable, to give advance notice before the repo goes permanently offline. If you have any questions about this, please open an issue on GitHub or email me at the address below.</p>

<h3>To use the new repository</h3>

<p>Run:</p>
<pre>
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update
</pre>

<h3>Switching from this repository to the official one</h3>
<p>If you previously followed the instructions below to add the unofficial repository, remove that one with:</p>

<pre>sudo rm /etc/apt/sources.list.d/wolfgang42-vagrant.list
sudo apt-key del AD319E0F7CFFA38B4D9F6E55CE3F3DE92099F7A4</pre>

<div style="outline: 2px solid goldenrod; padding: 0 0.2em">

<p><strong>Important:</strong> You will also need to force apt to "downgrade" the installed package to the version in the official repository. The easiest way to do that is to uninstall and reinstall the package:</p>

<pre>sudo apt-get remove vagrant &amp;&amp; sudo apt-get update &amp;&amp; sudo apt-get install vagrant</pre>

<p>After doing this, run <code>dpkg -s vagrant</code> and make sure that the reported version does <em>not</em> start with <code>1:</code> &mdash; if it does you will not get any upgrades in the future!</p>

</div>

<p>(Why is this necessary? The packages from HashiCorp that this unofficial repository uses have an epoch, like <code><strong>1:</strong>2.2.14</code>. For some reason they dropped the epoch when creating packages for their new repository. As a result, after you remove the unofficial repository apt will think that the version you have installed is newer than any available from the official repository, and will never upgrade the package again.)

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
<p>As per the deprecation notice above, <strong>please don't.</strong> However, if you must:</p>

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
