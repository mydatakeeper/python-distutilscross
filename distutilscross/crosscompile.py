import os
import sys
from distutils.command.build import build as _build
from distutils.command.build_ext import build_ext as _build_ext
from distutils import sysconfig

BASE_PREFIX = os.path.normpath(sys.base_prefix)
BASE_EXEC_PREFIX = os.path.normpath(sys.base_exec_prefix)

class build(_build):
    def finalize_options(self):
        if 'CROSS_COMPILE' in os.environ:
            print('Setting up cross compiling environment')
            if 'CROOT' in os.environ:
                print('Setting up cross compiling prefix')
                prefix = os.environ['CROOT']
                sysconfig.get_python_lib = get_python_lib
                sysconfig.get_python_inc = get_python_inc
                sysconfig.PREFIX = prefix
                sysconfig.EXEC_PREFIX = prefix
                # reinitialize variables
                sysconfig._config_vars = None
                sysconfig.get_config_var("LDSHARED")
                _build_ext.finalize_options = finalize_options

            if 'CHOST' in os.environ:
                print('Setting up cross compiling platform')
                platform = os.environ['CHOST']
                sysconfig.PLATFORM = platform
                _build_ext.get_ext_filename = get_ext_filename

            if 'CARCH' in os.environ:
                print('Setting up cross compiling architecture')
                os.environ['_PYTHON_HOST_PLATFORM'] = 'linux-' + os.environ['CARCH']

            os.environ['CC'] = os.environ['CROSS_COMPILE'] + sysconfig.get_config_var('CC')
            os.environ['LDSHARED'] = os.environ['CROSS_COMPILE'] + sysconfig.get_config_var('LDSHARED')

        _build.finalize_options(self)


_get_python_lib = sysconfig.get_python_lib
def get_python_lib(plat_specific=0, standard_lib=0, prefix=None):
    print("Setting library prefix")
    prefix = get_python_x_prefix()
    prefix += plat_specific and BASE_EXEC_PREFIX or BASE_PREFIX

    return _get_python_lib(plat_specific, standard_lib, prefix)

_get_python_inc = sysconfig.get_python_inc
def get_python_inc(plat_specific=0, prefix=None):
    print("Setting include prefix")
    prefix = get_python_x_prefix()
    prefix += plat_specific and BASE_EXEC_PREFIX or BASE_PREFIX

    return _get_python_inc(plat_specific, prefix)

def get_python_x_prefix():
    if 'CROOT' in os.environ:
        return os.environ['CROOT']

    return ''

_finalize_options = _build_ext.finalize_options
def finalize_options(self):
    _finalize_options(self)

    print("Setting library dir prefix")
    prefix = get_python_x_prefix()
    self.library_dirs = list(map(lambda str: prefix + str, self.library_dirs)
)

_get_ext_filename = _build_ext.get_ext_filename
def get_ext_filename(self, ext_name):
    ext_filename = \
        ext_name + '.' + \
        'cpython-' + \
        str(sys.version_info.major) + \
        str(sys.version_info.minor)+ \
        sys.abiflags + '-' + \
        os.environ['CHOST'] + \
        sysconfig.get_config_var('SHLIB_SUFFIX')
    return ext_filename
