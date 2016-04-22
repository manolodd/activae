import os
import config
import colors

from commodity import compile_package
from utils import chdir, exe, which, find

CHEROKEE_URL     = "http://www.cherokee-project.com/download/0.99/0.99.44/cherokee-0.99.44.tar.gz"
DIR              = "cherokee-trunk"
CONFIGURE_PARAMS = "--prefix=%s --enable-static-module=all --enable-static --enable-shared=no --with-ldap=no" % (config.BASE_DIR)
MAKE_PARAMS      = "-j4"
GRAPH_DIRECTORY  = '%s/var/lib/cherokee/graphs/'%(config.BASE_DIR)

def check_preconditions():
    assert os.access (config.BASE_DIR, os.W_OK), "Cannot deploy to: %s" %(config.BASE_DIR)
    assert os.access (config.COMPILATION_BASE_DIR, os.W_OK), "Cannot compile in: %s" %(config.COMPILATION_BASE_DIR)
    assert which("make"), "GNU Make is required"

def perform():
    # Install
    compile_package (CHEROKEE_URL, "cherokee-0.99.44", skip_check="cherokee-worker")

    exe('mkdir -p %s && chown activae:activae %s'%(GRAPH_DIRECTORY,
                                                   GRAPH_DIRECTORY))
