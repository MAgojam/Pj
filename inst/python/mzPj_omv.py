# Lettura e scrittura di file jamovi .omv con la sola libreria standard di Python.
#
# Fonti del formato (nessuna parte e' ricavata a memoria):
#   - jamovi-src/server/jamovi/server/formatio/omv.py: scrittura jamovi-Archive-Version 11.0,
#     lettura fino alla versione 12.x;
#   - jamovi-src/server/jamovi/core.pyx: valori testuali di ColumnType, DataType e MeasureType;
#   - jmvReadWrite (R/read_omv.R, R/write_omv.R, R/globals.R): secondo riferimento.
# Un .omv e' un archivio ZIP: meta, metadata.json, xdata.json (etichette dei livelli),
# data.bin (colonne una dopo l'altra, little endian), strings.bin (solo per le colonne ID
# testuali), index.html e le analisi. Le analisi non sono gestite da questa libreria.
#
# Funzioni pubbliche: mzpjReadOmv e mzpjWriteOmv. Le funzioni interne iniziano con _pj_omv_.
import json
import math
import os
import re
import struct
import tempfile
import zipfile
import base64
from collections.abc import Mapping, Sequence
from numbers import Integral, Real

# Valore mancante delle colonne intere e degli indici nella tabella delle stringhe.
_PJ_OMV_MISSING = -2147483648
_PJ_OMV_INT_MAX = 2147483647
# Versione scritta (come jamovi) e prima versione maggiore che jamovi rifiuta in lettura.
_PJ_OMV_WRITTEN_VERSION = '11.0'
_PJ_OMV_NEWEST_MAJOR = 12
_PJ_OMV_SPEC_KEYS = frozenset((
    'name', 'id', 'columnType', 'dataType', 'measureType', 'description', 'formula',
    'formulaMessage', 'parentId', 'width', 'importName', 'transform', 'edits',
    'missingValues', 'trimLevels', 'levels', 'filterNo', 'active',
    'outputAnalysisId', 'outputOptionName', 'outputName',
    'outputDesiredColumnName', 'outputAssignedColumnName'))


def _pj_omv_entry(archive, name):
    try:
        return archive.read(name)
    except KeyError:
        raise ValueError(f"File is corrupt ('{name}' is missing).") from None


def _pj_omv_json(archive, name):
    raw = _pj_omv_entry(archive, name)
    try:
        return json.loads(raw.decode('utf-8'))
    except ValueError as error:
        raise ValueError(f"File is corrupt ('{name}' is not valid JSON: {error}).") from None


def _pj_omv_archive_version(archive):
    # Come jamovi: prima 'meta', poi il vecchio META-INF/MANIFEST.MF.
    text = None
    names = archive.namelist()
    for entry in ('meta', 'META-INF/MANIFEST.MF'):
        if entry in names:
            try:
                text = archive.read(entry).decode('utf-8')
                break
            except UnicodeDecodeError:
                text = None
    if text is None:
        raise ValueError('File is corrupt (manifest is corrupt or missing).')
    found = re.search(r'^jamovi-Archive-Version: ?([0-9]+)\.([0-9]+)[ \t]*\r?$', text, re.MULTILINE)
    if not found:
        raise ValueError('File is corrupt (manifest is corrupt).')
    version = (int(found.group(1)), int(found.group(2)))
    if version[0] > _PJ_OMV_NEWEST_MAJOR:
        raise ValueError('A newer version of jamovi is required to read this file.')
    return version


def _pj_omv_types(field):
    # Stesse regole di jamovi, comprese quelle dei file vecchi senza dataType.
    measure = field.get('measureType', 'Nominal')
    data_type = field.get('dataType')
    if data_type is None:
        if measure == 'NominalText':
            return 'Text', 'Nominal'
        if measure == 'Continuous':
            return 'Decimal', 'Continuous'
        data_type = 'Integer'
    elif data_type not in ('Integer', 'Decimal', 'Text'):
        data_type = 'Integer'
    if measure not in ('Continuous', 'Ordinal', 'Nominal', 'ID', 'None'):
        measure = 'Continuous'
    return data_type, measure


