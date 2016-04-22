import sys
import time
from xmlrpclib import ServerProxy
from pprint import pprint

client = ServerProxy ("http://217.116.6.26:8002/")
client = ServerProxy ("http://127.0.0.1:8002/")

# INFO
print 'Method info()'
re = client.info ()
assert re != None
print '\tInfo:', re

# PING
print '\nMethod ping()'
for i in range(4):
    begin = time.time()
    print "\tPinging server.. " ,

    re = client.ping ()

    print "%.3f secs" % (time.time() - begin)
    time.sleep(1)

# SEARCH
print '\nMethod search()'
search = {'creator_id':1} # search by dictionary
re = client.search (search)
assert type(re)==list
print '\tSearch results:', re

# GET
print '\nMethod get()'
if not len(re):
    print '\tCould not test method. No previous results'
    sys.exit()

asset_id = re[0]
re = client.get (asset_id, False)
assert type(re) == dict
print '\tAsset: %d retrieved\n' % asset_id
pprint(re)
re = client.get (asset_id)
assert type(re) == list
print '\tAsset: %d retrieved (strict)\n' % asset_id
pprint(re)
