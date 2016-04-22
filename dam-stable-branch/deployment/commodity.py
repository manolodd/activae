import os
import sys
import colors
import config

from utils import chdir, exe, which, find, sed_file

def download (url, cachedir=config.CACHE_DIRECTORY, headers=[], agent=None, verbose=False):
    """ Download a file, using the cache """
    # Filename
    filename = url.split('/')[-1]

    # Check cache
    exe ("mkdir -p %s" % (cachedir))
    cache_filepath = os.path.join (cachedir, filename)

    # Parameters
    params = ''

    if not verbose:
        params += "-q "

    params += ' '.join (['--header="%s"'%(x) for x in headers]) + ' '
    if agent:
        params += '-U "%s" ' % (agent)

    if not os.path.exists (cache_filepath):
        print ("%s: %s" %(colors.yellow("Cache miss"), url))
        exe ("wget %s -O '%s' '%s'" % (params, cache_filepath, url), colorer=colors.green)
    else:
        print ("%s: %s" %(colors.yellow("Cache hit"), cache_filepath))


def download_source (url, dir):
    """ Download a source package from a URL: tarball o repository"""

    # Cache directory
    cachedir = os.path.join (config.CACHE_DIRECTORY, "packages")

    # Check the cache
    if url.startswith("svn://"):
        did_checkout = False
        cache_file = "SVN-" + url[6:].replace('/','_') + '.tar.gz'
    else:
        cache_file = filter (lambda x: ((".tar.gz" in x) or (".tar.bz2" in x) or (".zip" in x)), url.split('/'))[0]

    exe ("mkdir -p %s" % (cachedir))
    cache_filepath = os.path.join (cachedir, cache_file)

    # Download if it doesn't already exist
    if not os.path.exists (cache_filepath):
        print ("%s: %s" %(colors.yellow("Cache miss"), url))

        if url.startswith("svn://"):
            exe ("svn checkout %s %s" % (url, dir))
            exe ("tar cfvz %s %s" % (cache_filepath, dir))
            did_checkout = True
        elif url.startswith("http://") or url.startswith("ftp://"):
            exe ("wget -q -O '%s' '%s'" % (cache_filepath, url), colorer=colors.green)
        else:
            assert False, "Don't know how to download %s" % (url)
    else:
        print ("%s: %s" %(colors.yellow("Cache hit"), cache_filepath))

    # Uncompress
    if url.startswith("svn://"):
        if not did_checkout:
            exe ("tar xfvz '%s'" % (cache_filepath), colorer=colors.green)
    elif ".bz2" in url:
        exe ("tar xfvj '%s'" % (cache_filepath), colorer=colors.green)
    elif (".tar.gz" in url) or (".tgz" in url):
        exe ("tar xfvz '%s'" % (cache_filepath), colorer=colors.green)
    elif ".zip" in url:
        exe ("unzip '%s'" % (cache_filepath), colorer=colors.green)
    else:
        assert False, "Don't know how to uncompress %s" % (url)

    # Patching
    patches = os.path.join (os.path.dirname (__file__), "patches")
    pkg_path = os.path.join (patches, "%s.diff" % (cache_file))
    if os.path.exists (pkg_path):
        exe ("patch -p0 < %s" % (pkg_path), colorer=colors.yellow)