def _pj_omv_string(table, offset):
    # Stringa terminata da NUL a partire da offset; offset non valido come in jamovi: stringa vuota.
    if table is None:
        return str(offset)
    if offset < 0 or offset >= len(table):
        return ''
    end = table.find(b'\x00', offset)
    if end < 0:
        end = len(table)
    return table[offset:end].decode('utf-8', errors='ignore')


def _pj_omv_read(path, labels=True, max_bytes=256 * 1024**2):
    if not isinstance(labels, bool):
        raise TypeError('labels must be True or False.')
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes <= 0:
        raise ValueError('max_bytes must be a positive integer.')
    try:
        archive = zipfile.ZipFile(os.fspath(path), 'r')
    except zipfile.BadZipFile:
        raise ValueError('The file is not a valid jamovi archive (it is not a ZIP file).') from None
    with archive:
        # Nomi duplicati rendono ambigua la selezione dei metadati da leggere.
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('File is corrupt (duplicate archive entries).')
        # Si leggono soltanto i dati, senza estrarre percorsi ZIP o analisi.
        required = {'meta', 'META-INF/MANIFEST.MF', 'metadata.json',
                    'xdata.json', 'data.bin', 'strings.bin'}
        if sum(item.file_size for item in archive.infolist() if item.filename in required) > max_bytes:
            raise ValueError('OMV dataset exceeds max_bytes; increase it explicitly for a trusted large dataset.')
        version = _pj_omv_archive_version(archive)
        metadata = _pj_omv_json(archive, 'metadata.json')
        if not isinstance(metadata, dict) or not isinstance(metadata.get('dataSet'), dict):
            raise ValueError("File is corrupt ('metadata.json' has no dataSet).")
        dataset = metadata['dataSet']
        fields = dataset.get('fields')
        row_count = dataset.get('rowCount')
        if (not isinstance(fields, list) or isinstance(row_count, bool)
                or not isinstance(row_count, int) or row_count < 0):
            raise ValueError("File is corrupt ('metadata.json' has invalid fields or rowCount).")
        document = metadata.get('document')
        results_language = document.get('resultsLanguage', 'en') if isinstance(document, dict) else 'en'

        columns = []
        seen = set()
        for field in fields:
            if not isinstance(field, dict) or not isinstance(field.get('name'), str):
                raise ValueError("File is corrupt (a field has no name).")
            name = field['name']
            if name in seen:
                raise ValueError(f"File is corrupt (duplicate column name '{name}').")
            seen.add(name)
            data_type, measure = _pj_omv_types(field)
            column_type = field.get('columnType', 'Data')
            column = {
                'name': name,
                'id': field.get('id', 0),
                'columnType': column_type,
                'dataType': data_type,
                'measureType': measure,
                'description': field.get('description', ''),
                'formula': field.get('formula', ''),
                'formulaMessage': field.get('formulaMessage', ''),
                'parentId': field.get('parentId', 0),
                'width': field.get('width', 78 if column_type == 'Filter' else 100),
                'importName': field.get('importName', name),
                'transform': field.get('transform', 0),
                'edits': field.get('edits', []),
                'missingValues': field.get('missingValues', []),
            }
            if 'trimLevels' in field:
                column['trimLevels'] = field['trimLevels']
            if column_type == 'Filter':
                column['filterNo'] = field.get('filterNo', -1)
                column['active'] = field.get('active', True)
            if column_type == 'Output':
                for key in ('outputAnalysisId', 'outputOptionName', 'outputName',
                            'outputDesiredColumnName', 'outputAssignedColumnName'):
                    column[key] = field.get(key)
            columns.append(column)

        # Etichette dei livelli (xdata.json). Colonne senza etichette valide: livelli ricostruiti
        # dai valori, come fa jamovi in lettura.
        level_table = {}
        repair = set()
        try:
            xdata = _pj_omv_json(archive, 'xdata.json')
            if not isinstance(xdata, dict):
                raise ValueError('xdata')
            for column in columns:
                entry = xdata.get(column['name'])
                if entry is None:
                    continue
                try:
                    raw_labels = entry['labels']
                    if not raw_labels:
                        repair.add(column['name'])
                        continue
                    converted = []
                    for label in raw_labels:
                        import_value = label[2] if len(label) > 2 else label[1]
                        if import_value == '':
                            import_value = label[1]
                        pinned = label[3] if len(label) > 3 else column.get('trimLevels', True) is False
                        converted.append((label[0], label[1], import_value, bool(pinned)))
                    level_table[column['name']] = converted
                except Exception:
                    repair.add(column['name'])
        except Exception:
            repair = {c['name'] for c in columns if c['measureType'] != 'Continuous'}

        names = archive.namelist()
        if 'data.bin' in names:
            blob = archive.read('data.bin')
        elif row_count == 0:
            blob = b''
        else:
            raise ValueError("File is corrupt ('data.bin' is missing).")
        table = archive.read('strings.bin') if 'strings.bin' in names else None

        data = {}
        offset = 0
        for column in columns:
            name = column['name']
            decimal = column['dataType'] == 'Decimal'
            is_id = column['dataType'] == 'Text' and column['measureType'] == 'ID'
            size = (8 if decimal else 4) * row_count
            if offset + size > len(blob):
                raise ValueError("File is corrupt ('data.bin' is shorter than the metadata requires).")
            if decimal:
                raw = struct.unpack_from('<%dd' % row_count, blob, offset)
                values = [None if math.isnan(v) else v for v in raw]
            else:
                raw = struct.unpack_from('<%di' % row_count, blob, offset)
                if is_id:
                    values = []
                    for v in raw:
                        text = None if v == _PJ_OMV_MISSING else _pj_omv_string(table, v)
                        values.append(text if text else None)
                else:
                    values = [None if v == _PJ_OMV_MISSING else v for v in raw]
                    if name in repair:
                        repaired = []
                        known = set()
                        for v in values:
                            if v is not None and v not in known:
                                known.add(v)
                                repaired.append((v, str(v), str(v), False))
                        if repaired:
                            level_table[name] = repaired
            offset += size

            if column['columnType'] == 'Filter':
                values = [None if v is None else bool(v) for v in values]
            elif name in level_table:
                column['levels'] = level_table[name]
                if labels:
                    mapping = {item[0]: item[1] for item in level_table[name]}
                    values = [None if v is None else mapping.get(v, v) for v in values]
            data[name] = values

        return {
            'data': data,
            'columns': columns,
            'row_count': row_count,
            'weights': dataset.get('weights') or None,
            'results_language': results_language,
            'archive_version': version,
            'entries': names,
        }


