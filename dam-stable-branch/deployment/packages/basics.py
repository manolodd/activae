import os
import config
import colors

from commodity import compile_package
from utils import chdir, exe, which, exe_output

LIBICONV_URL    = "http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.13.1.tar.gz"
GETTEXT_URL     = "http://ftp.gnu.org/pub/gnu/gettext/gettext-0.18.tar.gz"
LIBBZIP2_URL    = "http://www.bzip.org/1.0.5/bzip2-1.0.5.tar.gz"
EXPAT_URL       = "http://downloads.sourceforge.net/project/expat/expat/2.0.1/expat-2.0.1.tar.gz"
ZLIB_URL        = "http://downloads.sourceforge.net/project/libpng/zlib/1.2.3/zlib-1.2.3.tar.gz"
PKGCONFIG_URL   = "http://pkgconfig.freedesktop.org/releases/pkg-config-0.23.tar.gz"
GLIB_URL        = "http://ftp.gnome.org/pub/gnome/sources/glib/2.20/glib-2.20.4.tar.bz2"
RRDTOOL_URL     = "http://oss.oetiker.ch/rrdtool/pub/rrdtool-1.4.3.tar.gz"

def check_preconditions():
    assert os.access (config.BASE_DIR, os.W_OK), "Cannot deploy to: %s" %(config.BASE_DIR)
    assert os.access (config.COMPILATION_BASE_DIR, os.W_OK), "Cannot compile in: %s" %(config.COMPILATION_BASE_DIR)
    assert which("wget"), "Wget is required"
    assert which("tar"),  "tar is required"

def perform():
    #compile_package (ZLIB_URL,      "zlib-1.2.3",      skip_check="zlib.3", pkg_type='zlib')
    compile_package (LIBBZIP2_URL,  "bzip2-1.0.5",     skip_check="libbz2.a", pkg_type='bzip2')
    compile_package (LIBICONV_URL,  "libiconv-1.13.1", skip_check="libiconv.*")
    compile_package (GETTEXT_URL,   "gettext-0.18",    skip_check="libintl.*")
    compile_package (EXPAT_URL,     "expat-2.0.1",     skip_check="libexpat.a")
    #compile_package (PKGCONFIG_URL, "pkg-config-0.23", skip_check="pkg-config.1")
    compile_package (GLIB_URL,      "glib-2.20.4",     skip_check="libgobject-2.0*")
