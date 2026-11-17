# Cache privata e attivazione esplicita delle librerie distribuite con Pj.
import importlib as _pj_lib_import
import importlib.abc as _pj_lib_abc
import importlib.machinery as _pj_lib_machinery
import pathlib as _pj_lib_pathlib

_pj_library_catalog = globals().get('_pj_library_catalog', {})
_pj_native_catalog = globals().get('_pj_native_catalog', {})
_pj_library_path = globals().get('_pj_library_path')
_pj_library_error = globals().get('_pj_library_error', '')
_pj_library_active = set()


def _pj_library_bootstrap(catalog, archive=None):
    # Il primo passaggio trasferisce solo il catalogo; lo ZIP serve su cache miss.
    import hashlib
    import tempfile
    import zipfile
    import os
    import json
    import sys
    import base64
    import io

    if sys.version_info < (3, 10):
        raise RuntimeError('Pj bundled libraries require Python 3.10 or newer.')
    digest = catalog['sha256']
    if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('Invalid Pj library bundle checksum.')
    cache = os.environ.get('LOCALAPPDATA') if os.name == 'nt' else os.environ.get('XDG_CACHE_HOME')
    cache = _pj_lib_pathlib.Path(cache or os.path.expanduser('~/.cache')) / 'mzPj' / 'python'
    cache.mkdir(parents=True, exist_ok=True, mode=0o700)
    root = cache / (digest + '-py' + str(sys.version_info.major) + str(sys.version_info.minor))
    marker = root / 'mzPj_manifest.json'
    if root.is_symlink():
        raise RuntimeError('Pj library cache must not be a symbolic link.')
    if marker.is_file():
        saved = json.loads(marker.read_text(encoding='utf-8'))
        if saved.get('sha256') == digest:
            return {'ready': True, 'path': str(root)}
    if archive is None:
        return {'ready': False}
    data = base64.b64decode(archive, validate=True)
    if hashlib.sha256(data).hexdigest() != digest:
        raise RuntimeError('Pj library bundle checksum verification failed.')
    allowed = {module for item in catalog['libraries']
               for module in [item['module'], *item.get('additional_modules', [])]}
    with tempfile.TemporaryDirectory(prefix='mzPj-stage-', dir=cache) as temporary:
        stage = _pj_lib_pathlib.Path(temporary) / 'libraries'
        stage.mkdir()
        with zipfile.ZipFile(io.BytesIO(data)) as zipped:
            entries = zipped.infolist()
            if len(entries) > 10000 or sum(entry.file_size for entry in entries) > 150000000:
                raise RuntimeError('Pj library bundle exceeds the supported extraction size.')
            for entry in entries:
                name = _pj_lib_pathlib.PurePosixPath(entry.filename)
                if (not name.parts or name.is_absolute() or '..' in name.parts or
                        '\\' in entry.filename or ':' in entry.filename or
                        (entry.external_attr >> 16) & 0o170000 == 0o120000 or
                        name.suffix.lower() in ('.pyd', '.so', '.dll', '.pyc') or
                        not (name.parts[0] in allowed or name.parts[0].endswith('.dist-info'))):
                    raise RuntimeError('Pj library bundle contains an unsupported entry.')
                zipped.extract(entry, stage)
        for module in allowed:
            if not (stage / module / '__init__.py').is_file():
                raise RuntimeError('Pj library bundle is missing ' + module + '.')
        (stage / 'mzPj_manifest.json').write_text(json.dumps(catalog), encoding='utf-8')
        try:
            stage.rename(root)
        except OSError:
            if not marker.is_file() or json.loads(marker.read_text(encoding='utf-8')).get('sha256') != digest:
                raise RuntimeError('Pj library cache is incomplete; remove that cache folder and try again.')
    return {'ready': True, 'path': str(root)}


