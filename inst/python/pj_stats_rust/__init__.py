"""Pj native statistics; select only the current process platform and architecture."""
import os as _os
import platform as _platform
import sys as _sys
_machine = _platform.machine().lower()
_arch = 'arm64' if _machine in ('arm64', 'aarch64') else 'x86_64' if _machine in ('amd64', 'x86_64') else _machine
_tag = ('win_amd64' if _arch == 'x86_64' else 'win_' + _arch) if _sys.platform == 'win32' else ('macosx_' + _arch if _sys.platform == 'darwin' else 'linux_' + _arch)
if _sys.maxsize <= 2**32 or _platform.python_implementation() != 'CPython':
    raise ImportError('Pj native statistics require a supported 64-bit CPython build.')
__path__ = [_os.path.join(_os.path.dirname(__file__), _tag)]
from .pj_stats_rust import *
from .pj_stats_rust import __version__
