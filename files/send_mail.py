#!/usr/bin/python3

import sys

f = open("/srv/zimbraweb/pipe.log", "a")
f.write(str(sys.stdin.read()))
f.close()