def mzpjReadOmv(path=None, labels=True, *, max_bytes=256 * 1024**2):
    """Read the data set of a jamovi .omv file; analyses stored in the file are ignored.

    Returns a dictionary with 'data' (dictionary of lists, None for missing values),
    'columns' (one metadata dictionary per column), 'row_count', 'weights',
    'results_language', 'archive_version' and 'entries' (names inside the archive).
    With labels=True a column that has levels is returned as its label texts; with
    labels=False as the stored codes. Filter columns are returned as True/False.
    max_bytes limits the combined uncompressed dataset entries (default 256 MiB).
    Stored missing-value rules are metadata: their matching values remain in data.
    Raises ValueError when the file is not a readable jamovi archive.
    """
    if path is None:
        raise ValueError('Read... loads dataext directly. Pass an explicit path to mzpjReadOmv().')
    return _pj_omv_read(path, labels, max_bytes)


def _pj_omv_is_bool(value):
    return isinstance(value, bool) or (
        type(value).__module__ == 'numpy' and type(value).__name__ in ('bool_', 'bool'))


def _pj_omv_classify(values, name):
    kinds = set()
    for value in values:
        if value is None:
            continue
        if _pj_omv_is_bool(value):
            kinds.add('bool')
        elif isinstance(value, str):
            kinds.add('str')
        elif isinstance(value, Integral):
            kinds.add('int')
        elif isinstance(value, Real):
            number = float(value)
            if math.isnan(number):
                continue
            if math.isinf(number):
                raise ValueError(f"Column '{name}' contains an infinite value.")
            kinds.add('float')
        else:
            raise TypeError(f"Column '{name}' contains an unsupported value type: {type(value).__name__}.")
    if not kinds:
        return 'empty'
    if kinds == {'int', 'float'}:
        return 'float'
    if len(kinds) > 1:
        raise TypeError(f"Column '{name}' mixes value types ({', '.join(sorted(kinds))}).")
    return kinds.pop()


