# Cache privata e attivazione esplicita delle librerie distribuite con Pj.
import importlib as _pj_lib_import
import importlib.abc as _pj_lib_abc
import importlib.machinery as _pj_lib_machinery
import pathlib as _pj_lib_pathlib

_pj_library_catalog = globals().get('_pj_library_catalog', {})
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
    allowed = {item['module'] for item in catalog['libraries']}
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


def mzpjUseLibrary(name, source='bundled'):
    # Non cambia sys.path e non sostituisce moduli gia' importati da altre fonti.
    import sys
    if source not in ('bundled', 'system'):
        raise ValueError("source must be 'bundled' or 'system'.")
    catalog = {item['module']: item for item in _pj_library_catalog.get('libraries', [])}
    aliases = {item['distribution'].lower().replace('-', '_'): key for key, item in catalog.items()}
    if not isinstance(name, str):
        raise TypeError('Library name must be a string.')
    module = aliases.get(name.lower().replace('-', '_'), name.lower())
    if module not in catalog:
        raise ValueError('Unknown Pj bundled library: ' + name + '. See mzpjListLibraries().')
    selected = set()

    def visit(current):
        if current not in selected:
            selected.add(current)
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
            raise RuntimeError(current + ' was already imported from another source. '
                               'Choose its source before importing it, then run the script again.')
    if source == 'bundled':
        _pj_library_active.update(selected)
        if _pj_library_finder not in sys.meta_path:
            sys.meta_path.insert(0, _pj_library_finder)
    else:
        _pj_library_active.difference_update(selected)
    return _pj_lib_import.import_module(module)


def mzpjListLibraries():
    # Restituisce record pronti anche per mzpjShowTable, senza importare le librerie.
    import sys
    return [dict(Library=item['module'], Version=item['version'],
                 Dependencies=', '.join(item['dependencies']) or 'None',
                 Available=bool(_pj_library_path),
                 Active=item['module'] in sys.modules and item['module'] in _pj_library_active)
            for item in sorted(_pj_library_catalog.get('libraries', []), key=lambda item: item['module'])]
