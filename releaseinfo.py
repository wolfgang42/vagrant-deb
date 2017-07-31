import os.path
import requests
import subprocess

def _cache_result(cachename):
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

@_cache_result(lambda build: 'size/'+build['filename'])
def build_size(build):
	r = requests.head(build['url'])
	r.raise_for_status()
	return r.headers['Content-Length']

@_cache_result(lambda release: 'shasums/'+release['shasums'])
def release_shasums(release):
	r = requests.get(
		'https://releases.hashicorp.com/' +
		release['name'] + '/' +
		release['version'] + '/' +
		release['shasums']
	)
	r.raise_for_status()
	return r.text

@_cache_result(lambda release: 'shasums/'+release['shasums']+'.sig')
def release_shasums_sig(release):
	r = requests.get(
		'https://releases.hashicorp.com/' +
		release['name'] + '/' +
		release['version'] + '/' +
		release['shasums_signature']
	)
	r.raise_for_status()
	return r.content

def check_shasums_sig(release):
	release_shasums(release)
	release_shasums_sig(release)
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