def _pj_omv_level_entries(name, levels, data_type):
    # Normalizza le etichette in tuple (valore, etichetta, valore di importazione, bloccato).
    if isinstance(levels, Mapping):
        items = list(levels.items())
    elif isinstance(levels, (str, bytes)) or not isinstance(levels, Sequence):
        raise TypeError(f"Column '{name}': levels must be a list or a dictionary.")
    else:
        items = []
        for position, item in enumerate(levels):
            if isinstance(item, str):
                items.append((position, item))
            elif isinstance(item, (tuple, list)) and 2 <= len(item) <= 4:
                items.append(tuple(item))
            else:
                raise TypeError(f"Column '{name}': each level must be a text or a (value, label) tuple.")
    entries = []
    for item in items:
        value, label = item[0], item[1]
        import_value = item[2] if len(item) > 2 and item[2] != '' else label
        pinned = bool(item[3]) if len(item) > 3 else False
        if isinstance(value, bool) or not isinstance(value, Integral):
            raise TypeError(f"Column '{name}': level values must be integers.")
        if not isinstance(label, str) or not isinstance(import_value, str):
            raise TypeError(f"Column '{name}': level labels must be texts.")
        if not -_PJ_OMV_INT_MAX <= int(value) <= _PJ_OMV_INT_MAX:
            raise ValueError(f"Column '{name}': a level value is outside the integer range.")
        entries.append((int(value), label, import_value, pinned))
    if len({e[0] for e in entries}) != len(entries) or len({e[1] for e in entries}) != len(entries):
        raise ValueError(f"Column '{name}': level values and labels must be unique.")
    if data_type == 'Text' and [e[0] for e in entries] != list(range(len(entries))):
        raise ValueError(f"Column '{name}': for Text columns the level values must be 0, 1, 2, ... in order.")
    return entries


def _pj_omv_check_text(name, values):
    for value in values:
        if value is not None and '\x00' in value:
            raise ValueError(f"Column '{name}' contains a text with a NUL character.")


