import os
import config
import colors

from commodity import compile_package
from utils import chdir, exe, which, exe_output

LIBOGG_URL     = "http://downloads.xiph.org/releases/ogg/libogg-1.1.4.tar.gz"
LIBVORBIS_URL  = "http://downloads.xiph.org/releases/vorbis/libvorbis-1.2.3.tar.gz"
LIBTHEORA_URL  = "http://downloads.xiph.org/releases/theora/libtheora-1.1beta2.tar.bz2"
LIBX264_URL    = "http://download.videolan.org/pub/videolan/x264/snapshots/x264-snapshot-20100606-2245.tar.bz2"
LIBXVID_URL    = "http://downloads.xvid.org/downloads/xvidcore-1.2.2.tar.bz2"
LIBMP3LAME_URL = "http://sourceforge.net/projects/lame/files/lame/3.98.2/lame-398-2.tar.gz/download"
LIBFAAD_URL    = "http://downloads.sourceforge.net/faac/faad2-2.7.tar.bz2"
LIBFAAC_URL    = "http://downloads.sourceforge.net/faac/faac-1.28.tar.bz2"
LIBSPEEX_URL   = "http://downloads.xiph.org/releases/speex/speex-1.2rc1.tar.gz"
LIBFLAC_URL    = "http://downloads.sourceforge.net/project/flac/flac-src/flac-1.2.1-src/flac-1.2.1.tar.gz"
LIBGSM_URL     = "http://ffmpeg.arrozcru.org/autobuilds/extra/sources/gsm-1.0.12.tar.gz"
LIBDC1394_URL  = "http://sourceforge.net/projects/libdc1394/files/libdc1394-2/2.1.2/libdc1394-2.1.2.tar.gz/download"
FFMPEG_URL     = "http://forja.cenatic.es/frs/download.php/1148/svn.ffmpeg.org_ffmpeg_trunk_23512.tar.gz" # "svn://svn.ffmpeg.org/ffmpeg/trunk@23512"

def check_preconditions():
    assert os.access (config.BASE_DIR, os.W_OK), "Cannot deploy to: %s" %(config.BASE_DIR)
    assert os.access (config.COMPILATION_BASE_DIR, os.W_OK), "Cannot compile in: %s" %(config.COMPILATION_BASE_DIR)
    assert which("wget"), "Wget is required"
    assert which("tar"),  "tar is required"
    assert which("svn"),  "SVN is required"

def perform():
    # Ogg, Vorbis, Theora
    compile_package (LIBOGG_URL,    "libogg-1.1.4",       skip_check="libogg.*")
    compile_package (LIBVORBIS_URL, "libvorbis-1.2.3",    skip_check="libvorbis.*")
    compile_package (LIBTHEORA_URL, "libtheora-1.1beta2", skip_check="libtheora.*")

    # x264
    conf = "--prefix=%s --enable-shared " %(config.BASE_DIR)
    if not which("yasm"):
        conf += "--disable-asm "

    compile_package (LIBX264_URL, "x264-snapshot-20100606-2245",
                     conf_params = conf,
                     skip_check  = "libx264.*")

    # Xvid
    compile_package (LIBXVID_URL, "xvidcore", 
                     pkg_type='xvidcore',
                     skip_check="libxvidcore.*")

    # MP3
    compile_package (LIBMP3LAME_URL, "lame-398-2", skip_check="libmp3lame.*")
    
    # MPEG-2 AAC decoder and encoder
    compile_package (LIBFAAD_URL, "faad2-2.7", skip_check="libfaad.*")
    compile_package (LIBFAAC_URL, "faac-1.28", skip_check="libfaac.*")

    # Speex
    compile_package (LIBSPEEX_URL, "speex-1.2rc1", skip_check="libspeex.*")

    # FLAC
    conf = "--prefix=%s --disable-rpath --disable-xmms-plugin --disable-asm-optimizations" %(config.BASE_DIR)
    compile_package (LIBFLAC_URL, "flac-1.2.1", conf_params = conf, skip_check="libFLAC.a")

    # GSM
    compile_package (LIBGSM_URL, "gsm-1.0-pl12", pkg_type='gsm', skip_check="libgsm.a")

    # DC1394
    compile_package (LIBDC1394_URL, "libdc1394-2.1.2", skip_check="libdc1394.a")

    # Ffmpeg
    conf_params = "--prefix=%s --extra-cflags=-I%s/include --extra-ldflags=-L%s/lib "%(config.BASE_DIR,config.BASE_DIR,config.BASE_DIR)
    conf_tweaks = "--enable-gpl --enable-nonfree --enable-shared "
    conf_enable = "--enable-libtheora --enable-libvorbis --enable-libx264 --enable-libxvid --enable-libmp3lame --enable-libfaad  --enable-libfaac --enable-libspeex --enable-libgsm"

    if "Darwin" in exe_output('uname'):
        conf_params += "--disable-mmx "

    compile_package (FFMPEG_URL, "ffmpeg-trunk",
                     conf_params = conf_params + conf_tweaks + conf_enable,
                     skip_check="libavcodec.a")
