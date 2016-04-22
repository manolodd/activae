import os
import config
import colors

from utils import which
from commodity import compile_package

CURL_URL = "http://curl.haxx.se/download/curl-7.19.4.tar.bz2"

def perform():
    compile_package (CURL_URL, "curl-7.19.4", skip_check="libcurl.a")

def check_preconditions():
    assert os.access (config.BASE_DIR, os.W_OK), "Cannot deploy to: %s" %(config.BASE_DIR)
    assert os.access (config.COMPILATION_BASE_DIR, os.W_OK), "Cannot compile in: %s" %(config.COMPILATION_BASE_DIR)
    assert which("wget"), "Wget is required"
    assert which("tar"),  "tar is required"
    assert which("svn"),  "SVN is required"
