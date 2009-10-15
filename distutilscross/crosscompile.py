import os
from distutils.command.build import build as _build
from distutils import sysconfig


class build(_build):
    user_options = _build.user_options + [ ('cross-compile', 'x', 'set things up for a cross compile')]

    boolean_options = _build.boolean_options + ['cross-compile']

    def initialize_options(self):
        _build.initialize_options(self)
        self.cross_compile = 0

    def finalize_options(self):
        if self.cross_compile and os.environ.has_key('PYTHONXCPREFIX'):
            prefix = os.environ['PYTHONXCPREFIX']
            sysconfig.get_python_lib = get_python_lib
            sysconfig.PREFIX = prefix
            sysconfig.EXEC_PREFIX = prefix
            # reinitialize variables
            sysconfig._config_vars = None
            sysconfig.get_config_var("LDSHARED")

        _build.finalize_options(self)


_get_python_lib = sysconfig.get_python_lib
def get_python_lib(plat_specific=0, standard_lib=0, prefix=None):
    if os.environ.has_key('PYTHONXCPREFIX'):
        print "Setting prefix"
        prefix = os.environ['PYTHONXCPREFIX']

    return _get_python_lib(plat_specific, standard_lib, prefix)