class _PjLibraryFinder(_pj_lib_abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in _pj_library_active:
            return _pj_lib_machinery.PathFinder.find_spec(fullname, path if path is not None else [_pj_library_path])
        return None

    def find_distributions(self, context=None):
        # Alcune librerie leggono la propria versione tramite importlib.metadata.
        from importlib import metadata
        selected = {item['distribution'].lower().replace('-', '_')
                    for item in _pj_library_catalog.get('libraries', [])
                    if item['module'] in _pj_library_active}
        if context is not None and context.name:
            if context.name.lower().replace('-', '_') not in selected:
                return iter(())
        local = metadata.DistributionFinder.Context(path=[_pj_library_path],
                    name=context.name if context is not None else None)
        return (item for item in metadata.MetadataPathFinder.find_distributions(local)
                if item.metadata['Name'].lower().replace('-', '_') in selected)


_pj_library_finder = _PjLibraryFinder()


# Il finder nativo e' limitato ai nomi del catalogo: nessuna modifica di sys.path.
_pj_native_sources = {}


def _pj_native_supported(item):
    import sys
    import platform
    if platform.python_implementation() != item.get('implementation', 'CPython') or sys.maxsize <= 2**32:
        return False
    return sys.version_info >= (3, 10) and _pj_native_tag() in item.get('supported_platforms', [])


def _pj_native_tag():
    import sys
    import platform
    machine = platform.machine().lower()
    arch = 'arm64' if machine in ('arm64', 'aarch64') else 'x86_64' if machine in ('amd64', 'x86_64') else machine
    return ('win_amd64' if arch == 'x86_64' else 'win_' + arch) if sys.platform == 'win32' else ('macosx_' + arch if sys.platform == 'darwin' else 'linux_' + arch)


def _pj_native_available(item):
    base = globals().get('_pj_module_python_path')
    if not base or not _pj_native_supported(item):
        return False
    name = item['module']
    # PathFinder su percorso esplicito non importa il package o la sua estensione.
    package = _pj_lib_machinery.PathFinder.find_spec(name, [base])
    extension_path = _pj_lib_pathlib.Path(base) / name
    if item.get('layout') == 'platform-directory':
        extension_path /= _pj_native_tag()
    extension = _pj_lib_machinery.PathFinder.find_spec(name + '.' + name, [str(extension_path)])
    return package is not None and extension is not None


class _PjNativeFinder(_pj_lib_abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        root = fullname.split('.')[0]
        item = next((item for item in _pj_native_catalog.get('libraries', []) if item['module'] == root), None)
        if item is None or _pj_native_sources.get(root, 'bundled') == 'system':
            return None
        if not _pj_native_available(item):
            raise ImportError(root + ' has no compatible Pj native build for this platform/Python.')
        base = globals().get('_pj_module_python_path')
        return _pj_lib_machinery.PathFinder.find_spec(fullname, path if path is not None else [base])


_pj_native_finder = _PjNativeFinder()
if _pj_native_catalog.get('libraries') and globals().get('_pj_module_python_path'):
    import sys as _pj_native_sys
    _pj_native_sys.meta_path.insert(0, _pj_native_finder)


def mzpjUseLibrary(name, source='bundled'):
    # Non cambia sys.path e non sostituisce moduli gia' importati da altre fonti.
    import sys
    if source not in ('bundled', 'system'):
        raise ValueError("source must be 'bundled' or 'system'.")
    catalog = {item['module']: item for item in _pj_library_catalog.get('libraries', [])}
    aliases = {item['distribution'].lower().replace('-', '_'): key for key, item in catalog.items()}
    if not isinstance(name, str):
        raise TypeError('Library name must be a string.')
    norm_name = name.lower().replace('-', '_')

    # Supporto librerie native (Rust / PyO3 / C++)
    native_libs = {item['module']: item for item in _pj_native_catalog.get('libraries', [])}
    native_aliases = {item.get('distribution', '').lower().replace('-', '_'): key for key, item in native_libs.items()}
    if norm_name in native_libs or norm_name in native_aliases:
        mod_key = native_aliases.get(norm_name, norm_name)
        existing = sys.modules.get(mod_key)
        base = globals().get('_pj_module_python_path')
        if existing is not None:
            origin = getattr(existing, '__file__', '') or ''
            bundled = bool(base and origin and _pj_lib_pathlib.Path(origin).resolve().is_relative_to(_pj_lib_pathlib.Path(base).resolve()))
            if bundled != (source == 'bundled'):
                raise RuntimeError(mod_key + ' was already imported from another source. Choose its source before importing it, then run the script again.')
        if source == 'bundled' and not _pj_native_available(native_libs[mod_key]):
            raise RuntimeError(mod_key + ' has no compatible Pj native build for this platform/Python.')
        previous = _pj_native_sources.get(mod_key)
        _pj_native_sources[mod_key] = source
        try:
            loaded = _pj_lib_import.import_module(mod_key)
        except BaseException:
            if previous is None:
                _pj_native_sources.pop(mod_key, None)
            else:
                _pj_native_sources[mod_key] = previous
            raise
        if source == 'bundled':
            _pj_library_active.add(mod_key)
        else:
            _pj_library_active.discard(mod_key)
        return loaded

    module = aliases.get(norm_name, name.lower())
    if module not in catalog:
        raise ValueError('Unknown Pj bundled library: ' + name + '. See mzpjListLibraries().')
    selected = set()
    reused = set()

    def visit(current):
        if current not in selected:
            selected.add(current)
            selected.update(catalog[current].get('additional_modules', []))
            for dependency in catalog[current]['dependencies']:
                visit(dependency)
    visit(module)
    if source == 'bundled' and not _pj_library_path:
        raise RuntimeError(_pj_library_error or 'The Pj library cache is unavailable.')
    for current in selected:
        existing = sys.modules.get(current)
        if existing is None:
            continue
        origin = getattr(existing, '__file__', '') or ''
        bundled = bool(_pj_library_path and _pj_lib_pathlib.Path(origin).is_relative_to(_pj_library_path))
        if bundled != (source == 'bundled'):
            # Plotly accetta packaging senza vincoli: riusa quello gia' caricato
            # da matplotlib, senza sostituirlo o cambiare il suo finder.
            if (source == 'bundled' and current != module and
                    current in catalog[module].get('reuse_loaded_dependencies', [])):
                reused.add(current)
                continue
            raise RuntimeError(current + ' was already imported from another source. '
                               'Choose its source before importing it, then run the script again.')
    if source == 'bundled':
        _pj_library_active.update(selected - reused)
        if _pj_library_finder not in sys.meta_path:
            sys.meta_path.insert(0, _pj_library_finder)
    else:
        _pj_library_active.difference_update(selected)
    return _pj_lib_import.import_module(module)


def mzpjListLibraries():
    # Restituisce record pronti anche per mzpjShowTable, senza importare le librerie.
    import sys
    records = []
    # Librerie Pure Python (da mzPj_python_libraries.json)
    for item in sorted(_pj_library_catalog.get('libraries', []), key=lambda x: x['module']):
        records.append(dict(
            Library=item['module'],
            Type='Pure Python',
            Version=item['version'],
            Dependencies=', '.join(item.get('dependencies', [])) or 'None',
            Available=bool(_pj_library_path),
            Active=item['module'] in sys.modules and item['module'] in _pj_library_active
        ))
    # Librerie Native compilate (Rust / C++) da mzPj_native_libraries.json
    for item in sorted(_pj_native_catalog.get('libraries', []), key=lambda x: x['module']):
        mod_name = item['module']
        is_avail = _pj_native_available(item)
        records.append(dict(
            Library=mod_name,
            Type=item.get('backend', 'Rust (PyO3)'),
            Version=item.get('version', '0.1.0'),
            Dependencies='None (ABI3)',
            Available=is_avail,
            Active=mod_name in sys.modules
        ))
    return records
