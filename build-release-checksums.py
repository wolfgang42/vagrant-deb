#!/usr/bin/env python2
import os
import sys
import hashlib

HASHES = {
	'md5': 'MD5Sum',
	'sha1': 'SHA1',
	'sha256': 'SHA256',
	'sha512': 'SHA512',
}

for hash in HASHES:
	print HASHES[hash]+':'
	for filename in sys.argv[1:]:
		h = hashlib.new(hash)
		with open(filename) as f:
			h.update(f.read())
		print '', h.hexdigest(), os.stat(filename).st_size, filename
