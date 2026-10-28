# file: inst/remote.py

import sys
import os
import json
import traceback
import base64
import io
import struct
from io import StringIO
from contextlib import redirect_stdout
from contextlib import ExitStack
import tempfile
import math

# L’unica sostituzione contiene esclusivamente base64, mai codice interpolato.
_config = json.loads(base64.b64decode('{{MZPJ_CONFIG}}').decode('utf-8'))
_pj_resources = _config.get('RESOURCES', {})
_pj_plot_js = _config.get('PLOT_JS', '')
_pj_plot_css = _config.get('PLOT_CSS', '')
_pj_chart_js = _config.get('CHART_JS', '')
_pj_plotly_gzip = _config.get('PLOTLY_GZIP', '')
_pj_library_catalog = _config.get('LIBRARY_CATALOG', {})
_pj_library_path = _config.get('LIBRARY_PATH')
_pj_library_error = _config.get('LIBRARY_ERROR', '')
for _key in ('DATASET', 'OUTPATH', 'CODE', 'SCRIPT_NAMES', 'EXTSCRIPT',
             'DATASET_INLINE', 'EXTSCRIPT_INLINE', 'D3_INLINE', 'STDIO_MODE',
             'FIGWIDTH', 'FIGHEIGHT', 'OUTPUT_MODE', 'PYTHON_MODE', 'SAVECOLUMNS'):
    globals()[_key] = _config[_key]
data = {}
results = {'items': []}
initial_headers = set()
# Namespace condiviso intenzionale; funziona anche con Python host in Flatpak.
for _service in _config['SERVICES']:
    exec(compile(_service['source'], _service['filename'], 'exec'), globals())
del _service, _config, _key

def _pj_report_error(exc, sources, active_source):
    """Conserva origine e chiamate dell'utente, senza esporre i frame del modulo."""
    frames = [
        (frame.filename, frame.lineno, frame.name)
        for frame in traceback.extract_tb(exc.__traceback__)
        if frame.filename in sources
    ]
    syntax = isinstance(exc, SyntaxError) and exc.filename in sources
    if syntax:
        frames.append((exc.filename, exc.lineno, '<module>'))

    source_id, line_no, function = frames[-1] if frames else (active_source, None, '<module>')
    label, source = sources[source_id]
    detail = exc.msg if syntax else str(exc)
    location = f' — line {line_no}' if line_no else ''
    message = [f'{label}{location} — {type(exc).__name__}: {detail}']

    def instruction(filename, number):
        lines = sources[filename][1].splitlines()
        return lines[number - 1] if number and 0 < number <= len(lines) else ''

    statement = instruction(source_id, line_no)
    if statement.strip():
        message.append('    ' + statement.lstrip())
        if syntax and exc.offset:
            # offset e' riferito alla riga originale, inclusa l'indentazione.
            prefix = statement[:max(0, exc.offset - 1)].expandtabs(4)
            indentation = len(statement) - len(statement.lstrip())
            removed = len(statement[:indentation].expandtabs(4))
            message.append('    ' + ' ' * max(0, len(prefix) - removed) + '^')

    for filename, number, function in reversed(frames[:-1]):
        caller = sources[filename][0]
        context = f' ({function})' if function != '<module>' else ''
        message.append(f'Called from {caller} — line {number}{context}')
        statement = instruction(filename, number)
        if statement.strip():
            message.append('    ' + statement.lstrip())

    # Un record JSON mantiene righe, Unicode e messaggi multilinea tra Python e R.
    print('__PJ_ERROR__ ' + json.dumps({'message': '\n'.join(message)}), file=sys.stderr)
    traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)

