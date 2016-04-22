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

from DBSlayer import Query

def get_license_name (license_id):
    l = get_license (license_id)
    if not l:
        return None
    return l['name']

def get_license (license_id):
    q = "SELECT id, name, description "\
        "FROM licenses WHERE id=%(license_id)s;" % locals()

    query = Query(q)
    if len(query) != 1:
        return None

    ret = {'id':          license_id,
           'name':        query['name'][0],
           'description': query['description'][0]}
    return ret

def test ():
    import sys

    try:
        license_id = sys.argv[1]
    except IndexError:
        print 'Required test parameters: license_id'
        sys.exit(1)

    print 'license_id %s, license_name %s' % (license_id, get_license_name(license_id))
    print get_license(license_id),

if __name__ == '__main__':
    test()
