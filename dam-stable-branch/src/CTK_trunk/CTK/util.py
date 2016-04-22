# -*- coding: utf-8 -*-
#
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
# You may contact the copyright holder at: Fundacion CENATIC, Avenida
# Clara Campoamor, s/n. 06200 Almendralejo (Badajoz), Spain
#
# NOTE: This version of CTK is a fork re-licensed by its author. The
#       mainstream version of CTK is available under a GPLv2 license
#       at the Cherokee Project source code repository.
#

import re

try:
    import json
except ImportError:
    import json_embedded as json

#
# Strings
#
def formater (string, props):
    """ This function does a regular substitution 'str%(dict)' with a
    little difference. It takes care of the escaped percentage chars,
    so strings can be replaced an arbitrary number of times."""

    s2 = ''
    n  = 0
    while n < len(string):
        if n<len(string)-1 and string[n] == string[n+1] == '%':
            s2 += '%%%%'
            n  += 2
        else:
            s2 += string[n]
            n  += 1

    return s2 %(props)

#
# HTML Tag properties
#
def props_to_str (props):
    assert type(props) == dict

    tmp = []
    for p in props:
        val = props[p]
        if val:
            tmp.append ('%s="%s"'%(p, val))
        else:
            tmp.append (p)

    return ' '.join(tmp)

#
# Copying and Cloning
#
def find_copy_name (orig, names):
    # Clean up name
    cropped = re.search (r' Copy( \d+|)$', orig) != None
    if cropped:
        orig = orig[:orig.rindex(' Copy')]

    # Find higher copy
    similar = filter (lambda x: x.startswith(orig), names)
    if '%s Copy'%(orig) in similar:
        higher = 1
    else:
        higher = 0

    for tmp in [re.findall(r' Copy (\d)+', x) for x in similar]:
        if not tmp: continue
        higher = max (int(tmp[0]), higher)

    # Copy X
    if higher == 0:
        return '%s Copy' %(orig)

    return '%s Copy %d' %(orig, higher+1)

#
# JSon
#
def json_dump (obj):
    # Python 2.6, and json_embeded
    if hasattr (json, 'dumps'):
        return json.dumps (obj)

    # Python 2.5
    return json.write(obj)
