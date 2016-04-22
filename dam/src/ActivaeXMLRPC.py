#!/usr/bin/env python
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

import sys
import time
import getopt
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from xmlrpclib import ServerProxy, Fault
import xmlrpclib

import config
import OpLookup
import Asset
import Role
from Error import *
from ACL import ACL

import ActivaeXMLRPCConversion

USAGE_MSG = """%s v%s
Usage: %s [params]

  --help                  Print this message
  --worker=<IP>           Launch a worker (RPC server)
  --test                  This will run some tests to see if the
                          is working

 Parameters:
  --listen=<IP>           Bind RCP server to IP
  --port=<INT>            Use a custom port for the RCP server
  --server=<IP>           Connect to a custom server
  --path=<RPC_PATH>       Path to which the rpc_server is restricted

Report bugs to %s"""


# Globals
listen = config.LISTEN
port   = config.LOOKUP_PORT
server = config.LOOKUP_SERVER
rpc_path = config.RPC_PATH

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = (rpc_path)

class WorkerOperations():
    def __init__ (self):
        self.op     = OpLookup.OpLookup()
        self.params = { 'roles':   config.LOOKUP_ROLES,
                        'user_id': config.LOOKUP_USERID}

    def search (self, search):
        """Search can be a string (for Fulltext search) or a
        dictionary (to lookup by fields.
        Can raise Empty (no search) or Invalid (wrong fields)
        exceptions."""
        results = self.op(search)
        acl = ACL (self.params)
        return acl.filter_assets ("co" , results)

    def info (self):
        return {'name':    config.PROJECT_NAME,
                'version': config.PROJECT_VERSION }

    def ping (self):
        return "pong"

    def get (self, asset_id = None, strict = True):
        """Send a dictionary with all valid DCMI tags"""
        if not asset_id:
            raise Empty

        try:
            asset_id = int(asset_id)
        except ValueError:
            raise Invalid

        asset = Asset.Asset(asset_id)
        if not asset['id']:
            raise Invalid

        acl = ACL (self.params)
        authorized = acl.filter_assets ("co" , [asset_id])
        if not authorized:
            raise Unauthorized

        tags = asset.get_tags()
        if not strict:
            return tags

        ret = []
        for tag, content in tags.items():
            if type(content) == list:
                for x in content:
                    ret.append((tag, str(x)))
            else:
                ret.append((tag, str(content)))
        return ret

    def transcode (self, asset_id, target_id):
        self.__check_transcoding_permissions (asset_id)
        self.__check_valid_target_id (asset_id, target_id)

        c = ActivaeXMLRPCConversion.Conversion()
        return c.transcode (asset_id, target_id)

    def lookup_formats (self, asset_id):
        self.__check_transcoding_permissions (asset_id)

        c = ActivaeXMLRPCConversion.Conversion()
        return c.lookup_formats (asset_id)

    def task_status (self, task_id):
        c = ActivaeXMLRPCConversion.Conversion()

        return c.task_status (task_id)

    def __check_transcoding_permissions (self, asset_id):
        if not Role.ROLE_PUBLISHER in self.params['roles']:
            raise Unauthorized, 'API not configured to convert assets'

        try:
            asset_id = int(asset_id)
        except ValueError:
            raise Invalid, 'Invalid asset'

        asset = Asset.Asset(asset_id)
        if not asset['id']:
            raise Invalid, 'Invalid asset'

        acl = ACL (self.params)
        authorized = acl.filter_assets ("ad" , [asset_id])
        if not authorized:
            raise Unauthorized, 'Permissions of asset do not allow to transcode'

    def __check_valid_target_id (self, asset_id, target_id):
        formats = self.lookup_formats (asset_id)
        valid   = [x['target_id'] for x in formats]

        if not target_id in valid:
            raise Invalid, 'Invalid target format specified'


# Tests
#
def __test_ping():
    http = "http://%s:%s/" % (server, port)

    for i in range(4):
        begin = time.time()
        print "Pinging server %s.. " % (http),

        client = ServerProxy (http)
        re = client.ping ()

        print "%.3f secs" % (time.time() - begin)
        time.sleep(1)

def __test_info():
    http = "http://%s:%s/" % (server, port)
    client = ServerProxy (http)
    re = client.info ()
    assert re != None
    print 'Info:', re

def __test_search(search):
    http = "http://%s:%s/" % (server, port)
    client = ServerProxy (http)
    re = client.search (search)
    assert type(re)==list
    print 'Search results:', re

def __test_get(asset_id):
    http = "http://%s:%s/" % (server, port)
    client = ServerProxy (http)
    re = client.get (asset_id, False)
    assert type(re) == dict
    re = client.get (asset_id)
    assert type(re) == list
    print 'Asset: %d retrieved' % asset_id

def do_tests():
    test_list = [
        ("__test_info()", None),
        ("__test_ping()", None),
        ("__test_search({})", 'Empty'),
        ("__test_search({'fake_field':'123'})", 'Invalid'),
        ("__test_search(search='admin')", None),
        ("__test_search({'creator_id':1})", None),
        ("__test_get(2**16)", 'Invalid'),
        ("__test_get(1)", 'Unauthorized'),
        ("__test_get(2)", None)
        ]

    for test in test_list:
        try:
            eval(test[0])
        except xmlrpclib.Fault,error:
            assert error.__dict__['faultString'] == "<class 'Error.%s'>:" % test[1]
            print '"%s" exception, as expected' % test[1]
        except Exception,ex:
            print test[0]
            raise ex

    print '\nREPORT: All tests went well\n'

# Real work
#
def launch_worker():
    # Create a RPC Server
    server = SimpleXMLRPCServer((listen, port),requestHandler=RequestHandler)
    server.register_introspection_functions()
    server.register_instance (WorkerOperations())
    server.server_address = server

    # Run forever
    print "%s, listening %s:%d" % (config.PROJECT_NAME, listen, port)
    while True:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print "\rExiting.."
            sys.exit(1)
        except Exception, e:
            print str(e)


def print_usage():
    print USAGE_MSG % (config.PROJECT_NAME,
                       config.PROJECT_VERSION,
                       sys.argv[0],
                       config.PROJECT_BUGTRACKER)

def main():
    global port
    global listen
    global server
    global rpc_path

    do_worker   = True
    do_test     = False

    try:
        opts, args = getopt.getopt (sys.argv[1:], '',
                                    ["worker=", "help", "listen=", "port=", "server=", "path=", "test"])

    except getopt.GetoptError, err:
        print "ERROR: %s\n" % (str(err))
        print_usage()
        sys.exit(2)

    for o, arg in opts:
        # Worker client
        if o == "--worker":
            server    = arg

        # Test operations
        elif o == "--test":
            do_test = True

        # Parameters
        elif o == "--listen":
            listen = arg
        elif o == "--server":
            server = arg
        elif o == "--port":
            port = int(arg)
        elif o == "--path":
            server = arg

        # Misc
        elif o == "--help":
            return print_usage()
        else:
            assert False, "Unhandled option: %s" %(o)

    if do_test:
        do_tests()
        sys.exit(0)

    elif do_worker:
        return launch_worker()

    print_usage()
    sys.exit(2)

if __name__ == "__main__":
    main()
