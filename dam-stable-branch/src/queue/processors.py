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
# You may contact the copyright holder at: Fundacion CENATIC, Edificio
# de Servicios Sociales: C/ Vistahermosa, 1, 3ra planta, 06200
# Almendralejo (Badajoz), Spain

import time
import os
import shutil
import tempfile
import zipfile
import sys
import smtplib
from email.mime.text import MIMEText

sys.path.append("..")
from config import *
from VFS import *
import Upload
import File
import status
import OpLookup
import Auth
import Asset
import OpAsset

RETRIES = 3
INSERTION_LAG = 3

ERROR_MSG = """
Se produjo un error en la cola de transcodificación procesando el
activo %(id)s: "%(title)s". El activo destino no ha sido eliminado y
requiere supervisión manual. La información referente al problema con
el archivo "%(filename)s" ha sido registrada en el fichero de logs.
"""

ERROR_SUBJECT = """
Activae: Problema con transcodificación
"""

class FileHandler:
    """Process file, unzip if required, make unique names and move
    to ASSET_PATH"""
    def __init__ (self):
        None

    def do_process (self, filename, original_name, name_conversions):
        """Process file and move it to ASSET_PATH. Unzip if
        necessary. Return the list of processed files"""
        tmp_dir  = tempfile.mkdtemp(dir=UPLOAD_PATH)
        src_name  = os.path.join(UPLOAD_PATH,filename)
        fullname  = os.path.join(tmp_dir, original_name)
        os.rename(src_name, fullname)

        if UNZIP_COLLECTIONS and self.extract (fullname):
            os.unlink (fullname)

        dir_name      = os.path.dirname(fullname)
        new_files     = []
        for subdir, dirs, files in os.walk(dir_name):
            for src_name in files:
                src = os.path.join(subdir,src_name)
                if src_name in name_conversions:
                    dst_name = name_conversions[src_name]
                else:
                    continue
                new_name = os.path.join(ASSET_PATH, dst_name)

                os.rename(src, new_name)
                Upload.get_thumbnail(new_name)
                new_files.append (new_name)

        shutil.rmtree(tmp_dir)
        return new_files

    def extract (self, fullname):
        try:
            zf = zipfile.ZipFile(fullname)
        except zipfile.BadZipfile:
            return False

        dir_name = os.path.dirname(fullname)
        tmp_dir = tempfile.mkdtemp(dir=dir_name)
        zf.extractall (tmp_dir)
        return True


class FileCallback:
    """This callback is executed after a file has been processed by
    the queue"""
    def __init__ (self, task_id):
        self.task_id = task_id

    def __call__ (self):
        for i in range(RETRIES):
            files = File.get_files_by_flag (self.task_id)
            if files:
                break
            else:
                time.sleep (10)
        files = self._cleanup (files)

        if not status.status[self.task_id] == True:
            self._execution_failure (files)

        try:
            for x in range(len(files)):
                filename = os.path.join (ASSET_PATH, files[x]['filename'])
                try:
                    f = Upload.get_info (filename)
                except:
                    continue
                for key,value in f.items():
                    if key == 'filename':
                        value = os.path.basename(value)
                    files[x][key] = value
                files[x]['queue_flag'] = None

            File.update_files (files)
        except:
            # The queue would freeze with an exception
            pass

        File.unset_flag (self.task_id)

    def _cleanup (self, files):
        for x in range(len(files)):
            for key,value in files[x].items():
                if value == None:
                    files[x].pop(key)
        return files

    def _execution_failure (self, files):
        """Send report to the user that enqueued the task"""
        try:
            asset_ids = self._get_asset_ids (files)
            for asset_id in asset_ids:
                asset = Asset.Asset (asset_id)
                if not asset:
                    continue

                to  = self._get_owner_email (asset)
                txt = self._get_message (asset)
                #self._delete_broken_asset (asset)
                self._send_email (to, txt)
        except:
            pass

    def _get_asset_ids (self, files):
        asset_ids = []
        o = OpLookup.OpLookup()
        for f in files:
            try:
                result = o({'filename':f['filename']})
                asset_ids.extend(result)
            except:
                pass
        return asset_ids

    def _get_owner_email (self, asset):
        user_id = asset['publisher_id']
        if not user_id:
            return

        user_name = Auth.get_user_name (user_id)
        user      = Auth.get_user (user_name)

        return user['email']

    def _send_email (self, to, txt):
        msg = MIMEText(txt)
        msg['Subject'] = ERROR_SUBJECT
        msg['From']    = QUEUE_REPORT_EMAIL
        msg['To']      = to

        s = smtplib.SMTP()
        s.connect()
        s.sendmail(QUEUE_REPORT_EMAIL, [to], msg.as_string())
        s.close()

    def _get_message (self, asset):
        data = {'id':    asset['id'],
                'title': asset['title'],
                'filename': asset._file['filename']}
        return ERROR_MSG % data

    def _delete_broken_asset (self, asset):
        oa = OpAsset.OpAsset (asset)
        oa.delete ()

class UpdateHandler:
    """This callback is executed after a file has been processed by
    the queue"""
    def __init__ (self, task_id):
        self.task_id = task_id

    def __call__ (self):
        for i in range(RETRIES):
            files = File.get_files_by_flag (self.task_id)
            if files:
                break
            else:
                time.sleep (1)

        files = self._cleanup (files)

        for x in range(len(files)):
            filename = os.path.join (ASSET_PATH, files[x]['filename'])
            try:
                f = Upload.get_info (filename)
            except:
                continue
            for key,value in f.items():
                if key == 'filename':
                    value = os.path.basename(value)
                files[x][key] = value

        File.update_files (files)

    def _cleanup (self, files):
        for x in range(len(files)):
            for key,value in files[x].items():
                if value == None:
                    files[x].pop(key)
        return files
