#!/usr/bin/env python
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
import threading
import Queue

from Worker import WorkerOperations
from SimpleXMLRPCServer import SimpleXMLRPCServer
from xmlrpclib import ServerProxy

sys.path.append ("..")
import config
import status

USAGE_MSG = """%s v%s
Usage: %s [params]

  --help                  Print this message

 Server:
  --worker=<IP>           Launch a worker (RPC server)

 Client:
  --ping                  Ping the server
  --image-conv=<params>   Convert an image file
  --image-info=<path>     Get information about an image file
  --image-thumb=<params>  Generate a thumbnail of the image
  --video-conv=<params>   Convert a media (audio and/or video) file
  --video-thumb=<params>  Generate a thumbnail of the video
  --video-info=<path>     Get information about a video file

 Parameters:
  --listen=<IP>           Bind to RCP server to IP
  --port=<INT>            Use a custom port for the RCP server
  --server=<IP>           Connect the a custom server

Report bugs to %s"""


# Globals
listen = config.LISTEN
port   = config.QUEUE_WORKPORT
server = config.QUEUE_WORKIP
jobs   = Queue.Queue(0)

def do_ping_server():
    http = "http://%s:%s/" % (server, port)

    for i in range(4):
        begin = time.time()
        print "Pinging server %s.. " % (http),

        try:
            client = ServerProxy (http)
            re = client.ping ('ping')
        except:
            print "could not connect"
            time.sleep(1)
            continue

        assert re == 'pong', "Did not receive pong"
        print "%.3f secs" % (time.time() - begin)
        time.sleep(1)

def do_convert_media (*args):
    http = "http://%s:%s/" % (server, port)

    client = ServerProxy (http)
    re = client.ConvertMedia (*args)

    if re == "ok":
        print "Media file successfuly converted."
        return 0

    print "Could not convert the media file."
    return 1

def do_convert_image (*args):
    http = "http://%s:%s/" % (server, port)

    client = ServerProxy (http)
    re = client.ConvertImage (*args)

    if re == "ok":
        print "Image file successfuly converted."
        return 0

    print "Could not convert the image file."
    return 1

def do_thumb_video (*args):
    http = "http://%s:%s/" % (server, port)

    client = ServerProxy (http)
    re = client.BuildThumbnailMedia (*args)

    if re == "ok":
        print "Thumbnail successfuly generated."
        return 0

    print "Could not generate thumbnail."
    return 1

def do_info_video (*args):
    http = "http://%s:%s/" % (server, port)

    client = ServerProxy (http)
    re, info = client.GetInfoMedia (*args)

    if re == "ok":
        print "Got information about the video:", info
        return 0

    print "Could not get information about the video."
    return 1

def do_info_image (*args):
    http = "http://%s:%s/" % (server, port)

    client = ServerProxy (http)
    re, info = client.GetInfoImage (*args)

    if re == "ok":
        print "Got information about the image:", info
        return 0

    print "Could not get information about the image."
    return 1

def do_thumb_image (*args):
    http = "http://%s:%s/" % (server, port)

    client = ServerProxy (http)
    re = client.BuildThumbnailImage (*args)

    if re == "ok":
        print "Thumbnail successfuly generated."
        return 0

    print "Could not generate thumbnail."
    return 1

class Superviser (threading.Thread):
    """Job queue supervising-thread"""

    def run (self):
        global jobs
        while True:

            try:
                job, args, callback, task_id = jobs.get()
                rc = job (*args)
                if rc==None:
                    rc = -1
                status.status[task_id] = rc
            except:
                print "Exception raised during task execution. This shouldn't happen."

            if callback:
                try:
                    callback()
                except:
                    print "Exception raised during callback execution. This shouldn't happen."


def launch_worker():
    # Instantiate queue and launch threads to supervise the task queue
    global jobs
    for x in range(config.TRANSCODERS):
        Superviser().start()

    # Create a RPC Server
    server = SimpleXMLRPCServer((listen, port))
    server.register_introspection_functions()
    server.register_instance (WorkerOperations(jobs))
    server.server_address = server

    # Run forever
    print "%s, listening %s:%d" % (config.PROJECT_NAME, listen, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print "\rExiting (%d remaining elements in queue).." % jobs.qsize()
        sys.exit(0)

def print_usage():
    print USAGE_MSG % (config.PROJECT_NAME,
                       config.PROJECT_VERSION,
                       sys.argv[0],
                       config.PROJECT_BUGTRACKER)

def main():
    global port
    global listen
    global server

    do_worker   = False
    do_ping     = False
    do_i_conv   = False
    do_i_info   = False
    do_i_thumb  = False
    do_v_conv   = False
    do_v_info   = False
    do_v_thumb  = False

    try:
        opts, args = getopt.getopt (sys.argv[1:], '',
                                    ["worker=", "help", "listen=", "port=", "server=", "ping",
                                     "video-conv=", "video-info=", "video-thumb=",
                                     "image-conv=", "image-info=", "image-thumb="])
    except getopt.GetoptError, err:
        print "ERROR: %s\n" % (str(err))
        print_usage()
        sys.exit(2)

    for o, arg in opts:
        # Worker client
        if o == "--worker":
            do_worker = True
            server    = arg

        # Client operations
        elif o == "--ping":
            do_ping = True

        # Image operations
        elif o == "--image-conv":
            do_i_conv = arg
        elif o == "--image-info":
            do_i_info = arg
        elif o == "--image-thumb":
            do_i_thumb = arg

        # Video operations
        elif o == "--video-conv":
            do_v_conv = arg
        elif o == "--video-info":
            do_v_info = arg
        elif o == "--video-thumb":
            do_v_thumb = arg

        # Parameters
        elif o == "--listen":
            listen = arg
        elif o == "--server":
            server = arg
        elif o == "--port":
            port = int(arg)

        # Misc
        elif o == "--help":
            return print_usage()
        else:
            assert False, "Unhandled option: %s" %(o)

    if do_worker:
        return launch_worker()
    elif do_ping:
        return do_ping_server()

    # Image
    elif do_i_conv:
        image_args = do_i_conv.split(',')
        return do_convert_image (*image_args)
    elif do_i_info:
        return do_info_image (do_i_info)
    elif do_i_thumb:
        thumb_args = do_i_thumb.split(',')
        return do_thumb_image (*thumb_args)

    # Video
    elif do_v_conv:
        conv_args = do_v_conv.split(',')
        return do_convert_media (*conv_args)
    elif do_v_info:
        return do_info_video (do_v_info)
    elif do_v_thumb:
        thumb_args = do_v_thumb.split(',')
        return do_thumb_video (*thumb_args)

    print_usage()
    sys.exit(2)

if __name__ == "__main__":
    main()
