import os, sys

# DAM modules
sys.path.insert(0, "../../deployment")
import config
from commodity import download

cache = os.path.join (config.CACHE_DIRECTORY, "images")

# 
download ("http://farm2.static.flickr.com/1231/1457847044_3f4ba1f2c7_o.jpg", cache, verbose=True)

# Amsterdam Library of Object Images (ALOI)
download ("http://www.science.uva.nl/~mark/aloi/aloi_red2_stereo.tar", cache, verbose=True)
