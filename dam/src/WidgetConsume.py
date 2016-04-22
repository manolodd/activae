# -*- coding: utf-8 -*-
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

import mimetypes
import urllib
import CTK
import Asset
import Collection
import OpAsset
import Bookmark
import Auth
import Error
import os

from Widget import *
from CTK.consts import *
from config import *
from consts import *
import PageLookup

LOCATION     = '/consume'

TRANSCODING_NOTE = "Este activo no es accesible por estar en la cola de procesamiento"
TRANSCODING_LINK = "Procesando"
FAULTY_NOTE      = "Este activo parece estar en un estado inconsistente. Probablemente no pudo ser procesado de manera correcta por la cola de transcodificación y deba ser eliminado"
FAULTY_LINK      = "Inconsistente"

ABSTRACT_TEMPLATE = """
<dl class="abstract">
<dt class="title">%(title)s</dt>
<dt class="description">%(desc)s</dt>
<dt class="license">Licencia</dt><dd>%(license_name)s</dd>
<dt class="author">Autor</dt><dd>%(creator_name)s</dd>
</dl>
"""

VIDEO_TEMPLATE = """
<video controls width="%(width)s" height="%(height)s" autobuffer>
   <source src="%(file)s">
</video>
"""

FLASH_TEMPLATE = """
<script type="text/javascript" src="%(flow_js)s"></script>
<a href="%(file)s"
   style="display:block;width:%(width)spx;height:%(height)spx;"
   id="player">
</a>

<script language="JavaScript">
flowplayer("player", "%(player)s");
</script>
"""

AUDIO_TEMPLATE = """
<audio src="%(file)s" controls autobuffer></audio>
"""

DCMI2DB = {
    'Creator':          'creator_name',
    'Has Part':         'id',
    'Has Version':      'id',
    'Identifier':       'id',
    'Is Format Of':     'id',
    'Is Part Of':       'id',
    'Is Referenced By': 'collections_id',
    'Is Replaced By':   'id',
    'Is Version Of':    'id',
    'Publisher':        'publisher_name',
    'Relation':         'id',
    'Replaces':         'id',
    'Source':           'id',
}


RESIZE_WRAPPER_JS = """
<script type="text/javascript">
var Wrap = document.getElementById("wrap");
Wrap.style.width = "%spx";
</script>
"""

def _smart_truncate(content, length=DESCRIPTION_SZ, suffix='...'):
    if not content: return ''
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix


def get_meta_link (tag, value):
    """Adds the DCMI reference"""

    if not DCMI2DB.has_key(tag):
        return str(value)

    link = LINK_HREF % ("%s/%s=%s" % (PageLookup.LOCATION, DCMI2DB[tag], str(value)), str(value))

    return link

def add_meta_ref (tag, value):
    """Adds the DCMI reference"""
    link = get_meta_link (tag, value)
    return [CTK.RawHTML(tag), CTK.RawHTML(link)]


class AbstractWidget (InterfaceWidget):
    """Produce consume widget"""

    def __init__ (self, **kwargs):
        InterfaceWidget.__init__ (self)
        self.show = [0,1,2] # List of visible columns
        if 'show' in kwargs:
            self.show = kwargs['show']

    def Add (self, content):
        assert isinstance (content, Asset.Asset) or\
               isinstance (content, Collection.Collection)

        diz = content.get_diz()
        # Thumb
        thumb = CTK.RawHTML('<img src="%s" />' % (diz['thumb']))

        # Abstract
        creator_name = diz['creator']
        license_name = diz['license']
        title        = diz['title']
        desc         = _smart_truncate(diz['desc'])
        abstract     = CTK.RawHTML(ABSTRACT_TEMPLATE %locals())

        # Links
        links  = ActionsWidget()
        links.Add(content)

        table = CTK.Table()
        row = [thumb, links, abstract]
        row = [row[x] for x in self.show]
        table[(1,1)] = row
        self += table


