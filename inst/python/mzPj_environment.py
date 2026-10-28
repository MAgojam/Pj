# Informazioni e librerie opzionali dell’interprete.

def _pj_mac_library_path(executable, version, platform, mode):
    # Il launcher MacOS/python non aggiunge sempre Resources/lib agli import.
    # Si considera solo l'app dell'eseguibile embedded, mai il Python System.
    from pathlib import Path
    if platform != 'darwin' or mode not in ('bundled', 'embedded', 'jamovi'):
        return None
    binary = Path(executable).resolve()
    contents = binary.parent.parent
    if binary.parent.name != 'MacOS' or contents.name != 'Contents' or contents.parent.suffix != '.app':
        return None
    library = contents/'Resources'/'lib'/('python' + '.'.join(map(str, version[:2])))
    return str(library) if library.is_dir() else None

import sys as _pj_environment_sys
_pj_embedded_lib = _pj_mac_library_path(_pj_environment_sys.executable,
    _pj_environment_sys.version_info, _pj_environment_sys.platform, globals().get('PYTHON_MODE'))
if _pj_embedded_lib and _pj_embedded_lib not in _pj_environment_sys.path:
    _pj_environment_sys.path.insert(0, _pj_embedded_lib)

# numpy/scipy protetti da try/except: con Python di sistema (opzione
# 'External') potrebbero mancare o fallire per un problema di caricamento
# DLL (vedi caso matplotlib) - senza questa protezione, un fallimento qui,
# PRIMA di main(), interrompe lo script senza produrre ne' 'ERROR:' ne' 'OK',
# quindi jamovi non mostra nulla (ne' output ne' errore). Con la protezione,
# lo script prosegue comunque; il report esclude le librerie non caricate.
_available_libs = []

try:
    import numpy as np
    _available_libs.append('numpy')
except Exception as e:
    np = None

try:
    from scipy import stats
    _available_libs.append('scipy')
except Exception as e:
    stats = None

# matplotlib protetto allo stesso modo - disponibile solo con Python di
# sistema per ora (l'embedded non lo ha). Il backend 'Agg' va impostato
# PRIMA di importare pyplot: e' non-interattivo, l'unico adatto qui visto
# che gira in un sottoprocesso senza display.
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    _available_libs.append('matplotlib')
except Exception as e:
    matplotlib = None
    plt = None