def _pj_omv_prepare(name, values, spec):
    # Anche NaN NumPy rappresenta un mancante, prima di ricodificare i booleani.
    values = [None if isinstance(v, Real) and not isinstance(v, Integral)
              and math.isnan(v) else v for v in values]
    column_type = spec.get('columnType', 'Data')
    if column_type not in ('Data', 'Computed', 'Recoded', 'Filter'):
        raise ValueError(f"Column '{name}': columnType must be Data, Computed, Recoded or Filter.")
    measure = spec.get('measureType')
    data_type = spec.get('dataType')
    levels_in = spec.get('levels')
    if measure not in (None, 'Nominal', 'Ordinal', 'Continuous', 'ID'):
        raise ValueError(f"Column '{name}': measureType must be Nominal, Ordinal, Continuous or ID.")
    if data_type not in (None, 'Integer', 'Decimal', 'Text'):
        raise ValueError(f"Column '{name}': dataType must be Integer, Decimal or Text.")
    kind = _pj_omv_classify(values, name)

    stored = None
    labels = []
    if measure == 'ID' and data_type not in ('Integer', 'Decimal'):
        if kind not in ('empty', 'str', 'int'):
            raise TypeError(f"Column '{name}': ID columns need text or integer values.")
        if levels_in is not None:
            raise ValueError(f"Column '{name}': ID columns have no levels.")
        data_type = 'Text'
        stored = [None if v is None or v == '' else str(v) for v in values]
        _pj_omv_check_text(name, stored)
        storage = 's'
    else:
        booleans = kind == 'bool'
        if booleans:
            values = [None if v is None else int(bool(v)) for v in values]
            kind = 'int'
        if kind == 'str' and data_type == 'Integer':
            # Colonna intera con livelli letta con le etichette: le etichette tornano ai codici.
            measure = measure or 'Nominal'
            if levels_in is None or measure not in ('Nominal', 'Ordinal'):
                raise TypeError(f"Column '{name}': text values in an Integer column need levels "
                                "and a Nominal or Ordinal measureType.")
            lookup = {e[1]: e[0] for e in _pj_omv_level_entries(name, levels_in, 'Integer')}
            converted = []
            for v in values:
                if v is None or v == '':
                    converted.append(None)
                elif v in lookup:
                    converted.append(lookup[v])
                else:
                    raise ValueError(f"Column '{name}': the value {v!r} is not in levels.")
            values = converted
            kind = 'int'
        if kind == 'int' and data_type == 'Text' and levels_in is not None:
            # Colonna testuale letta con labels=False: i codici tornano alle etichette.
            label_of = {e[0]: e[1] for e in _pj_omv_level_entries(name, levels_in, 'Text')}
            converted = []
            for v in values:
                if v is None:
                    converted.append(None)
                elif v in label_of:
                    converted.append(label_of[v])
                else:
                    raise ValueError(f"Column '{name}': the code {v!r} is not in levels.")
            values = converted
            kind = 'str'
        if kind == 'int' and data_type != 'Decimal':
            if any(v is not None and abs(v) > _PJ_OMV_INT_MAX for v in values):
                if data_type == 'Integer':
                    raise ValueError(f"Column '{name}': a value is outside the integer range.")
                if any(v is not None and int(float(v)) != v for v in values):
                    raise ValueError(f"Column '{name}': an integer cannot be stored as Decimal without precision loss; use text IDs.")
                kind = 'float'
        if (kind == 'float' and data_type in (None, 'Integer')
                and all(v is None or (float(v).is_integer() and abs(v) <= _PJ_OMV_INT_MAX)
                        for v in values if not (isinstance(v, float) and math.isnan(v)))):
            # Valori decimali tutti interi: come jmvReadWrite, colonna intera.
            values = [None if v is None or (isinstance(v, float) and math.isnan(v)) else int(v) for v in values]
            kind = 'int'
        if kind == 'str':
            if data_type not in (None, 'Text'):
                raise TypeError(f"Column '{name}': text values need dataType Text.")
            data_type = 'Text'
            measure = measure or 'Nominal'
        elif kind in ('int', 'float'):
            if data_type is None:
                data_type = 'Integer' if kind == 'int' else 'Decimal'
            if data_type == 'Text':
                raise TypeError(f"Column '{name}': numeric values cannot have dataType Text.")
            if data_type == 'Integer' and kind == 'float':
                raise ValueError(f"Column '{name}': dataType Integer needs whole numbers.")
            measure = measure or ('Nominal' if booleans else 'Continuous')
        else:
            data_type = data_type or 'Integer'
            measure = measure or 'Nominal'
        if data_type == 'Decimal' and measure not in ('Continuous', 'ID'):
            raise ValueError(f"Column '{name}': Decimal columns must be Continuous or ID.")
        if data_type == 'Text' and measure == 'Continuous':
            raise ValueError(f"Column '{name}': Text columns cannot be Continuous.")
        has_levels = measure in ('Nominal', 'Ordinal') and data_type in ('Integer', 'Text')
        if levels_in is not None and not has_levels:
            raise ValueError(f"Column '{name}': levels need a Nominal or Ordinal Integer or Text column.")

        if has_levels and data_type == 'Text':
            if levels_in is None:
                present = sorted({v for v in values if v is not None and v != ''})
                labels = _pj_omv_level_entries(name, present, 'Text')
            else:
                labels = _pj_omv_level_entries(name, levels_in, 'Text')
            index = {e[1]: e[0] for e in labels}
            _pj_omv_check_text(name, [v for v in values if v is not None])
            stored = []
            for v in values:
                if v is None or v == '':
                    stored.append(_PJ_OMV_MISSING)
                elif v in index:
                    stored.append(index[v])
                else:
                    raise ValueError(f"Column '{name}': the value {v!r} is not in levels.")
            storage = 'i'
        elif has_levels:
            if levels_in is not None:
                labels = _pj_omv_level_entries(name, levels_in, 'Integer')
            elif booleans:
                labels = [(1, 'TRUE', 'TRUE', False), (0, 'FALSE', 'FALSE', False)]
            else:
                labels = [(v, str(v), str(v), False) for v in sorted({v for v in values if v is not None})]
            known = {e[0] for e in labels}
            for v in values:
                if v is not None and v not in known:
                    raise ValueError(f"Column '{name}': the value {v!r} is not in levels.")
            stored = [_PJ_OMV_MISSING if v is None else int(v) for v in values]
            storage = 'i'
        elif data_type == 'Decimal':
            if any(isinstance(v, Integral) and int(float(v)) != v for v in values if v is not None):
                raise ValueError(f"Column '{name}': an integer cannot be stored as Decimal without precision loss; use text IDs.")
            stored = [float('nan') if v is None or (isinstance(v, float) and math.isnan(v)) else float(v)
                      for v in values]
            storage = 'd'
        else:
            stored = [_PJ_OMV_MISSING if v is None else int(v) for v in values]
            storage = 'i'
        if column_type == 'Filter':
            if data_type != 'Integer' or any(v is not None and v not in (0, 1) for v in values):
                raise ValueError(f"Column '{name}': Filter columns need Integer values 0, 1 or missing.")

    if column_type == 'Filter' and ('filterNo' not in spec or 'active' not in spec):
        raise ValueError(f"Column '{name}': Filter columns need filterNo and active in the metadata "
                         "(copy them from mzpjReadOmv).")
    return {'storage': storage, 'values': stored, 'labels': labels, 'column_type': column_type,
            'data_type': data_type, 'measure': measure}