class ActionsWidget (InterfaceWidget):
    """Produce block of display-actions that can be applied to a
    content. Those are: view metadata, download, view asset"""

    def __init__ (self, **kwargs):
        InterfaceWidget.__init__ (self)

    def Add (self, content):
        c_types = ['collection', 'asset']
        c_type  = c_types[isinstance (content, Asset.Asset)]

        c_id     = '%s=%s' % (c_type[0], str(content['id']))
        link     = LINK_HREF % ("%s/meta/%s" %(LOCATION,c_id),'Metadatos')
        links    = [CTK.RawHTML(link)]

        try:
            Auth.check_if_authorized (content)
            link = LINK_HREF % ("/acl/%s/%d" % (c_type, content['id']), 'Permisos')
            links.append(CTK.RawHTML(link))
        except Error.Unauthorized:
            pass

        if c_id[0] == 'c':
            link = LINK_HREF % ("%s/view/%s" % (LOCATION, c_id), 'Ver')
            links.append(CTK.RawHTML(link))

        elif c_id[0] == 'a':
            if content['attachment']:
                if not content._file['queue_flag']:
                    if self._has_valid_attachment (content):
                        links = links + self._get_attachment_links(content, c_id)
                    else:
                        # Error notice
                        dialog = CTK.Dialog ({'title': 'Activo #%d corrupto'%content['id'], 'autoOpen': False})
                        dialog += CTK.RawHTML (FAULTY_NOTE)
                        dialog.AddButton ('Cerrar', "close")
                        link = LINK_JS_ON_CLICK %(dialog.JS_to_show(), FAULTY_LINK)
                        self += dialog
                        links.append(CTK.RawHTML(link))
                else:
                    # Transcoding notice
                    dialog = CTK.Dialog ({'title': 'Procesando #%d...'%content['id'], 'autoOpen': False})
                    dialog += CTK.RawHTML (TRANSCODING_NOTE)
                    dialog.AddButton ('Cerrar', "close")
                    link = LINK_JS_ON_CLICK %(dialog.JS_to_show(), TRANSCODING_LINK)
                    self += dialog
                    links.append(CTK.RawHTML(link))

            links.append (self._get_bookmark_link (content['id']))

        table = CTK.Table({'class':"abstract_actions"})
        n = 1
        for link in links:
            table[(n,1)] = link
            n+=1
        self+= table

    def _has_valid_attachment (self, asset):
        try:
            filename = asset._file['filename']
            fullname = os.path.join(ASSET_PATH, filename)
            if os.path.getsize (fullname):
                return True
        except:
            pass
        return False

    def _get_attachment_links (self, content, c_id):
        links  = []
        url    = "%s/view/%s" % (LOCATION, c_id)
        link   = LINK_HREF % (url, 'Ver')
        links.append(CTK.RawHTML(link))
        if content['attachment']:
            url    = "%s/link/%d/%s"% (STATIC_PRIVATE, content['id'], content['attachment'])
            link   = LINK_HREF % (url, 'Enlace')
            links.append(CTK.RawHTML(link))
        return links


    def _get_bookmark_link (self, asset_id):
        bookmark = (asset_id, Auth.get_user_id())
        ref   = urllib.unquote_plus(CTK.request.url)
        flag  = Bookmark.bookmark_exists (bookmark)
        table = CTK.Table ()
        table [(1,1)] = CTK.RawHTML('Favorito')
        table [(1,2)] = CTK.Checkbox({'name': 'bookmark', 'checked': flag})

        submit = '/bookmark/%s;%s' % (asset_id, ref)
        form   = CTK.Submitter (submit)
        form  += table
        return form


class MetaWidget (InterfaceWidget):
    """Produce block with metadescriptors"""

    def __init__ (self, **kwargs):
        InterfaceWidget.__init__ (self)

    def Add (self, content):
        assert isinstance (content, Asset.Asset) or\
            isinstance (content, Collection.Collection)

        if isinstance (content, Asset.Asset):
            self._update_views(content['id'])

        tags = content.get_tags()
        table = CTK.Table()
        n=1

        for tag, data in tags.items():
            if type(data) == list:
                for x in data:
                    table[(n,1)] = add_meta_ref(tag, x)
                    n+=1
            else:
                table[(n,1)] = add_meta_ref(tag, data)
                n+=1

        self += table


    def _update_views (self, asset_id):
        asset = Asset.Asset(asset_id)
        asset['views'] += 1
        oa = OpAsset.OpAsset(asset)
        rc = oa.update()
        if not rc:
            raise SQLException


