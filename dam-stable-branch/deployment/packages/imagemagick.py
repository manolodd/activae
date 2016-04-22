import os
import config
import colors

from commodity import compile_package
from utils import chdir, exe, which, exe_output

GHOSTSCRIPT_URL    = "http://downloads.sourceforge.net/ghostscript/ghostscript-8.64.tar.bz2"
GHOSTSCRIPT_PARMS  = "--prefix=%s --with-libiconv=no --disable-cups" % (config.BASE_DIR)
LIBXML2_URL        = "http://xmlsoft.org/sources/libxml2-2.7.7.tar.gz"
LIBWMF_URL         = "http://downloads.sourceforge.net/project/wvware/libwmf/0.2.8.3/libwmf-0.2.8.3.tar.gz"

IMAGEMAGICK_URL    = "http://ftp.nluug.nl/ImageMagick/ImageMagick-6.5.5-2.tar.bz2"
IMAGEMAGICK_PARAMS = "--prefix=%s --with-perl=no" % (config.BASE_DIR)

GS_FONTS_URL    = "http://ghostscript.googlecode.com/files/ghostscript-fonts-std-8.11.tar.gz"
FREETYPE_URL    = "http://downloads.sourceforge.net/project/freetype/freetype2/2.3.9/freetype-2.3.9.tar.bz2"
LIBTIFF_URL     = "http://dl.maptools.org/dl/libtiff/tiff-3.8.2.tar.gz"
LIBJPEG_URL     = "http://www.ijg.org/files/jpegsrc.v7.tar.gz"
LIBPNG_URL      = "http://prdownloads.sourceforge.net/libpng/libpng-1.2.39.tar.gz"
JASPER_URL      = "http://www.ece.uvic.ca/~mdadams/jasper/software/jasper-1.900.1.zip"
LCMS_URL        = "http://downloads.sourceforge.net/project/lcms/lcms/1.18/lcms-1.18a.tar.gz"
DCRAW_URL       = "http://www.cybercom.net/~dcoffin/dcraw/archive/dcraw-8.96.tar.gz"
PIXMAN_URL      = "http://pkgs.fedoraproject.org/repo/pkgs/pixman/pixman-0.15.20.tar.gz/613c95e7ddc8069b7aa2708f93219b7d/pixman-0.15.20.tar.gz"
FONTCONFIG_URL  = "http://www.fontconfig.org/release/fontconfig-2.8.0.tar.gz"
CAIRO_URL       = "http://cairographics.org/releases/cairo-1.8.8.tar.gz"
PANGO_URL       = "http://ftp.gnome.org/pub/gnome/sources/pango/1.24/pango-1.24.5.tar.bz2"

def check_preconditions():
    assert os.access (config.BASE_DIR, os.W_OK), "Cannot deploy to: %s" %(config.BASE_DIR)
    assert os.access (config.COMPILATION_BASE_DIR, os.W_OK), "Cannot compile in: %s" %(config.COMPILATION_BASE_DIR)
    assert which("wget"), "Wget is required"
    assert which("tar"),  "tar is required"

def perform():
    compile_package (FREETYPE_URL,    "freetype-2.3.9",      skip_check="libfreetype.a")
    compile_package (GS_FONTS_URL,    "fonts",               skip_check="n021003l.pfb",   pkg_type="gsfonts")
    compile_package (GHOSTSCRIPT_URL, "ghostscript-8.64",    skip_check="gslp.1",         conf_params=GHOSTSCRIPT_PARMS, make_params='')
    compile_package (LIBTIFF_URL,     "tiff-3.8.2",          skip_check="libtiff.a")
    #compile_package (LIBJPEG_URL,     "jpeg-7",              skip_check="libjpeg.a")
    compile_package (LIBPNG_URL,      "libpng-1.2.39",       skip_check="libpng.a" )
    #compile_package (LIBXML2_URL,     "libxml2-2.7.7",       skip_check="libxml2.so",       pkg_type='xml2')
    compile_package (LIBWMF_URL,      "libwmf-0.2.8.3",      skip_check="libwmflite-0*",    pkg_type='wmf')
    compile_package (JASPER_URL,      "jasper-1.900.1",      skip_check="libjasper.*",      pkg_type='jasper')
    compile_package (LCMS_URL,        "lcms-1.18",           skip_check="liblcms.a")
    compile_package (DCRAW_URL,       "dcraw",               skip_check="dcraw.1",          pkg_type='dcraw')
    compile_package (PIXMAN_URL,      "pixman-0.15.20",      skip_check="libpixman-1.*")
    compile_package (FONTCONFIG_URL,  "fontconfig-2.8.0",    skip_check="fontconfig.pc",    pkg_type='fontconfig')
    compile_package (CAIRO_URL,       "cairo-1.8.8",         skip_check="libcairo.a")
    compile_package (PANGO_URL,       "pango-1.24.5",        skip_check="libpango-1.*")
    compile_package (IMAGEMAGICK_URL, "ImageMagick-6.5.5-2", skip_check="ImageMagick.h",  conf_params=IMAGEMAGICK_PARAMS)
