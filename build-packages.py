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

def cache_result(cachename):
	def decorator(getresult):
		def wrapper(*args):
			cachefile = 'cache/' + cachename(*args)
			if not os.path.exists(cachefile):
				result = getresult(*args)
				with open(cachefile, 'w') as f:
					f.write(result)
			with open(cachefile) as f:
				return f.read()
		return wrapper
	return decorator

def get_build(release, arch):
	for build in release['builds']:
		if build['os'] == 'debian' and build['arch'] in ARCH_SYNONYMS[arch]:
			return build

@cache_result(lambda build: 'size/'+build['filename'])
def get_size(build):
	r = requests.head(build['url'])
	r.raise_for_status()
	return r.headers['Content-Length']

@cache_result(lambda release: 'shasums/'+release['shasums'])
def get_shasums(release):
	r = requests.get(
		'https://releases.hashicorp.com/' +
		release['name'] + '/' +
		release['version'] + '/' +
		release['shasums']
	)
	r.raise_for_status()
	return r.text

@cache_result(lambda release: 'shasums/'+release['shasums']+'.sig')
def get_shasums_sig(release):
	r = requests.get(
		'https://releases.hashicorp.com/' +
		release['name'] + '/' +
		release['version'] + '/' +
		release['shasums_signature']
	)
	r.raise_for_status()
	return r.content

def check_shasums_sig(release):
	get_shasums(release)
	get_shasums_sig(release)
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
		'--verify', 'cache/shasums/'+release['shasums']+'.sig',
	], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.wait()
	output = p.stderr.read()
	if (
		(p.returncode != 0) or
		('GOODSIG 51852D87348FFC4C HashiCorp Security <security@hashicorp.com>' not in output) or
		('VALIDSIG 91A6E7F85D05C65630BEF18951852D87348FFC4C' not in output)
	):
		raise Exception('Bad signature for '+release['shasums'])

def shasums(release):
	check_shasums_sig(release)
	ret = {}
	for line in get_shasums(release).split('\n'):
		if line == '': continue
		(sha, filename) = line.split('  ')
		ret[filename] = sha
	return ret

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
			print "SHA256:", shasums(release)[build['filename']]
			print "Size:", get_size(build)
			print
