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

import os
import sys
import imp
import string
import traceback

from consts import *
from Widget import Widget
from Container import Container
from Combobox import ComboCfg
from Server import cfg, publish, post
from PageCleaner import Postprocess
from Help import HelpEntry, HelpGroup


SELECTOR_CHANGED_JS = """
/* On selector change
 */
$('#%(id)s').bind ('change', this, function() {
    info = {'%(key)s': $('#%(id)s')[0].value };
    $.ajax ({url:      '%(url)s',
             type:     'POST',
	     async:     true,
	     data:      info,
             success:  function(data) {
                 $('#%(plugin_id)s').html(data);
		 $('#%(id)s').trigger('changed');
             },
             error: function (xhr, ajaxOptions, thrownError) {
		 alert ("Error: " + xhr.status +"\\n"+ xhr.statusText);
             }
    });

   /* Update the Help menu
    */
   Help_update_group ('%(key)s', $('#%(id)s')[0].value);
});

/* Help: Initial status
 */
Help_update_group ('%(key)s', $('#%(id)s')[0].value);
"""


class Plugin (Container):
    def __init__ (self, key):
        Container.__init__ (self)

        self.key = key
        self.id  = "Plugin_%s" %(self.uniq_id)


class PluginInstanceProxy:
    def __call__ (self, key, modules, **kwargs):
        # Update the configuration
        if not key in post.keys():
            return ''

        new_val = post.get_val (key)
        cfg[key] = new_val

        if not new_val:
            return ''

        # Instance the content
        plugin = instance_plugin (new_val, key, **kwargs)
        if not plugin:
            return ''

        # Render it
        render = plugin.Render()

        output  = '<div id="%s">%s</div>' %(plugin.id, render.html)
        if render.js:
            output += HTML_JS_ON_READY_BLOCK %(render.js)

        return Postprocess(output)


class PluginSelector (Widget):
    def __init__ (self, key, modules, **kwargs):
        def key_to_url (key):
            return ''.join ([('_',c)[c in string.letters + string.digits] for c in key])

        Widget.__init__ (self)

        # Properties
        self._key   = key
        self._mods  = modules
        self._url   = '/plugin_content_%s' %(key_to_url(key))
        active_name = cfg.get_val (self._key)

        # Widgets
        self.selector_widget = ComboCfg (key, modules)
        self.plugin          = instance_plugin (active_name, key, **kwargs)

        # Register hidden URL for the plugin content
        publish (self._url, PluginInstanceProxy, key=key, modules=modules, method='POST', **kwargs)

    def _get_helps (self):
        global_key  = self._key.replace('!','_')
        global_help = HelpGroup(global_key)

        for e in self._mods:
            name, desc = e
            module = load_module (name, 'plugins')
            if module:
                if 'HELPS' in dir(module):
                    help_grp = HelpGroup (name)
                    for entry in module.HELPS:
                        help_grp += HelpEntry (entry[1], entry[0])
                    global_help += help_grp

        return [global_help]

    def Render (self):
        # Load the plugin
        render = self.plugin.Render()

        # Warp the content
        render.html = '<div id="%s">%s</div>' %(self.plugin.id, render.html)

        # Add the initialization Javascript
        render.js += SELECTOR_CHANGED_JS %({
                'id':        self.selector_widget.id,
                'url':       self._url,
                'plugin_id': self.plugin.id,
                'key':       self._key})

        # Helps
        render.helps = self._get_helps()
        return render


# Helper functions
#

def load_module (name, dirname):
    # Sanity check
    if not name:
        return

    # Figure the path to admin's python source (hacky!)
    stack = traceback.extract_stack()

    if 'pyscgi.py' in ' '.join([x[0] for x in stack]):
        for stage in stack:
            if 'CTK/pyscgi.py' in stage[0]:
                base_dir = os.path.join (stage[0], '../../..')
                break
    else:
        base_dir = os.path.dirname (stack[0][0])

    mod_path = os.path.abspath (os.path.join (base_dir, dirname))
    fullpath = os.path.join (mod_path, "%s.py"%(name))

    # Shortcut: it might be loaded
    if sys.modules.has_key (name):
        if sys.modules[name].__file__ == fullpath:
            return sys.modules[name]

    # Load the plug-in
    fullpath = os.path.join (mod_path, "%s.py"%(name))

    try:
        return imp.load_source (name, fullpath)
    except IOError:
        print "Could not load '%s'." %(fullpath)
        raise


def instance_plugin (name, key, **kwargs):
    # Load the Python module
    module = load_module (name, 'plugins')
    if not module:
        # Instance an empty plugin
        plugin = Plugin(key)
        return plugin

    # Instance an object
    class_name = 'Plugin_%s' %(name)
    obj = module.__dict__[class_name](key, **kwargs)
    return obj