def _pj_python_info():
    """Raccoglie i moduli senza importarli; eventuali errori restano nel report."""
    import platform
    import pkgutil
    import importlib.util as _ilu
    from html import escape

    notes = []
    versions = {}
    distributions = {}
    try:
        from importlib import metadata
        distributions = metadata.packages_distributions()
        for distribution in metadata.distributions():
            try:
                name = distribution.metadata.get('Name')
                if name:
                    versions[name.lower().replace('_', '-')] = distribution.version
            except Exception:
                continue
    except Exception:
        notes.append('Some package version information is unavailable.')

    candidates = set(sys.builtin_module_names)
    candidates.update(getattr(sys, 'stdlib_module_names', ()))
    # Una directory non leggibile non deve impedire il resto della raccolta.
    for path in dict.fromkeys(sys.path):
        try:
            candidates.update(module.name for module in pkgutil.iter_modules([path]))
        except Exception:
            notes.append('Some module locations could not be inspected.')

    libraries = []
    for name in sorted(candidates, key=lambda value: (value.casefold(), value)):
        if name.startswith('_'):
            continue
        # Le librerie gia' precaricate hanno una verifica di importazione reale.
        if name in ('numpy', 'scipy', 'matplotlib') and name not in _available_libs:
            continue
        try:
            if _ilu.find_spec(name) is None:
                continue
        except Exception:
            continue
        version = next((
            versions.get(package.lower().replace('_', '-'))
            for package in distributions.get(name, ())
            if versions.get(package.lower().replace('_', '-'))
        ), '')
        libraries.append(
            '<li><span>' + escape(name) + '</span>' +
            (' <small>' + escape(str(version)) + '</small>' if version else '') +
            '</li>'
        )

    interpreter = 'System Python' if PYTHON_MODE == 'external' else 'jamovi Python'
    fields = (
        ('Version', platform.python_version() + ' · ' + platform.python_implementation()),
        ('Executable', sys.executable or 'Unavailable'),
        ('Platform', platform.platform()),
        ('Architecture', str(struct.calcsize('P') * 8) + '-bit'),
        ('Environment', sys.prefix),
    )
    rows = ''.join(
        '<div class="pj-pyinfo-row"><dt>' + escape(label) + '</dt><dd>' +
        escape(str(value)) + '</dd></div>' for label, value in fields
    )
    diagnostics = ''.join('<p class="pj-pyinfo-note">' + escape(note) + '</p>'
                          for note in dict.fromkeys(notes))
    bundled = globals().get('mzpjListLibraries', lambda: [])()
    bundle_html = ('<details><summary>Pj bundled libraries (' + str(len(bundled)) +
        ')</summary><p class="pj-pyinfo-note">Activate with mzpjUseLibrary(name). '
        'Bundled versions are independent of packages installed in this interpreter.</p><ul>' +
        ''.join('<li><span>' + escape(item['Library']) + '</span> <small>' +
                escape(item['Version']) + (' · active' if item['Active'] else '') +
                '</small></li>' for item in bundled) + '</ul>' +
        ('<p class="pj-pyinfo-note">The bundled library cache is unavailable.</p>'
         if bundled and not bundled[0]['Available'] else '') + '</details>') if bundled else ''
    return '''<section class="pj-pyinfo">
<style>
.pj-pyinfo { width: 960px; max-width: 100%; color: #1e293b; font: 13px/1.55 sans-serif; }
.pj-pyinfo .pj-pyinfo-header { display: flex; align-items: center; gap: 12px;
    border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; }
.pj-pyinfo h3 { margin: 0; font-size: 16px; font-weight: 600; }
.pj-pyinfo .pj-pyinfo-badge { color: #3e6da9; background: #f0f5fa;
    border-radius: 4px; padding: 2px 8px; font-size: 12px; }
.pj-pyinfo dl { margin: 12px 0 16px; }
.pj-pyinfo .pj-pyinfo-row { display: flex; gap: 14px; padding: 3px 0; }
.pj-pyinfo dt { flex: 0 0 90px; color: #64748b; }
.pj-pyinfo dd { margin: 0; min-width: 0; overflow-wrap: anywhere; }
.pj-pyinfo details { border-top: 1px solid #e2e8f0; padding-top: 10px; }
.pj-pyinfo summary { cursor: pointer; color: #3e6da9; font-weight: 600; }
.pj-pyinfo summary:focus-visible { outline: 2px solid #3e6da9; outline-offset: 3px; }
.pj-pyinfo ul { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
    column-gap: 0; list-style: none; padding: 0 6px 0 0; margin: 10px 0;
    max-height: 260px; overflow-y: auto; scrollbar-gutter: stable; }
.pj-pyinfo ul:focus-visible { outline: 2px solid #3e6da9; outline-offset: 3px; }
.pj-pyinfo li { min-width: 0; min-height: 26px; box-sizing: border-box;
    font-size: 12px; line-height: 20px; padding: 3px 8px; overflow-wrap: anywhere; }
.pj-pyinfo li:nth-child(8n+1), .pj-pyinfo li:nth-child(8n+2),
.pj-pyinfo li:nth-child(8n+3), .pj-pyinfo li:nth-child(8n+4) {
    background: rgba(62, 109, 169, 0.07); }
.pj-pyinfo small { color: #64748b; font-size: 11px; }
.pj-pyinfo .pj-pyinfo-note { color: #64748b; font-size: 12px; margin: 8px 0; }
</style>
<div class="pj-pyinfo-header"><h3>Python environment</h3>
<span class="pj-pyinfo-badge">''' + interpreter + '''</span></div>
<dl>''' + rows + '''</dl>''' + bundle_html + '''
<details><summary>Available libraries and modules (''' + str(len(libraries)) + ''')</summary>
<p class="pj-pyinfo-note">Detected in this interpreter without importing additional libraries.
Presence does not guarantee that all runtime dependencies can load.
Versions are shown when package metadata is available.</p>
<ul tabindex="0" aria-label="Available libraries and modules">''' + ''.join(libraries) + '''</ul></details>''' + diagnostics + '</section>'

