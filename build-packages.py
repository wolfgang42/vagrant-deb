#!/usr/bin/env python2
import sys
import json
import releaseinfo

with open('cache/releases.json') as f:
	releases = json.load(f)

ARCH_SYNONYM = {
	'i386': 'i686',
	'amd64': 'x86_64',
}

def get_build(release, arch):
	for build in release['builds']:
		if build['os'] == 'debian' and build['arch'] == ARCH_SYNONYM[arch]:
			return build

def shasums(release):
	releaseinfo.check_shasums_sig(release)
	ret = {}
	for line in releaseinfo.release_shasums(release).split('\n'):
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
			sys.stdout.write(releaseinfo.build_control_entry(build, 'control'))
			poolname = "pool/any/main/"+program[0]+"/"+program+"/"+program+"_"+version+"_"+arch+".deb"
			redirects.write('rewrite ^/'+poolname+' '+build['url']+' permanent;\n')
			print "Filename:", poolname
			print "SHA256:", shasums(release)[build['filename']]
			print "Size:", releaseinfo.build_size(build)
			print
