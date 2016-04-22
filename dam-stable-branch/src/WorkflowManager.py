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
import Role
import CTK
import Profile
import Auth
import Workflow

def steer (filename):
    """Given an input page and role, return a destination"""

    page       = __get_page_name (filename)
    user       = Auth.get_user()
    roles      = Role.get_user_roles ()

    request    = CTK.request.url
    params     = request.split('/')[-1]
    profile_name = '__default__'
    profile_id = user.get('profile_id')
    user_id    = user.get('id')
    user_name  = user.get('username')

    profiles = Profile.get_profiles ()
    for x in profiles:
        if x['id'] == profile_id:
            profile_name = x['name']
            break

    entry = Workflow.SCRIPT[page]
    if profile_name in entry:
        destination = entry[profile_name] % locals()
    else:
        destination = entry['__default__'] % locals()

    return CTK.HTTP_Redir (destination)

def __get_page_name (filename):
    basename = os.path.basename (filename)
    name,ext = os.path.splitext (basename)
    return name

def test():
    assert __get_page_name(__file__) == 'WorkflowManager'
    print '__get_page_name() --> OK'
    #steer()                 --> Cannot be tested as standalone

if __name__=='__main__':
    test()
