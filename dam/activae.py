#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010 CENATIC: Centro Nacional de Referencia de
# Aplicacion de las TIC basadas en Fuentes Abiertas, Spain.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
#   Neither the name of the CENATIC nor the names of its contributors
#   may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# You may contact the copyright holder at: Fundacion CENATIC, Edificio
# de Servicios Sociales: C/ Vistahermosa, 1, 3ra planta, 06200
# Almendralejo (Badajoz), Spain

import os
import sys
import getopt
from deployment.config import *

USAGE_MSG = """Activae v1.0
Usage: %s [param]

  --help               Print this message
  --frontend           Run main load-balancing Activae instance
  --queue              Run main balancer for XMLRPC transcoding queue
  --database           Run main database load-balancer
  --search             Publish local XMLRPC search API
  --web                Launch Activae local instance on default port
  --transcoder         Launch instance of local transcoder
  --debug              Show additional debug information
"""

def run (message, command):
    print "CWD:      ", os.getcwd()
    print "Launching:", message
    print "Executing:", command
    return os.system(command)

def main():
    try:
        opts, args = getopt.getopt (sys.argv[1:], '',
                                    ["help", "frontend", "database", "search", "queue", "web", "transcoder=", "debug"])

    except getopt.GetoptError, err:
        print "ERROR: %s\n" % (str(err))
        print_usage()
        sys.exit(2)

    SRC_DIR = os.path.dirname (os.path.abspath (os.path.realpath(__file__)))

    debug = bool (filter (lambda x:'debug' in x[0], opts))
    message, command = None, None

    for o, arg in opts:
        if o == "--database":
            message = 'Database load balancer'
            command = '%s/sbin/cherokee -C %s/database/cherokee.conf > /dev/null 2>&1'%(BASE_DIR, BASE_DIR)
        elif o == "--frontend":
            message = 'Main Activae load balancer'
            command = '( %s/frontend/run.py  > /dev/null 2>&1 )'%(SRC_DIR)
        elif o == "--search":
            message = 'Local search API'
            command = '( cd %s/src && python ActivaeXMLRPC.py > /dev/null 2>&1 )'%(SRC_DIR)
        elif o == "--queue":
            message = 'Main transcoding queue balancer'
            command = '%s/src/queue/run.py > /dev/null 2>&1'%(BASE_DIR)
        elif o == "--web":
            message = 'Local Activae instance'
            command = '( cd %s/src/CTK_trunk/tests/ && ./run.py ../../main.py >> %s 2>&1 )'%(SRC_DIR, LOG_ACTIVAE)
            if debug:
                command = '( cd %s/src/CTK_trunk/tests/ && ./run.py ../../main.py )'%(SRC_DIR)
        elif o == "--transcoder":
            message = 'Local transcoding-queue worker'
            command = '( cd %s/src/queue/ && python main.py --worker=%s >> %s 2>&1 )'%(SRC_DIR, arg, LOG_ACTIVAE)
            if debug:
                command = '( cd %s/src/queue/ && python main.py --worker=%s )'%(SRC_DIR, arg)
        elif o == "--help":
            return print_usage()
        elif o == "--debug":
            pass
        else:
            assert False, "Unhandled option: %s" %(o)

    if message and command:
        return run (message, command)
    return print_usage()

def print_usage():
    print USAGE_MSG % sys.argv[0]

if __name__ == "__main__":
    main()
