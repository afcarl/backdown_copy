#test main for backdown

import backdown
import sys


argv = sys.argv
if not len(argv) >= 3:
	print "USAGE: test.py INPUT KEY OUTPUT"
print backdown.backdown([argv[1], argv[2]], "nope", argv[3])