def _pj_omv_spec_map(meta, names):
    if meta is None:
        return {}
    if isinstance(meta, Mapping):
        items = list(meta.items())
    elif isinstance(meta, Sequence) and not isinstance(meta, (str, bytes)):
        items = []
        for entry in meta:
            if not isinstance(entry, Mapping) or not isinstance(entry.get('name'), str):
                raise TypeError("meta must be a dictionary of column metadata or a list of dictionaries with a name.")
            items.append((entry['name'], entry))
    else:
        raise TypeError("meta must be a dictionary of column metadata or a list of dictionaries with a name.")
    result = {}
    for name, spec in items:
        if name not in names:
            raise ValueError(f"meta describes the column '{name}', which is not in data.")
        if not isinstance(spec, Mapping):
            raise TypeError(f"meta for column '{name}' must be a dictionary.")
        if spec.get('name', name) != name:
            raise ValueError(f"meta for column '{name}' has a different name.")
        unknown = set(spec) - _PJ_OMV_SPEC_KEYS
        if unknown:
            raise ValueError(f"meta for column '{name}' has unsupported keys: {', '.join(sorted(unknown))}.")
        result[name] = dict(spec)
    return result


def _pj_omv_text_value(name, spec, key, default=''):
    value = spec.get(key, default)
    if not isinstance(value, str):
        raise TypeError(f"meta for column '{name}': {key} must be a text.")
    return value


def _pj_omv_int_value(name, spec, key, default):
    value = spec.get(key, default)
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"meta for column '{name}': {key} must be an integer.")
    return int(value)