def compile_package (url, dir,
                     conf_params  = "--prefix=%s" %(config.BASE_DIR),
                     make_params  = config.MAKE_PARAMS,
                     pre_rm       = True,
                     install      = True,
                     pkg_type     = "autoconf",
                     skip         = "--fast" in sys.argv,
                     skip_check   = None):

    # Check whether to skip it
    if skip and skip_check:
        tmp = find (config.BASE_DIR, skip_check)
        if tmp:
            print "%s: %s!" %(dir, colors.yellow("Skipped"))
            return

    # Clean up
    if pre_rm:
        exe ("rm -rfv %s"%(dir), colorer=colors.red)

    # Download
    download_source (url, dir)

    # Compile and install
    prev = chdir(dir)
    if pkg_type == 'autoconf':
        exe ("./configure %s" % (conf_params))
        exe ("make %s" % (make_params))

        if install:
            exe ("make install")

    elif pkg_type == 'zlib':
        exe ("./configure %s" % (conf_params))
        exe ("make %s" % (make_params))
        if install:
            exe ("make install")

        exe ("./configure -s %s" % (conf_params))
        exe ("make %s" % (make_params))
        if install:
            exe ("make install")

    elif pkg_type == 'xvidcore':
        chdir ('build/generic')
        exe ("./configure %s" % (conf_params))
        exe ("make %s" % (make_params))

        if install:
            exe ("make install")

    elif pkg_type == 'gsm':
        sed_file ('Makefile', r'-rm ', '-rm -f ')
        sed_file ('Makefile', r'-O2 ', '-O2 -fPIC ')

        exe ("make %s" % (make_params))
        exe ("gcc -shared -o lib/libgsm.so src/*.o")
        if install:
            exe ("cp -v bin/* %s/bin" % (config.BASE_DIR))
            exe ("cp -v lib/* %s/lib" % (config.BASE_DIR))
            exe ("mkdir -p %s/include/gsm" % (config.BASE_DIR))
            exe ("cp -v inc/gsm.h %s/include/gsm" % (config.BASE_DIR))

    elif pkg_type == 'bzip2':
        exe ("make %s" % (make_params))
        if install:
            exe ("make install PREFIX=%s" % (config.BASE_DIR))

        exe ("make -f Makefile-libbz2_so clean all")
        if install:
            exe ("cp -a libbz2.so* %s/lib" %(config.BASE_DIR))
            exe ("ln -s %s/lib/libbz2.so.1.0.4 %s/lib/libbz2.so" %(config.BASE_DIR, config.BASE_DIR))

    elif pkg_type == 'dcraw':
        sed_file ('install', r'prefix=/usr/local', 'prefix=%s'%(config.BASE_DIR))
        sed_file ('install', r'-march=native', '')
        sed_file ('install', r'-s', '-s -L%s/lib' %(config.BASE_DIR))
        sed_file ('install', r'-s', '-s -I%s/include' %(config.BASE_DIR))
        sed_file ('install', r'-s', '-s -lintl')
        sed_file ('install', r'-s', '')

        if install:
            exe ("sh install")

    elif pkg_type == 'gsfonts':
        exe ("mkdir -p %s/share/ghostscript/fonts" % (config.BASE_DIR))
        exe ("cp -rv * %s/share/ghostscript/fonts/" % (config.BASE_DIR))

    elif pkg_type == 'fontconfig':
        sed_file ('configure', 'use_iconv=1', 'use_iconv=0')
        exe ("PKG_CONFIG_PATH=%s/lib/pkgconfig:%s/lib64/pkgconfig:/usr/lib/pkgconfig ./configure %s" % (config.BASE_DIR, config.BASE_DIR, conf_params))
        exe ("make install")

    elif pkg_type == "wmf":
        exe ('CFLAGS="-D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64" ./configure --prefix=%s --with-png=%s' %(config.BASE_DIR, config.BASE_DIR))
        exe ('make %s' % (make_params))

        if install:
            exe ("make install")

    elif pkg_type == "xml2":
        exe ('CFLAGS="-D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64" ./configure --prefix=%s' %(config.BASE_DIR))
        exe ('make %s' % (make_params))

        if install:
            exe ("make install")

    elif pkg_type == 'jasper':
        exe ('./configure --prefix=%s --enable-shared' %(config.BASE_DIR))
        exe ('make %s' % (make_params))

        if install:
            exe ("make install")

    else:
        assert False, "Unknown package type: %s" %(pkg_type)

    # Revert chdir
    chdir (prev)

def change_name (source, pre=None, ext=None):
    """Change filenames, prepending 'pre' and changing extension to
    'ext' if necessary"""

    target = source
    if ext:
        name, _ = os.path.splitext (source)
        target  = '%s%s' % (name, ext)
    if pre:
        name    = os.path.basename (target)
        dirname = os.path.dirname (target)
        target  = os.path.join (dirname, '%s%s' % (pre,name))

    os.rename(source, target)
