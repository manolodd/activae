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
import random
import string

try:
    from hashlib import sha256 as sha, md5
except:
    from md5 import md5
    from sha import sha

import CTK
import Role
import Error
from DBSlayer import Query

EXPIRATION   = 6 * 60*60 # 6h


class Auth:
    def __init__ (self):
        None

    def is_logged_in (self):
        user = CTK.cookie['user']
        vali = CTK.cookie['validation']
        now  = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

        if not user or not vali:
            return False

        q = ("SELECT COUNT(*) FROM sessions WHERE user = '%(user)s' AND " +
             "validation = '%(vali)s' AND expiration > '%(now)s';") % (locals())

        if Query(q)['COUNT(*)'][0] != 1:
            return False

        return True

    def auth (self, user, password, client_ip):
        # Sanity check
        if not user or not password:
            return False

        hashed_password =  md5(password).hexdigest()

        # Check the database
        q = "SELECT COUNT(*) FROM users " + \
            "WHERE username='%(user)s' AND password='%(hashed_password)s';" %(locals())

        if Query(q)['COUNT(*)'][0] != 1:
            return False

        # Set cookie
        random_str = ''.join ([random.choice(string.letters) for x in range(30)])
        cookie_raw = random_str + client_ip
        cookie = sha(cookie_raw).hexdigest()

        CTK.cookie['validation'] = cookie  + "; path=/; HttpOnly"
        CTK.cookie['user']       = user    + "; path=/; HttpOnly"

        # Save the session
        exp_time   = time.time() + EXPIRATION
        expiration = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(exp_time))

        q = "REPLACE INTO sessions (user, validation, expiration) " +\
            "VALUES ('%(user)s','%(cookie)s','%(expiration)s');" %(locals())

        Query(q)
        return True

    def deauth (self):
        user = CTK.cookie['user']
        vali = CTK.cookie['validation']

        if not user or not vali:
            return False

        q = ("DELETE FROM sessions WHERE " +
             "  user = '%(user)s' AND validation = '%(vali)s';") %(locals())

        Query(q)
        return True


#
# Convenience functions
#
def assert_is_role (x):
    # Is he logged?
    auth = Auth()
    if not auth.is_logged_in():
        return CTK.HTTP_Redir('/auth')

    # Check the roles
    if type(x) == int:
        if Role.user_has_role (x):
            return None # ok
    elif type(x) == list:
        for role in x:
            if Role.user_has_role (role):
                return None # ok

    # Does not have the role
    return CTK.HTTP_Redir('/')

def get_user_id (username = None):
    if username == None:
        username = CTK.cookie['user']
    q = "SELECT id FROM users WHERE username='%s';" % username
    query = Query(q)

    if len(query) == 1:
        return query['id'][0]
    return None

def get_user_name (user_id = None):
    if user_id == None:
        return CTK.cookie['user']

    q = "SELECT username FROM users WHERE id='%s';" % user_id
    query = Query(q)
    if len(query) == 1:
        return query['username'][0]
    return None

def get_users ():
    q = "SELECT id, username FROM users;"
    query = Query(q)
    return [(query['id'][x], query['username'][x]) for x in query]

def get_user (username = None):
    if username == None:
        username = CTK.cookie['user']

    if not username:
        return {}

    q = "SELECT * FROM users WHERE username='%s';" % username

    query = Query(q)
    user = {}
    try:
        for key in query.get_headers():
            user[key] = query[0][key]
    except:
        pass

    return user

def check_if_authorized (content):
    """Checks"""
    if Role.user_has_role (Role.ROLE_ADMIN):
        return # OK

    if Role.user_has_role (Role.ROLE_UPLOADER):
        user_id = get_user_id()
        if user_id == content['creator_id']:
            return

    raise Error.Unauthorized




def do_test (expected_result, func, *args):
    try:
        if args:
            ret = func(*args)
        else:
            ret = func()
        assert ret == expected_result
    except AttributeError: # Expected
        pass

def test ():
    import sys
    import Asset
    import OpAsset

    try:
        username = sys.argv[1]
    except:
        print 'Required test parameters: user'
        sys.exit(1)

    user        = get_user (username)
    assert user
    print '#1 get_user("%s") --> OK' % username

    test_string = 'phony'
    client_ip   = '127.0.0.1'
    password    = user['password']

    auth = Auth()
    do_test (False, auth.is_logged_in)
    print '#2 Auth.is_logged_in() (not_logged) == False --> OK'

    args = (test_string, test_string, client_ip)
    do_test (False, auth.auth, *args)
    print '#3 Auth.auth(phony_data) == False --> OK'

    args = (username, password, client_ip)
    do_test (True, auth.auth, *args)
    print '#4 Auth.auth(valida_data) == True --> OK'

    do_test (True, auth.is_logged_in)
    print '#5 Auth.is_logged_in() (logged) == True --> OK'

    do_test (True, auth.deauth)
    print '#6 Auth.deauth() (logged) == True --> OK'

    do_test (False, auth.is_logged_in)
    print '#7 Auth.is_logged_in() (not logged) == False --> OK'

    users = get_users ()
    usernames = [x[1] for x in users]
    assert username in usernames
    print '#8 get_users () --> OK'

    user_id = get_user_id (username)
    assert user_id == user['id']
    print '#9 get_user_id () --> OK'

    assert username == get_user_name (user_id)
    print '#10 get_user_name () --> OK'

if __name__ == '__main__':
    test()
