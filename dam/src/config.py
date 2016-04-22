# -*- coding: utf-8 -*-
# Configuration parameters
#
import os
import sys

sys.path.append (os.path.abspath (os.path.realpath(__file__) + '/../../'))
from deployment.config import *

# Platform configuration
#
CTK_PORT      = 8000        # Platform port

QUEUE_PORT    = 8001        # Balancer XMLRPC queue port
QUEUE_SERVER  = "127.0.0.1" # Balancer XMLRPC queue server
QUEUE_WORKPORT= 8003        # This PORT and IP must match those
                            # configured on the src/queue/cherokee.conf
QUEUE_WORKIP  = "127.0.0.1" # WORKPORT and WORKIP are the values
                            # actually used to serve the XMLRPM queue

LOOKUP_PORT   = 8002        # XMLRPC search api port
LOOKUP_SERVER = "127.0.0.1"

# Misc: data required to report problems with Transcoding Queue
QUEUE_REPORT_EMAIL  = "activae@localhost"

# Data about user of XMLRPC searches
LOOKUP_ROLES  = [4,5] # Consumer (to lookup) and publisher (to transcode)
LOOKUP_USERID = 0 # Non-existent user

SERVER        = "127.0.0.1" # Main server. Balancer, DBSlayer, etc.
LISTEN        = "0.0.0.0"
TRANSCODERS   = 1 # Number of concurrent active transcoders
DB_HOST       = '%s:33060' % SERVER # IP address and port of the DBSlayer instance

RPC_PATH     = '/RPC2'

# Constants
#
PROJECT_NAME       = "Activae"
PROJECT_VERSION    = "0.9-6-20120807"
PROJECT_BUGTRACKER = "http://forja.cenatic.es/projects/activae"

# Paths
#
STATIC_PATH    = os.path.abspath (os.path.realpath(__file__) + '/../static')
PUBLIC_PATH    = 'public'
PRIVATE_PATH   = 'private'
ASSET_PATH     = "%s/%s/assets" % (STATIC_PATH, PRIVATE_PATH)
THUMB_PATH     = "%s/%s/thumbs" % (STATIC_PATH, PRIVATE_PATH)
UPLOAD_PATH    = '%s/%s/upload' % (STATIC_PATH, PRIVATE_PATH) # path for initial file uploads

# URL prefix
STATIC_URL     = '/files'
STATIC_PUBLIC  = '%s/%s' % (STATIC_URL,PUBLIC_PATH)  # url prefix of public static files
STATIC_PRIVATE = '%s/%s' % (STATIC_URL,PRIVATE_PATH) # url prefix of private static files

# Thumbnails
#
ICON_PATH          = "%s/images/Tango" % STATIC_PUBLIC
THUMB_SIDE         = 128
THUMB_SIZE         = "128x96"  # pixels (sqcif)
THUMB_VIDEO_OFFSET = 4         # seconds
THUMB_ASSET        = "%s/thumb_asset.png" % ICON_PATH      #default asset icon
THUMB_COLLECTION   = "%s/thumb_collection.png" % ICON_PATH #default collection icon
THUMB_EXT          = "png"
THUMB_ABS_ASSET_AUDIO  = "%s/public/images/Tango/thumb_audio.png" % STATIC_PATH
THUMB_ABS_ASSET_IMAGE  = "%s/public/images/Tango/thumb_image.png" % STATIC_PATH
THUMB_ABS_ASSET_TEXT   = "%s/public/images/Tango/thumb_text.png"  % STATIC_PATH
THUMB_ABS_ASSET_VIDEO  = "%s/public/images/Tango/thumb_video.png" % STATIC_PATH
THUMB_ABS_ASSET        = "%s/public/images/Tango/thumb_asset.png" % STATIC_PATH

# Abstracts
#
DESCRIPTION_SZ     = 200 # char-limit for description abstracts

# Embedded content
#
FLOW_WIDTH     = 640
FLOW_HEIGHT    = 480
#FLOW_PLAYER    = "%s/flowplayer/flowplayer-3.1.5.swf" % STATIC_PUBLIC
#FLOW_JS        = "%s/flowplayer/flowplayer-3.1.4.min.js" % STATIC_PUBLIC
FLOW_PLAYER    = "%s/flowplayer/flowplayer-3.2.12.swf" % STATIC_PUBLIC
FLOW_JS        = "%s/flowplayer/flowplayer-3.2.11.min.js" % STATIC_PUBLIC

# Reports
#
REPORT_ITEM_SZ  = 5   # items per category
REPORT_MAX_CHAR = 128 # title char limit for one-line reports

# Pagination
#
PAG_ITEMS = 10 # number of results

# Edition
#
EDIT_WINDOW = 300 # lock-time of an asset while being edited (in seconds)


# Limits in bytes (0 = no limit)
#
LIMIT_ASSET_FILES = 0 # number of assets that a user can add
LIMIT_ASSET_SIZE  = 0 # maximum size of the assets
LIMIT_ASSET_TOTAL = 0 # maximum total size of assets

# Upload
#
UNZIP_COLLECTIONS = 1

# Width of the View Wrapper
#
WRAPPER_WIDTH = 920
SIDEBAR_WIDTH = 210