def execute_user_code(code, ext_script_path=""):
    local_vars = globals().copy()
    editor_source = '<pj-editor>'
    service_source = '<pj-service>'
    sources = {
        editor_source: (SCRIPT_NAMES.get('editor', 'Python editor'), code),
        service_source: (SCRIPT_NAMES.get('service', 'Service script'), '')
    }
    
    local_vars['data'] = data
    local_vars['np'] = np
    local_vars['math'] = math
    local_vars['stats'] = stats
    local_vars['matplotlib'] = matplotlib
    local_vars['plt'] = plt
    local_vars['mzpjShowImage'] = _pj_add_image
    local_vars['mzpjShowHtml'] = _pj_add_html
    local_vars['mzpjShowText'] = _pj_add_text
    local_vars['mzpjShowTable'] = _pj_add_table
    local_vars['mzpjShowScatter'] = _pj_show_scatter
    local_vars['mzpjShowHistogram'] = _pj_show_histogram
    local_vars['mzpjShowBoxPlot'] = _pj_show_boxplot
    local_vars['mzpjShowBar'] = _pj_show_bar
    local_vars['mzpjShowLine'] = _pj_show_line
    local_vars['mzpjShowIntervals'] = _pj_show_intervals
    local_vars['mzpjShowDistribution'] = _pj_show_distribution
    local_vars['mzpjShowCorrelation'] = _pj_show_correlation
    local_vars['mzpjShowPaired'] = _pj_show_paired
    local_vars['mzpjShowTestDistribution'] = _pj_show_test_distribution
    local_vars['mzpjShowChart'] = _pj_show_chart
    local_vars['mzpjShowPlotly'] = _pj_show_plotly
    local_vars['mzpjRecode'] = _pj_recode
    local_vars['mzpjRowStatistic'] = _pj_row_statistic
    local_vars['mzpjStandardize'] = _pj_standardize
    local_vars['mzpjRank'] = _pj_rank
    local_vars['mzpjEffectSize'] = _pj_effect_size
    local_vars['mzpjEffectInterval'] = _pj_effect_interval
    local_vars['mzpjSamplingVariance'] = _pj_sampling_variance
    local_vars['mzpjMetaWeights'] = _pj_meta_weights
    local_vars['mzpjFigureSize'] = {
        'width': _pj_figure_dimension(FIGWIDTH, 600),
        'height': _pj_figure_dimension(FIGHEIGHT, 500)
    }
    local_vars['d3_js'] = D3_INLINE
    local_vars['d3_script'] = (
        f"<script>{D3_INLINE}</script>"
        if D3_INLINE
        else ""
    )
    local_vars['results'] = results

    resource_directory = None

    def resource_path(filename):
        """Materializza soltanto le risorse incluse, nell'ambiente dell'interprete scelto."""
        nonlocal resource_directory
        if not isinstance(filename, str) or filename not in _pj_resources:
            raise FileNotFoundError(f'Pj resource not found: {filename!r}.')
        if not resource_directory:
            resource_directory = resource_stack.enter_context(
                tempfile.TemporaryDirectory(prefix='mzpj-'))
        path = os.path.join(resource_directory, filename)
        if not os.path.exists(path):
            with open(path, 'wb') as resource_file:
                resource_file.write(base64.b64decode(_pj_resources[filename], validate=True))
        return path

    local_vars['mzpjResourcePath'] = resource_path
    
    f = StringIO()
    # La directory temporanea viene creata su richiesta e rimossa anche in caso di errore.
    with redirect_stdout(f), ExitStack() as resource_stack:
        try:
            # Script esterno opzionale (opzione File 'scriptFile'): eseguito
            # PRIMA del codice utente, nello stesso namespace, cosi' le funzioni/
            # classi/variabili che definisce sono direttamente utilizzabili senza
            # bisogno di 'import' (il file sul disco ha un nome basato sull'hash
            # di sessione, non il nome originale, quindi 'import' non sarebbe
            # comunque praticabile)
            if ext_script_path or (
                STDIO_MODE.lower() == 'true' and
                EXTSCRIPT_INLINE
            ):
                try:

                    if STDIO_MODE.lower() == 'true':
                        ext_code = EXTSCRIPT_INLINE
                    else:
                        with open(
                            ext_script_path,
                            'r',
                            encoding='utf-8'
                        ) as ext_f:
                            ext_code = ext_f.read()

                    sources[service_source] = (sources[service_source][0], ext_code)
                    exec(compile(ext_code, service_source, 'exec'), local_vars)
                except (Exception, SystemExit) as e:
                    _pj_report_error(e, sources, service_source)
                    return f.getvalue()
            exec(compile(code, editor_source, 'exec'), local_vars)
        except (Exception, SystemExit) as e:
            _pj_report_error(e, sources, editor_source)

    return f.getvalue()


