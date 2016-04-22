#!/usr/bin/env python

import os
import tempfile
import sys

srctop = os.path.abspath (os.path.realpath(__file__) + '/../../../')
sys.path.append (srctop)
from deployment.config import *

# Write the configuration file
config = open('%s/src/queue/cherokee.conf.orig'%(srctop), 'r').read()
config = config.replace ('${tmp}', srctop)

tempfd, cherokee_conf = tempfile.mkstemp()
os.write(tempfd, config)
os.close(tempfd)

# Launch the server
command = "%s/sbin/cherokee -C %s" %(BASE_DIR, cherokee_conf)

print "CWD:      ", os.getcwd()
print "Executing:", command
os.system(command)
