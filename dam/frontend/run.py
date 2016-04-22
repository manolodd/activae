#!/usr/bin/env python

import os
import tempfile
import sys

srctop = os.path.abspath (os.path.realpath(__file__) + '/../../')
sys.path.append (srctop)
from deployment.config import *

# Temporal directory
tmpdir = os.getenv('TMPDIR', os.getenv('TEMP', os.getenv('TMP', '/tmp')))
alldir = '%s/cherokee/rrd-cache'%(tmpdir)

try:
    os.makedirs(alldir)
except:
    pass
finally:
    os.chmod(alldir,0775)

# Write the configuration file
config = open('%s/frontend/cherokee.conf.orig'%(srctop), 'r').read()
config = config.replace ('${tmp}',  tmpdir)
config = config.replace ('${path}', srctop)

tempfd, cherokee_conf = tempfile.mkstemp()
os.write(tempfd, config)
os.close(tempfd)

# Launch the server
command = "%s/sbin/cherokee -C %s" %(BASE_DIR, cherokee_conf)

print "CWD:      ", os.getcwd()
print "Executing:", command
os.system(command)
