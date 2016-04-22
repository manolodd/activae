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

from Box import Box
from Button import Button
from Refreshable import RefreshableURL
from Server import request

JS_BUTTON_GOTO = """
var druid      = $(this).parents('.druid:first');
var refresh    = druid.find('.refreshable-url');
var submitters = refresh.find('.submitter');

// No Submit
if ((! %(do_submit)s) || (submitters.length == 0))
{
   refresh.trigger({'type':'refresh_goto', 'goto':'%(url)s'});
   return;
}

// Submit
submitters.bind ('submit_success', function (event) {
   $(this).unbind (event);
   if ('%(url)s'.length > 0) {
      refresh.trigger({'type':'refresh_goto', 'goto':'%(url)s'});
   } else {
      druid.trigger('druid_exiting');
   }
});

submitters.bind ('submit_fail', function (event) {
   $(this).unbind (event);
});

submitters.trigger ({'type': 'submit'});
"""

JS_BUTTON_CLOSE = """
$(this).parents('.ui-dialog-content:first').dialog('close');
return false;
"""


class Druid (Box):
    def __init__ (self, refreshable, _props={}):
        # Properties
        props = _props.copy()
        if 'class' in props:
            props['class'] += ' druid'
        else:
            props['class'] = 'druid'

        # Parent's constructor
        Box.__init__ (self, props)

        # Widget
        assert isinstance (refreshable, RefreshableURL)
        self.refreshable = refreshable
        self += self.refreshable

    def JS_to_goto (self, url):
        props = {'refresh': self.refreshable.id,
                 'url':     url}
        return "$('#%(refresh)s').trigger({'type':'refresh_goto', 'goto': %(url)s});" %(props)


#
# Buttons
#

class DruidButton (Button):
    def __init__ (self, caption, url, _props={}):
        # Properties
        props = _props.copy()
        if 'class' in props:
            props['class'] += ' druid-button'
        else:
            props['class'] = 'druid-button'

        # Parent's constructor
        Button.__init__ (self, caption, props.copy())

class DruidButton_Goto (DruidButton):
    def __init__ (self, caption, url, do_submit, _props={}):
        DruidButton.__init__ (self, caption, url, _props.copy())

        props = {'url':       url,
                 'do_submit': ('false', 'true')[do_submit]}

        # Event
        self.bind ('click', JS_BUTTON_GOTO %(props))

class DruidButton_Close (DruidButton):
    def __init__ (self, caption, _props={}):
        DruidButton.__init__ (self, caption, _props.copy())

        # Event
        self.bind ('click', JS_BUTTON_CLOSE)

class DruidButton_Submit (DruidButton):
    def __init__ (self, caption, _props={}):
        DruidButton.__init__ (self, caption, _props.copy())

        props = {'url':       '',
                 'do_submit': 'true'}

        # Event
        self.bind ('click', JS_BUTTON_GOTO%(props))

#
# Button Panels
#

class DruidButtonsPanel (Box):
    def __init__ (self, _props={}):
        # Properties
        props = _props.copy()
        if 'class' in props:
            props['class'] += ' druid-button-panel'
        else:
            props['class'] = 'druid-button-panel'

        # Parent's constructor
        Box.__init__ (self, props)
        self.buttons = []

class DruidButtonsPanel_Next (DruidButtonsPanel):
    def __init__ (self, url, cancel=True, do_submit=True, props={}):
        DruidButtonsPanel.__init__ (self, props.copy())
        if cancel:
            self += DruidButton_Close(_('Cancel'))
        self += DruidButton_Goto (_('Next'), url, do_submit)

class DruidButtonsPanel_PrevNext (DruidButtonsPanel):
    def __init__ (self, url_prev, url_next, cancel=True, do_submit=True, props={}):
        DruidButtonsPanel.__init__ (self, props.copy())
        if cancel:
            self += DruidButton_Close(_('Cancel'))
        self += DruidButton_Goto (_('Next'), url_next, do_submit)
        self += DruidButton_Goto (_('Prev'), url_prev, False)

class DruidButtonsPanel_PrevCreate (DruidButtonsPanel):
    def __init__ (self, url_prev, cancel=True, props={}):
        DruidButtonsPanel.__init__ (self, props.copy())
        if cancel:
            self += DruidButton_Close(_('Cancel'))
        self += DruidButton_Submit (_('Create'))
        self += DruidButton_Goto (_('Prev'), url_prev, False)

class DruidButtonsPanel_Create (DruidButtonsPanel):
    def __init__ (self, cancel=True, props={}):
        DruidButtonsPanel.__init__ (self, props.copy())
        if cancel:
            self += DruidButton_Close(_('Cancel'))
        self += DruidButton_Submit (_('Create'))

class DruidButtonsPanel_Cancel (DruidButtonsPanel):
    def __init__ (self, props={}):
        DruidButtonsPanel.__init__ (self, props.copy())
        self += DruidButton_Close(_('Cancel'))


#
# Helper
#
def druid_url_next (url):
    parts = url.split('/')

    try:
        num = int(parts[-1])
    except ValueError:
        return '%s/2' %(url)

    return '%s/%d' %('/'.join(parts[:-1]), num+1)

def druid_url_prev (url):
    parts = url.split('/')
    num = int(parts[-1])

    if num == 2:
        return '/'.join(parts[:-1])
    return '%s/%d' %('/'.join(parts[:-1]), num-1)


class DruidButtonsPanel_Next_Auto (DruidButtonsPanel_Next):
    def __init__ (self, **kwargs):
        kwargs['url'] = druid_url_next(request.url)
        DruidButtonsPanel_Next.__init__ (self, **kwargs)

class DruidButtonsPanel_PrevNext_Auto (DruidButtonsPanel_PrevNext):
    def __init__ (self, **kwargs):
        kwargs['url_prev'] = druid_url_prev(request.url)
        kwargs['url_next'] = druid_url_next(request.url)
        DruidButtonsPanel_PrevNext.__init__ (self, **kwargs)

class DruidButtonsPanel_PrevCreate_Auto (DruidButtonsPanel_PrevCreate):
    def __init__ (self, **kwargs):
        kwargs['url_prev'] = druid_url_prev(request.url)
        DruidButtonsPanel_PrevCreate.__init__ (self, **kwargs)
