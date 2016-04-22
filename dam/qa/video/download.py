import os, sys

# DAM modules
sys.path.insert(0, "../../deployment")
import config
from commodity import download

cache = os.path.join (config.CACHE_DIRECTORY, "videos")

def get (*args, **kwargs):
    kwargs['cachedir'] = cache
    kwargs['verbose']  = True
    return download (*args, **kwargs)

# OGV (Theora)
# Video: theora, yuv420p, 528x288, PAR 1:1 DAR 11:6, 25 tbr, 25 tbn, 25 tbc
# Size: 2,447,611
get ("http://upload.wikimedia.org/wikipedia/commons/d/dc/Guillemot_theora_conversion_test.ogv")

# MP3
# Audio: mp3, 44100 Hz, 2 channels, s16, 128 kb/s
# Size:  2,771,799
get ("http://www.philringnalda.com/shannon/prs_scott_2_03.mp3")

# OGG
# Audio: vorbis, 44100 Hz, 2 channels, s16, 128 kb/s
# Size:  4,357,992
get ("http://www.vorbis.com/music/Epoq-Lepidoptera.ogg")

# XViD
# Video: mpeg4, yuv420p, 960x720 [PAR 4:3 DAR 16:9], PAR 1024:767 DAR 4096:2301, 25 tbr, 25 tbn, 25 tbc
# Audio: Audio: mp3, 48000 Hz, 2 channels, s16, 83 kb/s
# Size:  770,732,812
get ("http://fosdem.unixheads.org/2009/maintracks/ext4.xvid.avi")

# DiVX
# Video: mpeg4, yuv420p, 800x600 [PAR 1:1 DAR 4:3], 30 tbr, 30 tbn, 30k tbc
# Size:  99,223,378
get ("http://www.kotlinski.com/art/videos/CF425_2_2.DivX.avi")

# MPEG
# Video: mpeg1video, yuv420p, 320x240 [PAR 1:1 DAR 4:3], 104857 kb/s, 25 tbr, 90k tbn, 25 tbc
# Audio: mp2, 32000 Hz, 1 channels, s16, 32 kb/s
# Size:  1,017,860
get ("http://he.fi/video/data/fordka-cat.mpg")

# 3GP
# Video: flv, yuv420p, 320x240, 386 kb/s, 25 tbr, 1k tbn, 1k tbc
# Audio: Audio: mp3, 22050 Hz, 1 channels, s16
# Size:  3,601,770
get ("http://tendencias.tv/videos/3gp/fashion_eeeee.3gp")


# FOSDEM 2008: OGG (Theora)
# Video 720x576
lst = ["http://mirrors.dotsrc.org/fosdem/2008/lightningtalks/FOSDEM2008-bluepad.ogg",
       "http://mirrors.dotsrc.org/fosdem/2008/lightningtalks/FOSDEM2008-cloudbridges.ogg",
       "http://mirrors.dotsrc.org/fosdem/2008/lightningtalks/FOSDEM2008-coherence.ogg",
       "http://mirrors.dotsrc.org/fosdem/2008/lightningtalks/FOSDEM2008-dacco.ogg",
       "http://mirrors.dotsrc.org/fosdem/2008/lightningtalks/FOSDEM2008-ganeti.ogg",
       "http://mirrors.dotsrc.org/fosdem/2008/lightningtalks/FOSDEM2008-iogrind.ogg",
       "http://mirrors.dotsrc.org/fosdem/2008/lightningtalks/FOSDEM2008-k3d.ogg",
       "http://mirrors.dotsrc.org/fosdem/2008/lightningtalks/FOSDEM2008-kettle.ogg",
       "http://mirrors.dotsrc.org/fosdem/2008/lightningtalks/FOSDEM2008-mamona.ogg",]

for x in lst:
    get (x)

# FOSDEM 2009: XviD
# Video 720x576
lst = ["http://mirrors.dotsrc.org/fosdem/2009/lightningtalks/apache_felix.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2009/lightningtalks/bazaar.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2009/lightningtalks/bug.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2009/lightningtalks/camelot.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2009/lightningtalks/custom_opensolaris.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2009/lightningtalks/jtr.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2009/lightningtalks/linux_defenders.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2009/lightningtalks/lxde.xvid.avi",]

for x in lst:
    get (x)

# FOSDEM 2010: XviD
# Video 960x720
lst = ["http://mirrors.dotsrc.org/fosdem/2010/lightningtalks/saturday/02-sat-civicrm.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2010/lightningtalks/saturday/03-sat-portableapps.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2010/lightningtalks/saturday/04-sat-openpcf.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2010/lightningtalks/saturday/05-sat-savannah.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2010/lightningtalks/saturday/06-sat-nanonote.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2010/lightningtalks/saturday/07-sat-tinc.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2010/lightningtalks/saturday/10-sat-kamailio.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2010/lightningtalks/saturday/12-sat-csync.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2010/lightningtalks/saturday/15-sat-syncevolution.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2010/lightningtalks/sunday/03-sun-cloudlets.xvid.avi",
       "http://mirrors.dotsrc.org/fosdem/2010/lightningtalks/sunday/04-sun-wtdbo.xvid.avi",]

for x in lst:
    get (x)
