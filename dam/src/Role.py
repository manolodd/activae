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
import CTK
from DBSlayer import Query

# Constants
ROLE_ADMIN     = 1
ROLE_UPLOADER  = 2
ROLE_EDITOR    = 3
ROLE_PUBLISHER = 4
ROLE_CONSUMER  = 5

def role_to_name (role_id):
    rid = int(role_id)
    if rid == ROLE_ADMIN:
        return "Administrator"
    elif rid == ROLE_UPLOADER:
        return "Ingestador"
    elif rid == ROLE_EDITOR:
        return "Editor"
    elif rid == ROLE_PUBLISHER:
        return "Publicador"
    elif rid == ROLE_CONSUMER:
        return "Consumidor"

    assert False, "Unknown role"

def name_to_role (name):
    if name == "Administrator":
        return ROLE_ADMIN
    elif name == "Ingestador":
        return ROLE_UPLOADER
    elif name == "Editor":
        return ROLE_EDITOR
    elif name == "Publicador":
        return ROLE_PUBLISHER
    elif name == "Consumidor":
        return ROLE_CONSUMER

    assert False, "Unknown role"


def user_has_role (role, user=None, check_auth = True):
    if check_auth: # This is disabled on unit tests
        # Is he logged?
        auth = Auth.Auth()
        if not auth.is_logged_in():
            return False

    if not user:
        user = CTK.cookie['user']

    q = ("SELECT COUNT(*) " +
         "FROM users JOIN profiles ON users.profile_id = profiles.id " +
         "           JOIN profiles_has_roles ON profiles.id = profiles_has_roles.profiles_id " +
         "WHERE users.username = '%(user)s' AND profiles_has_roles.roles_id = %(role)d;") %(locals())

    if Query(q)['COUNT(*)'][0] != 1:
        return False

    return True

def user_has_roles (role_list, user=None):
    """Find out if user has at least one role"""
    assert(type(role_list) == list)

    for x in role_list:
        if user_has_role (x,user):
            return True
    return False

def get_user_roles (user=None):
    if not user:
        user = CTK.cookie['user']

    q = ("SELECT roles_id AS roles FROM users "
         "JOIN profiles ON users.profile_id = profiles.id "
         "JOIN profiles_has_roles "
         "ON profiles.id = profiles_has_roles.profiles_id "
         "WHERE users.username = '%s';" % user)
    query = Query(q)
    if len(query):
        return query['roles']
    return []

def test ():
    import sys

    try:
        user = sys.argv[1]
    except IndexError:
        print 'Required test parameters: user_name'
        sys.exit(1)

    user_roles = get_user_roles (user)

    print 'User roles:', user_roles
    for role in user_roles:
        print 'User has role %s' % role, user_has_role (role, user, False)

    print 'User has role INVENTED', user_has_role (0, user, False)

if __name__ == '__main__':
    test()