def _pj_omv_write(path, data, meta, weights, results_language, overwrite, html):
    if not isinstance(overwrite, bool):
        raise TypeError('overwrite must be True or False.')
    if html is not None and not isinstance(html, str):
        raise TypeError('html must be a text or None.')
    path = os.fspath(path)
    if not path.lower().endswith('.omv'):
        raise ValueError("The file name must end with '.omv'.")
    directory = os.path.dirname(os.path.abspath(path))
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"The folder '{directory}' does not exist.")
    if os.path.exists(path) and not overwrite:
        raise FileExistsError(f"'{path}' already exists; use overwrite=True to replace it.")
    if not isinstance(data, Mapping) or not data:
        raise TypeError('data must be a non-empty dictionary of columns.')
    columns = {}
    for name, values in data.items():
        if not isinstance(name, str) or not name:
            raise ValueError('Column names must be non-empty texts.')
        if isinstance(values, (str, bytes, Mapping)):
            raise TypeError(f"Column '{name}' must be a one-dimensional sequence.")
        try:
            columns[name] = list(values)
        except TypeError:
            raise TypeError(f"Column '{name}' must be a one-dimensional sequence.") from None
    lengths = {len(values) for values in columns.values()}
    if len(lengths) != 1:
        raise ValueError('All columns must have the same number of rows.')
    row_count = lengths.pop()
    if not isinstance(results_language, str) or not results_language:
        raise ValueError('results_language must be a non-empty text.')
    specs = _pj_omv_spec_map(meta, columns)
    # Un nuovo dataset non possiede analisi, trasformazioni o dipendenze di
    # calcolo originali: si salvano i valori correnti, senza formule attive.
    for name, spec in specs.items():
        if spec.get('columnType', 'Data') not in ('Data', 'Computed', 'Recoded', 'Filter', 'Output'):
            raise ValueError(f"Column '{name}': unsupported columnType.")
        spec.update(columnType='Data', formula='', formulaMessage='', parentId=0, transform=0, edits=[])

    prepared = {}
    for name, values in columns.items():
        prepared[name] = _pj_omv_prepare(name, values, specs.get(name, {}))
    if weights is not None:
        if weights not in prepared or prepared[weights]['data_type'] == 'Text':
            raise ValueError('weights must name a numeric column of data.')

    # Identificatori: si tengono se tutti presenti e unici, altrimenti 1..n (come jmvReadWrite).
    wanted = [specs.get(name, {}).get('id') for name in columns]
    if (any(isinstance(i, bool) or not isinstance(i, Integral) or i <= 0 for i in wanted)
            or len(set(wanted)) != len(wanted)):
        wanted = list(range(1, len(columns) + 1))

    fields = []
    xdata = {}
    data_bin = bytearray()
    strings_bin = bytearray()
    for column_id, (name, column) in zip(wanted, prepared.items()):
        spec = specs.get(name, {})
        is_filter = column['column_type'] == 'Filter'
        kind = {'d': 'number', 's': 'string', 'i': 'integer'}[column['storage']]
        field = {
            'name': name,
            'id': int(column_id),
            'columnType': column['column_type'],
            'dataType': column['data_type'],
            'measureType': column['measure'],
            'formula': _pj_omv_text_value(name, spec, 'formula'),
            'formulaMessage': _pj_omv_text_value(name, spec, 'formulaMessage'),
            'parentId': _pj_omv_int_value(name, spec, 'parentId', 0),
            'width': _pj_omv_int_value(name, spec, 'width', 78 if is_filter else 100),
            'type': kind,
            'importName': _pj_omv_text_value(name, spec, 'importName'),
            'description': _pj_omv_text_value(name, spec, 'description'),
            'transform': _pj_omv_int_value(name, spec, 'transform', 0),
            'edits': list(spec.get('edits', [])),
            'missingValues': list(spec.get('missingValues', [])),
        }
        if any(not isinstance(v, str) for v in field['missingValues']):
            raise TypeError(f"meta for column '{name}': missingValues must be a list of texts.")
        if is_filter:
            field['filterNo'] = _pj_omv_int_value(name, spec, 'filterNo', 0)
            field['active'] = bool(spec['active'])
        elif column['labels']:
            field['trimLevels'] = bool(spec.get('trimLevels', True))
        if column['labels']:
            xdata[name] = {'labels': [list(entry) for entry in column['labels']]}
        fields.append(field)

        values = column['values']
        if column['storage'] == 'd':
            data_bin += struct.pack('<%dd' % row_count, *values)
        elif column['storage'] == 'i':
            data_bin += struct.pack('<%di' % row_count, *values)
        else:
            offsets = []
            for text in values:
                if text is None:
                    offsets.append(_PJ_OMV_MISSING)
                else:
                    offsets.append(len(strings_bin))
                    strings_bin += text.encode('utf-8') + b'\x00'
            data_bin += struct.pack('<%di' % row_count, *offsets)

    metadata = {
        'document': {'resultsLanguage': results_language},
        'dataSet': {
            'rowCount': row_count,
            'columnCount': len(fields),
            'removedRows': [],
            'addedRows': [],
            'fields': fields,
            'transforms': [],
            'weights': weights,
        },
    }
    manifest = ('Manifest-Version: 1.0\n'
                'Data-Archive-Version: 1.0.2\n'
                f'jamovi-Archive-Version: {_PJ_OMV_WRITTEN_VERSION}\n'
                'Created-By: Pj mzpjWriteOmv\n')

    # Scrittura in un file temporaneo nella stessa cartella e sostituzione finale:
    # un errore non lascia mai un .omv a meta'.
    handle, temporary = tempfile.mkstemp(prefix='.mzpj-omv-', suffix='.tmp', dir=directory)
    os.close(handle)
    try:
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('meta', manifest.encode('utf-8'), zipfile.ZIP_DEFLATED)
            if html is not None:
                archive.writestr('index.html', html.encode('utf-8'), zipfile.ZIP_DEFLATED)
            archive.writestr('metadata.json', json.dumps(metadata).encode('utf-8'), zipfile.ZIP_DEFLATED)
            archive.writestr('xdata.json', json.dumps(xdata).encode('utf-8'), zipfile.ZIP_DEFLATED)
            archive.writestr('data.bin', bytes(data_bin), zipfile.ZIP_DEFLATED)
            if strings_bin:
                archive.writestr('strings.bin', bytes(strings_bin), zipfile.ZIP_DEFLATED)
        if overwrite:
            os.replace(temporary, path)
        else:
            # Pubblicazione atomica senza sovrascrittura: anche un file creato
            # da un altro processo dopo il controllo iniziale viene protetto.
            if os.name == 'nt':
                os.rename(temporary, path)
            else:
                os.link(temporary, path)
                os.remove(temporary)
    except BaseException:
        try:
            os.remove(temporary)
        except OSError:
            pass
        raise
    return {'path': path, 'row_count': row_count, 'column_count': len(fields)}


