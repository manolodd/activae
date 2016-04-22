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

import Auth
import Error
from DBSlayer import Query

def get_profiles ():
    q = ('SELECT id, name, GROUP_CONCAT(roles_id) AS roles '
         'FROM profiles '
         'JOIN profiles_has_roles ON profiles_id=id '
         'GROUP by profiles.id;')
    query = Query(q)

    ret = []
    for x in query:
        roles = query[x]['roles'].split(',')
        roles = [int(r) for r in roles]
        d={'id':          query[x]['id'],
           'name':        query[x]['name'],
           'roles':       roles}
        ret.append(d)
    return ret

def get_user_profile (user_id = None):
    if not user_id:
        username = None
    else:
        username = Auth.get_user_name (user_id)
        if not username:
            raise Error.Invalid

    user = Auth.get_user (username)
    return user['profile_id']

def test ():
    import sys

    try:
        user_id = sys.argv[1]
    except IndexError:
        print 'Required test parameters: user_id'
        sys.exit(1)

    print 'Profiles:', get_profiles()
    print '\nuser_id %s, profile_id %s' % (user_id, get_user_profile(user_id))

if __name__ == '__main__':
    test()