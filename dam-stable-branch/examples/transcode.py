import sys
from xmlrpclib import ServerProxy

#client = ServerProxy ("http://217.116.6.26:8002/")
client = ServerProxy ("http://127.0.0.1:8002/")

try:
    target_id = int(sys.argv[2])
except:
    target_id = None

try:
    asset_id = int(sys.argv[1])
except:
    print 'Required parameters: asset_id target_id'
    sys.exit(1)

try:
    if not target_id:
        # Valid targets
        print 'lookup_formats()', client.lookup_formats (asset_id)
    else:
        # Enque task
        print 'transcode()', client.transcode (asset_id, target_id)
except Exception,e:
    print str(e)

