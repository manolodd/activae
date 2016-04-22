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
import time
import subprocess
import sys
sys.path.append("..")
import config

def log (msg):
    txt = '%s - %s\n' % (time.asctime(), msg)
    print txt,

    f = open (config.LOG_QUEUE, "a+")
    f.write (txt)
    f.flush()
    f.close()

def exe_output (cmd):
    re = ""

    p = subprocess.Popen (cmd, shell=True, stdout=subprocess.PIPE)
    while True:
        line = p.stdout.readline()
        if not line:
            break
        re += line

    p.wait()
    return re


def exe (cmd, log_file = config.LOG_QUEUE):
    # Log the command being executed
    if log_file:
        print cmd
        log_obj = open (log_file, "a+")
        log_obj.write ("%s\n" %(cmd))
        log_obj.flush()

    # Execute the command
    p = subprocess.Popen (cmd, shell=True, stdout=subprocess.PIPE)
    while True:
        line = p.stdout.readline()
        if not line:
            break

        # Print and log
        print line.rstrip('\n\r')
        if log_file:
            log_obj.write(line)
            log_obj.flush()

    # Close and report exit code
    if log_file:
        log_obj.close()

    p.wait()
    return p.returncode == 0

def local_reference (url):
    # Local file
    if url.startswith('file:'):
        tmp = url[5:]
        while tmp[0] == '/':
            tmp = tmp[1:]
        return '/' + tmp

    elif url.startswith('/') or url.startswith('~'):
        return url

    # HTTP reference
    if url.startswith('http:'):
        filename = url.split('/')[-1]
        filepath = os.path.join (config.CACHE_PATH, filename)

        exe ("mkdir -p '%s'" % (config.CACHE_PATH))
        exe ("wget --continue -O '%s' '%s' --append-output='%s'" % (filepath, url, config.LOG_QUEUE))

        return filepath

    print "?????"
    return "??"
