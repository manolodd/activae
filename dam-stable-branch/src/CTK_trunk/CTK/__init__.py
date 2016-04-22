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

# Generic
from Widget import Widget, RenderResponse
from Container import Container
from Box import Box
from Submitter import Submitter, SubmitterButton
from Page import Page, PageEmpty
from Config import Config
from Plugin import Plugin, instance_plugin, load_module

import JS
import util

# Widgets
from Table import Table, TableFixed
from RawHTML import RawHTML
from TextField import TextField, TextFieldPassword, TextCfg, TextCfgAuto
from Checkbox import Checkbox, CheckCfg, CheckboxText, CheckCfgText
from Combobox import Combobox, ComboCfg
from PropsTable import PropsTable, PropsTableAuto, PropsAuto
from Template import Template
from Server import Server, run, init, set_synchronous, step, publish, unpublish, cookie, post, request, cfg, error, cfg_reply_ajax_ok, cfg_apply_post
from Proxy import Proxy
from iPhoneToggle import iPhoneToggle, iPhoneCfg
from Tab import Tab
from Dialog import Dialog, DialogProxy, DialogProxyLazy, Dialog2Buttons
from HTTP import HTTP_Response, HTTP_Redir, HTTP_Error, HTTP_XSendfile
from HiddenField import HiddenField, Hidden
from Uploader import Uploader
from Plugin import PluginSelector
from Refreshable import Refreshable, RefreshableURL
from Image import Image, ImageStock
from SortableList import SortableList
from Indenter import Indenter
from Notice import Notice
from Link import Link, LinkIcon
from DatePicker import DatePicker
from Button import Button
from TextArea import TextArea
from ToggleButton import ToggleButtonImages, ToggleButtonOnOff
from Druid import Druid, DruidButtonsPanel, DruidButton, DruidButton_Goto, DruidButton_Close, DruidButton_Submit, DruidButtonsPanel_Next, DruidButtonsPanel_PrevNext, DruidButtonsPanel_PrevCreate, DruidButtonsPanel_Create, DruidButtonsPanel_Cancel, DruidButtonsPanel_Next_Auto, DruidButtonsPanel_PrevNext_Auto, DruidButtonsPanel_PrevCreate_Auto
from List import List, ListEntry

# Comodity
from cgi import escape as escape_html
