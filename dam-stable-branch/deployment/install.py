#!/usr/bin/env python

import os
import sys
import config
import colors
from utils import chdir, exe_output, exe

def install (package_name):
    # Load the module
    exec ("import %s"%(package_name))
    pkg = sys.modules[package_name]

    # Check package preconditions
    pkg.check_preconditions()

    # Change the current directory
    prev_dir = chdir (config.COMPILATION_BASE_DIR)

    # Perform
    try:
        pkg.perform()
    except:
        chdir (prev_dir)
        raise

    # Done and dusted
    chdir (prev_dir)

def main():
    # Check user
    try:
        rc_uid = exe('id -u activae > /dev/null 2>&1', return_fatal=False)
        rc_gid = exe('id -g activae > /dev/null 2>&1', return_fatal=False)
        if rc_uid or rc_gid:
            raise AttributeError
    except:
        print "Create user and group 'activae' to proceed.."
        return

    # Ensure required directories exist
    rc = exe ('mkdir -p %s && chmod 755 %s'%(config.BASE_DIR,config.BASE_DIR))
    if rc:
        print "Create dir %s and give me RWX permissions.." % (config.BASE_DIR)
        return

    rc = exe ('mkdir -p %s && chmod 777 %s'%(config.CACHE_DIRECTORY,config.CACHE_DIRECTORY))
    if rc:
        print "Create dir %s and give me RWX permissions.." % (config.CACHE_DIRECTORY)
        return

    rc = exe ('mkdir -p %s && touch %s %s && chown activae:activae %s -R  && chmod 777 %s/* '%(config.LOG_DIR, config.LOG_QUEUE, config.LOG_ACTIVAE, config.LOG_DIR, config.LOG_DIR))
    if rc:
        print "Create dir %s and give me RWX permissions.." % (config.LOG_DIR)
        return

    # Copy Activae to deployment directory
    DIR = os.path.abspath (os.path.realpath(__file__) + '/../../')
    rc = exe('cp -R %s/* %s && chown activae:activae %s -R'%(DIR, config.BASE_DIR, config.BASE_DIR))

    if rc:
        print "Copy Activae files to target directory %s"%(config.BASE_DIR)
        return

    # Environment variables
    os.putenv ("PKG_CONFIG_PATH", "%s/lib/pkgconfig"%(config.BASE_DIR))

    ld = "%s/lib" % (config.BASE_DIR)
    ld_prev = os.getenv("LD_LIBRARY_PATH")

    if ld_prev and (not ld in ld_prev):
        os.putenv ("LD_LIBRARY_PATH", "%s/lib:%s"%(config.BASE_DIR, ld_prev))
    else:
        os.putenv ("LD_LIBRARY_PATH", "%s/lib"%(config.BASE_DIR))

    path = "%s/bin:%s/sbin" % (config.BASE_DIR, config.BASE_DIR)
    path_prev = os.getenv("PATH")

    if path_prev and (not path in path_prev):
        os.putenv ("PATH", "%s/bin:%s/sbin:%s"%(config.BASE_DIR, config.BASE_DIR, path_prev))
    else:
        os.putenv ("PATH", "%s/bin:%s/sbin"%(config.BASE_DIR, config.BASE_DIR))

    # Install packages
    sys.path.insert (0, os.path.join (os.getcwd(), "packages"))

    for arg in filter(lambda x: not x.startswith('-'), sys.argv[1:]):
        install (arg)

    del (sys.path[0])
    print colors.yellow("Installation complete!")

if __name__ == "__main__":
    src_dir = os.path.abspath (os.path.realpath(__file__) + '/../../').rstrip('/')
    dst_dir = config.BASE_DIR.rstrip('/')

    if src_dir == dst_dir:
        print 'Source and target directories are the same.'
        print 'It looks like you are trying to reinstall Activae using an installer located in the target directory.'
        print 'You must try from another location. Aborting deployment!'
        sys.exit(-1)

    if os.getuid() == 0:
        main()
    else:
        print 'Must be root to run the installer'
        sys.exit(-2)
