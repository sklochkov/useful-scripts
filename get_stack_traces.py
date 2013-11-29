#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import re
import subprocess
import hashlib
import sys


EXCEPTION_RE = re.compile("""(Exception|Error):""")
SUPP_EXCE_RE = re.compile("""^(java|com|org|javax)\.[\w\.]+?Exception.*""")
STACK_RE = re.compile("""^\s*at""")

MTAIL = "/work/scripts/mon/mtail.sh"
#MTAIL = "/home/klochkov/iqbuzz-monitoring-scripts/mtail.sh"
APP_NAME = "get_stack_traces.sh"

def usage():
	print "%s <log> [exclude list]" % sys.argv[0]

def prepare_excludes(excludes):
	if excludes == None:
		return None
	try:
		f = open(excludes, 'r')
	except:
		return None
	res = []
	for line in f:
		res.append(re.compile(line.strip()))
	return res

def get_stack_traces(log, app, exclude=None):
	p = subprocess.Popen(args="%s '%s' '%s'" % (MTAIL, log, app), shell=True, stdout=subprocess.PIPE)
	in_block = 0
	blocks = {}
	chksums = {}
	block = ""
	stack = ""
	prev_line = ""
	for line in p.stdout:
		line = line.strip()
		if in_block == 0:
			if re.search(EXCEPTION_RE, line) and not re.search(STACK_RE,line):
				found = 0
				if exclude != None:
					for pattern in exclude:
						if re.search(pattern, line):
							found = 1
							break
				if found == 0:
					block = prev_line + "\n" + line + "\n"
					in_block = 1
		else:
			if re.search(STACK_RE, line):
				block = block + line + "\n"
				stack = stack + line + "\n"
			elif re.match(SUPP_EXCE_RE, line):
				block = block + line + "\n"
			else:
				in_block = 0
				hash = hashlib.md5(stack).hexdigest()
				if hash not in chksums:
					chksums[hash] = 1
				else:
					chksums[hash] += 1
				if hash not in blocks:
					blocks[hash] = block
				block = ""
				stack = ""
		prev_line = line
	for hash, repeated in chksums.iteritems():
		print blocks[hash],
		print "Repeated %s times\n" % repeated


if __name__ == "__main__":
	#MTAIL = "/home/klochkov/iqbuzz-monitoring-scripts/mtail.sh"
	try:
        	log = sys.argv[1]
	except:
        	usage()
	        sys.exit(1)
	try:
        	excl = sys.argv[2]
	except:
        	excl = None
	exclude_list = prepare_excludes(excl)
	get_stack_traces(log, APP_NAME, exclude_list)

