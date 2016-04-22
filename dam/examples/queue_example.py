import sys
from xmlrpclib import ServerProxy

client = ServerProxy ("http://217.116.6.26:8001/")

# Note 1: Filenames must be specified with absolute paths
# Note 2: An exception is raised if source files don't exist
# Note 3: For this example, you need /tmp/test.mpg and /tmp/test.png

# Video
source = '/tmp/test.mpg'
target = '/tmp/target.mp4'
format = 'mp4'
vts_id = client.ConvertMedia (source, target, format)
print 'Video Conversion: %s -> %s (%s) [Task_ID: %s]' %(source, target, format,vts_id)

source = '/tmp/test.mpg'
target = '/tmp/target.mpg.png'
ret    = client.BuildThumbnailMedia (source, target)
# Possible returns: "failed" | "ok"
print 'Video Thumbnail: %s -> %s [%s]' %(source, target, ret)

source = '/tmp/test.mpg'
ret    = client.GetInfoMedia (source)
# Possible returns: "failed" |  ("ok", dict_info)
print 'Video Info: %s [%s]' %(source, ret)


# Image
source = '/tmp/test.png'
target = '/tmp/target.jpg'
its_id = client.ConvertImage (source, target, 'jpg')
print 'Image Conversion: %s -> %s (%s) [Task_ID: %s]' %(source, target, format,its_id)

source = '/tmp/test.png'
target = '/tmp/target.png.png'
ret    = client.BuildThumbnailImage (source, target)
# Possible returns: "failed" | "ok"
print 'Image Thumbnail: %s -> %s [%s]' %(source, target, ret)

source = '/tmp/test.png'
ret    = client.GetInfoImage (source)
# Possible returns: "failed" |  ("ok", dict_info)
print 'Image Info: %s [%s]' %(source, ret)


# Tasks
try:
    ret = client.GetTaskStatus (its_id)
except Exception,e:
    ret = str(e)
print 'Image Conversion Task Status: %s [Task_ID: %s]' %(ret,its_id)

try:
    ret = client.GetTaskStatus (vts_id)
except Exception,e:
    ret = str(e)
print 'Video Conversion Task Status: %s [Task_ID: %s]' %(ret,vts_id)

try:
    ret = client.GetTaskStatus (00000000)
except Exception,e:
    ret = str(e)
print 'Non-existent Task Status: %s [Task_ID: %s]' %(ret,00000000)
