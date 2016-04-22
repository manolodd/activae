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

def get_type_name (type_id):
    l = get_type (type_id)
    if not l:
        return None
    return l['name']

def get_type (type_id):
    q = "SELECT id, type "\
        "FROM asset_types WHERE id=%(type_id)s;" % locals()

    query = Query(q)
    if len(query) != 1:
        return None

    ret = {'id':          type_id,
           'name':        query['type'][0]}
    return ret

def get_types ():
    q = "SELECT id, type "\
        "FROM asset_types;" % locals()

    query = Query(q)

    if not len(query):
        return None

    ret = []
    for x in query:
        d={'id':          query[x]['id'],
           'name':        query[x]['type']}
        ret.append(d)
    return ret


def test ():
    import sys

    try:
        type_id = sys.argv[1]
    except IndexError:
        print 'Required test parameters: type_id'
        sys.exit(1)

    print 'Types:', get_types()
    print 'type_id %s, type_name %s' % (type_id, get_type_name(type_id))
    print get_type(type_id),

if __name__ == '__main__':
    test()