class ViewWidget (InterfaceWidget):
    """Produce embeddable view"""

    def __init__ (self, **kwargs):
        InterfaceWidget.__init__ (self)

    def Add (self, content):
        if isinstance (content, Collection.Collection):
            self.widget_collection(content)

        elif isinstance (content, Asset.Asset):
            self.widget_asset(content)

        else:
            raise TypeError

    def widget_collection (self, content):
        self += CTK.RawHTML("<h2>%s %s</h2>" % (BACK_LINK, content['name']))

        assets = [(Asset.Asset,x) for x in content['assets']]
        self += Paginate(assets, AbstractWidget)


    def widget_asset (self, content):
        table = CTK.Table()

        if not content['attachment']:
            return

        asset_title = content['tags']['Title']
        format      = content['tags']['Format']
        extent      = content['tags']['Extent']
        description = content['tags']['Description']
        extra = filter(lambda x:x, [format, extent])

        if extra:
            asset_title += '(%s)' % (', '.join(extra))

        player = self._get_player (content)
        url    = "%s/link/%d/%s"% (STATIC_PRIVATE, content['id'], content['attachment'])
        link   = '%s<br/>' % LINK_HREF%(url,'Enlace')

        table = CTK.Table()
        table[(1,1)] = CTK.RawHTML("<h2>%s %s</h2>" % (BACK_LINK, asset_title))
        table[(2,1)] = CTK.RawHTML(player)
        table[(3,1)] = CTK.RawHTML(link)
        table[(4,1)] = CTK.RawHTML("<p>%s</p>" % description)

        self += table


    def _get_player (self, content):
        filename = content['attachment']
        mimetype, encoding = mimetypes.guess_type (filename)

        data = content._file.copy()
        for key,val in data.items():
            if not val:
                del(data[key])

        resize = ''
        try:
            width = data.get('width',0)
            if width + SIDEBAR_WIDTH > WRAPPER_WIDTH:
                resize = RESIZE_WRAPPER_JS % (width + SIDEBAR_WIDTH)
        except:
            pass

        lst = ['video/mp4', 'video/ogg']
        if mimetype in lst:
            d = { 'width':  data.get('width',  FLOW_WIDTH),
                  'height': data.get('height', FLOW_HEIGHT),
                  'file':   "%s/assets/%d" % (STATIC_PRIVATE, content['id'])}
            return resize + VIDEO_TEMPLATE % d

        lst = ['video/x-flv']
        if mimetype in lst:
            # Flowplayer is said to support: FLV, SWF, MP3, MP4, H.264 video

            d = { 'width':  data.get('width',  FLOW_WIDTH),
                  'height': data.get('height', FLOW_HEIGHT),
                  'file':   "%s/assets/%d" % (STATIC_PRIVATE, content['id']),
                  'player': FLOW_PLAYER,
                  'flow_js':FLOW_JS }

            return resize + FLASH_TEMPLATE % d

        lst = ['audio/ogg', 'audio/mpeg']
        if mimetype in lst:
            d = { 'file':   "%s/assets/%d" % (STATIC_PRIVATE, content['id'])}
            return AUDIO_TEMPLATE % d

        lst = ['image/gif', 'image/jpeg', 'image/png']
        if mimetype in lst:
            title = content['tags']['Title']
            filename = "%s/assets/%d" %(STATIC_PRIVATE, content['id'])
            ret = '<img src="%(filename)s" alt="%(title)s" />' % locals()
            return resize + ret

        return ''


def do_test (widget, asset, collection):
    widget_name = str(widget).split('.')[-1]
    test        = widget()
    render      = test.Render().toStr()
    assert test
    print '\n#1 %s() OK' % widget_name

    try:
        test.Add(asset)
    except AttributeError: # Expected
        pass
    print '#2 %s().Add(asset) OK' % widget_name

    try:
        test.Add(collection)
    except AttributeError: # Expected
        pass
    print '#3 %s().Add(collection) OK' % widget_name

    try:
        test.Add(None)
    except (TypeError, AssertionError):
        print '#4 %s().Add(None) OK: Exception as expected' % widget_name


def test ():
    import sys

    try:
        asset_id      = sys.argv[1]
        collection_id = sys.argv[2]
        asset         = Asset.Asset(asset_id)
        collection    = Collection.Collection(collection_id)
        test_string   = 'phony'
        asset._tags['Title'] = test_string
        collection['name']   = test_string
    except IndexError:
        print 'Required test parameters: asset_id collection_id'
        sys.exit(1)

    do_test (AbstractWidget, asset, collection)
    do_test (ActionsWidget,  asset, collection)
    do_test (MetaWidget,     asset, collection)
    do_test (ViewWidget,     asset, collection)

if __name__ == '__main__':
    test()