def main():
    global data, results, initial_headers
    
    local_figwidth = _pj_figure_dimension(FIGWIDTH, 600)
    local_figheight = _pj_figure_dimension(FIGHEIGHT, 500)
        
    local_echo = OUTPUT_MODE == 'echo'
    local_pyinfo = OUTPUT_MODE == 'pyinfo'

    # Dimensione di default delle figure matplotlib, dalle impostazioni
    # Figure size dell'interfaccia - solo un default: plt.figure(figsize=...)
    # nel codice dell'utente lo sovrascrive normalmente
    if plt is not None:
        plt.rcParams['figure.figsize'] = (local_figwidth / 100, local_figheight / 100)

    # JSON tipizzato: niente conversioni dei nomi/etichette numeriche in float.
    try:
        if STDIO_MODE.lower() == 'true':
            data = json.loads(DATASET_INLINE)
        else:
            with open(DATASET, 'r', encoding='utf-8') as stream:
                data = json.load(stream)
        if not isinstance(data, dict) or any(not isinstance(v, list) for v in data.values()):
            raise ValueError('Expected an object containing column arrays.')
        if len({len(v) for v in data.values()}) > 1:
            raise ValueError('Dataset columns have different lengths.')
        initial_headers = set(data)
    except Exception as e:
        print(f'ERROR: Error loading dataset: {e}', file=sys.stderr)
        return

    # Esecuzione del codice
    console_output = execute_user_code(CODE, EXTSCRIPT)
    
    # Rilevamento automatico e pacchettizzazione delle nuove colonne (Output 'createdColumns')
    if SAVECOLUMNS.lower() == 'true':
        created_columns = []
        for col_name, col_values in data.items():
            if col_name not in initial_headers:
                try:
                    safe_values = _json_safe_column(col_values)
                except Exception as e:
                    print(f"ERROR: Could not serialize column '{col_name}': {e}", file=sys.stderr)
                    continue
                created_columns.append({
                    "name": col_name,
                    "values": safe_values
                })
        
        # L'elenco vuoto rimuove gli Output precedenti di questa analisi sul server jamovi.
        results["items"].append({
            "type": "Output",
            "name": "createdColumns",
            "columns": created_columns
        })
    
    # Il report informativo e' indipendente dai risultati dello script.
    if local_pyinfo:
        try:
            info_content = _pj_python_info()
        except Exception:
            info_content = '<p>Python environment information is unavailable.</p>'
        info_name = 'pythonInfo'
        used_names = {item.get('name') for item in results['items']}
        while info_name in used_names:
            info_name += '_'
        results['items'].insert(0, {
            'type': 'Html',
            'name': info_name,
            'title': 'Python environment',
            'content': info_content
        })

    # Mantiene la console Preformatted anche quando il report e' attivo.
    content = None
    if console_output.strip() or local_echo:
        content = ""
        if local_echo:
            content += "## Executed Python Code:\n" + CODE.strip() + "\n\n"
        if console_output.strip():
            content += console_output

    if content is not None:
        results["items"].insert(0, {
            "type": "Preformatted",
            "name": "console", 
            "title": "Output Console",
            "content": content
        })
    
    # Output JSON.
    # In modalita' STDIO il risultato torna direttamente al processo R.
    # Nella modalita' normale resta il file JSON originale.
    try:

        if STDIO_MODE.lower() == 'true':

            print(
                "__PJ_RESULT__ " +
                json.dumps(results, ensure_ascii=False)
            )

        else:

            with open(
                OUTPATH,
                'w',
                encoding='utf-8'
            ) as f:
                json.dump(
                    results,
                    f,
                    indent=4
                )

            print("OK")

    except Exception as e:
        print(
            f"ERROR: Error writing JSON output: {e}",
            file=sys.stderr
        )

if __name__ == "__main__":
    main()