def mzpjWriteOmv(path, data, meta=None, weights=None, results_language=None, overwrite=False, html=None):
    """Write a dictionary of columns as a jamovi .omv file containing the data set only.

    data is a dictionary of equal-length lists; None (and NaN, and '' in text columns)
    means missing. Without meta the type is inferred: whole numbers -> Integer and
    Continuous, other numbers -> Decimal and Continuous, text -> Text and Nominal with
    the levels sorted, True/False -> Integer and Nominal with the labels TRUE/FALSE.
    meta is a dictionary {column: {...}} or the 'columns' list returned by mzpjReadOmv;
    allowed keys: measureType (Nominal, Ordinal, Continuous, ID), dataType (Integer,
    Decimal, Text), levels (list of labels, list of (value, label) tuples or a
    dictionary {value: label}), description, missingValues (for example ['== 99']),
    width, importName, trimLevels and id. Original role/formula metadata returned by
    mzpjReadOmv is accepted, but all columns are saved as ordinary Data columns:
    formulas, transforms, analysis-output links and active filters are not recreated.
    Filter values are saved as ordinary values; all rows are included.
    weights names a numeric column used as weights. html is optional index.html text.
    An existing file is replaced only with overwrite=True. Analyses are not written.
    Returns {'path', 'row_count', 'column_count'}.
    """
    if hasattr(data, '_pj_metadata'):
        stored = data._pj_metadata
        if meta is None:
            meta = [c for c in stored.get('columns', []) if c['name'] in data] or None
        if weights is None and stored.get('weights') in data:
            weights = stored['weights']
        if results_language is None:
            results_language = stored.get('results_language')
    if isinstance(data, Mapping) and isinstance(data.get('data'), Mapping):
        document = data
        meta = document.get('columns') if meta is None else meta
        weights = document.get('weights') if weights is None else weights
        if results_language is None:
            results_language = document.get('results_language', 'en')
        data = document['data']
    if results_language is None:
        results_language = 'en'
    return _pj_omv_write(path, data, meta, weights, results_language, overwrite, html)

