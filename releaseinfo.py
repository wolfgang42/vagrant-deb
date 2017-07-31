import os.path
import requests
import subprocess
import tarfile

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

@_cache_result(lambda build: 'control/'+build['filename']+'.control.tar.gz')
def build_control_file(build):
	# Get the `control.tar.gz` file from the package.
	# This is done by (very carefully!) downloading the file's header
	# (which is in Unix `ar` format) and parsing it to find out
	# where the control.tar.gz file is,
	# and then sending a separate request with the correct range
	# to obtain only the control.tar.gz file from the package.
	# The best way to understand this code (should you need to)
	# is probably to get a hexdump of a package, and read the header yourself.
	
	# First, obtain the relevant bits of the header, which happen to be
	# the first 132 bytes.
	rh = requests.get(build['url'], headers={'Range': 'bytes=0-131'})
	rh.raise_for_status()
	# Then, sanity check and parse the response
	head = rh.content
	assert head[0:8] == '!<arch>\n' # AR file header
	## First file ##
	assert head[8:24] == 'debian-binary/  ' # File name
	# head[24:36] (Skip timestamp)
	assert head[36:56] == '0     0     100644  ' # Owner, group, mode
	assert head[56:68] == '4         `\n' # Length: 4 bytes
	assert head[68:72] == '2.0\n' # Contents of file
	## Second file ##
	assert head[72:88] == 'control.tar.gz/ ' # File name
	# head[88:100] (Skip timestamp)
	assert head[100:120] == '0     0     100644  ' # Owner, group, mode
	control_length = int(head[120:130]) # This is the bit we need
	assert head[130:132] == '`\n' # End of header record
	
	# Finally, send a request for the control.tar.gz file,
	# which begins immediately after the header we just read
	# and continues for control_length more bytes.
	rc = requests.get(build['url'], headers={'Range': 'bytes=132-'+str(control_length+132)})
	rc.raise_for_status()
	return rc.content

def build_control_entry(build, entry):
	build_control_file(build)
	with tarfile.open('cache/control/'+build['filename']+'.control.tar.gz', 'r:gz') as tf:
		return tf.extractfile('./'+entry).read()

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
