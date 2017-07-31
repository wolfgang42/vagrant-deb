#!/usr/bin/env python2
import sys
import json
import os.path
import requests
import subprocess

with open('cache/releases.json') as f:
	releases = json.load(f)

ARCH_SYNONYMS = {
	'i386': ['i386', 'i686'],
	'amd64': ['amd64', 'x86_64'],
}

def get_build(release, arch):
	for build in release['builds']:
		if build['os'] == 'debian' and build['arch'] in ARCH_SYNONYMS[arch]:
			return build

def get_shasums(release):
	cachefile = 'cache/shasums/'+release['shasums']
	# Download shasums (if they don't exist)
	if not os.path.exists(cachefile):
		r = requests.get(
			'https://releases.hashicorp.com/' +
			release['name'] + '/' +
			release['version'] + '/' +
			release['shasums']
		)
		r.raise_for_status()
		with open(cachefile, 'w') as f:
			f.write(r.text)
	# Download shasums signature (if it doesn't exist)
	if not os.path.exists(cachefile+'.sig'):
		r = requests.get(
			'https://releases.hashicorp.com/' +
			release['name'] + '/' +
			release['version'] + '/' +
			release['shasums_signature']
		)
		r.raise_for_status()
		with open(cachefile+'.sig', 'w') as f:
			f.write(r.content)
	# Verify shasums signature
	# https://github.com/micahflee/torbrowser-launcher/issues/147
	p = subprocess.Popen([
		'/usr/bin/gpg',
		# Output machine-readable data on stderr
		'--status-fd', '2',
		# Use a keyring which only has Hashicorp's key on it
		'--no-default-keyring', '--keyring', '/app/hashicorp.key',
		# We completely trust all keys on this keyring
		# (as per above, there's only one anyway)
		'--trust-model', 'always',
		# Verify the shasums file using its signature
		'--verify', cachefile+'.sig',
	], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.wait()
	output = p.stderr.read()
	if (
		(p.returncode != 0) or
		('GOODSIG 51852D87348FFC4C HashiCorp Security <security@hashicorp.com>' not in output) or
		('VALIDSIG 91A6E7F85D05C65630BEF18951852D87348FFC4C' not in output)
	):
		raise Exception('Bad signature for '+release['shasums'])
	# Finally, return the result
	ret = {}
	with open(cachefile) as f:
		for line in f:
			(sha, filename) = line.strip().split('  ')
			ret[filename] = sha
	return ret

def get_size(build):
	cachefile = 'cache/size/'+build['filename']
	if not os.path.exists(cachefile):
		r = requests.head(build['url'])
		r.raise_for_status()
		with open(cachefile, 'w') as f:
			f.write(r.headers['Content-Length'])
	with open(cachefile) as f:
		return f.read()


arch=sys.argv[1]
redirects = open('public_html/redirects-'+arch+'.conf', 'w')
for program in ['vagrant']:
	for version in releases[program]['versions']:
		release = releases[program]['versions'][version]
		build = get_build(release, arch)
		if build:
			print "Package:", program
			print "Version:", version
			print "Architecture:", arch
			print "Maintainer: HashiCorp <support@hashicorp.com>"
			print "Description: no description given"
			poolname = "pool/any/main/"+program[0]+"/"+program+"/"+program+"_"+version+"_"+arch+".deb"
			redirects.write('rewrite ^/'+poolname+' '+build['url']+' permanent;\n')
			print "Filename:", poolname
			print "SHA256:", get_shasums(release)[build['filename']]
			print "Size:", get_size(build)
			print
