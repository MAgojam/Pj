# Trasformazioni di dataset, senza dipendenze opzionali; nessuna modifica in-place.
from collections.abc import Mapping
from functools import cmp_to_key
import copy
import math
from numbers import Real, Integral


def _pj_frame(value):
    external = hasattr(value, '_pj_metadata')
    document = isinstance(value, Mapping) and isinstance(value.get('data'), Mapping)
    data = value['data'] if document else value
    if not isinstance(data, Mapping) or not data or any(not isinstance(n, str) or not n for n in data):
        raise ValueError('A dataset must be a non-empty mapping of column names to sequences.')
    result = {}
    for name, column in data.items():
        if isinstance(column, (str, bytes, Mapping)):
            raise TypeError(f"Column '{name}' must be a sequence.")
        result[name] = list(column)
    if len({len(v) for v in result.values()}) != 1:
        raise ValueError('All columns must have equal length.')
    metadata = copy.deepcopy({k: v for k, v in value.items() if k != 'data'}) if document else None
    if external:
        metadata = copy.deepcopy(value._pj_metadata)
        metadata['_pj_external'] = True
    return result, metadata


def _pj_frame_result(data, document, columns=None):
    if document is None:
        return data
    document['data'] = data
    document['row_count'] = len(next(iter(data.values())))
    if columns is None:
        old = {c['name']: c for c in document.get('columns', [])}
        columns = [old.get(n, {'name': n}) for n in data]
    document['columns'] = columns
    if document.get('weights') not in data:
        document['weights'] = None
    if document.pop('_pj_external', False):
        return _PjExternalData(data, {k: v for k, v in document.items() if k != 'data'})
    return document


def _pj_names(names, data, argument):
    names = [names] if isinstance(names, str) else list(names)
    if not names or len(set(names)) != len(names) or any(n not in data for n in names):
        raise ValueError(f'{argument} must contain unique existing column names.')
    return names


def _pj_missing(value):
    return value is None or isinstance(value, Real) and not isinstance(value, Integral) and math.isnan(value)


def mzpjCombineColumns(dataset, columns, name, sep=' ', drop=False, missing='skip'):
    """Combine values as text in a new column, without overwriting an existing one."""
    data, document = _pj_frame(dataset)
    names = _pj_names(columns, data, 'columns')
    if not isinstance(name, str) or not name or name in data:
        raise ValueError('name must be a new non-empty column name.')
    if not isinstance(sep, str) or not isinstance(drop, bool) or missing not in ('skip', 'propagate'):
        raise ValueError("Use a text sep, Boolean drop and missing='skip' or 'propagate'.")
    combined = []
    for row in range(len(next(iter(data.values())))):
        values = [data[n][row] for n in names]
        present = [str(v) for v in values if not _pj_missing(v)]
        combined.append(None if not present or missing == 'propagate' and len(present) != len(values) else sep.join(present))
    out = {n: v for n, v in data.items() if not drop or n not in names}
    out[name] = combined
    return _pj_frame_result(out, document)


def mzpjSortRows(dataset, by, descending=False, missing='last'):
    """Stable row sort by one or more columns; returns a copy in the input representation."""
    data, document = _pj_frame(dataset)
    names = _pj_names(by, data, 'by')
    flags = [descending] * len(names) if isinstance(descending, bool) else list(descending)
    if len(flags) != len(names) or any(not isinstance(f, bool) for f in flags):
        raise ValueError('descending must be a Boolean or one Boolean per sort column.')
    if missing not in ('first', 'last'):
        raise ValueError("missing must be 'first' or 'last'.")
    def compare(a, b):
        for name, reverse in zip(names, flags):
            x, y = data[name][a], data[name][b]
            mx, my = _pj_missing(x), _pj_missing(y)
            if mx or my:
                if mx != my:
                    return (-1 if mx else 1) * (1 if missing == 'first' else -1)
                continue
            try:
                order = int(x > y) - int(x < y)
            except TypeError:
                raise TypeError(f"Column '{name}' contains values that cannot be ordered together.") from None
            if order:
                return -order if reverse else order
        return 0
    rows = sorted(range(len(next(iter(data.values())))), key=cmp_to_key(compare))
    return _pj_frame_result({n: [v[i] for i in rows] for n, v in data.items()}, document)


def mzpjOrderColumns(dataset, columns, keep_others=True):
    """Place columns first in the requested order; optionally keep remaining columns."""
    data, document = _pj_frame(dataset)
    names = _pj_names(columns, data, 'columns')
    if not isinstance(keep_others, bool):
        raise TypeError('keep_others must be True or False.')
    if keep_others:
        names += [n for n in data if n not in names]
    return _pj_frame_result({n: data[n] for n in names}, document)


def mzpjWideToLong(dataset, columns, id_columns=None, names_to='variable', values_to='value'):
    """Stack selected columns; keep identifiers. Output order is source row, then column."""
    data, document = _pj_frame(dataset)
    values = _pj_names(columns, data, 'columns')
    ids = [n for n in data if n not in values] if id_columns is None else _pj_names(id_columns, data, 'id_columns')
    if set(ids) & set(values) or not isinstance(names_to, str) or not isinstance(values_to, str) or not names_to or not values_to:
        raise ValueError('Identifier/value columns must be distinct and output names non-empty.')
    if names_to == values_to or names_to in ids or values_to in ids:
        raise ValueError('Long output column names collide with identifier columns.')
    out = {n: [] for n in ids + [names_to, values_to]}
    for row in range(len(next(iter(data.values())))):
        for name in values:
            for key in ids:
                out[key].append(data[key][row])
            out[names_to].append(name)
            out[values_to].append(data[name][row])
    # I metadati delle colonne impilate non sono trasferibili senza ambiguita'.
    old = {c['name']: c for c in (document or {}).get('columns', [])}
    meta = [old.get(n, {'name': n}) for n in ids] + [
        {'name': names_to, 'dataType': 'Text', 'measureType': 'Nominal'}, {'name': values_to}]
    return _pj_frame_result(out, document, meta)


def _pj_key(values):
    if any(_pj_missing(v) for v in values):
        raise ValueError('Key columns cannot contain missing values.')
    key = tuple(values)
    try:
        hash(key)
    except TypeError:
        raise TypeError('Key values must be scalar and hashable.') from None
    return key


def mzpjLongToWide(dataset, id_columns, names_from='variable', values_from='value', fill=None):
    """Pivot one value column; duplicate identifier/name combinations raise an error."""
    data, document = _pj_frame(dataset)
    ids = _pj_names(id_columns, data, 'id_columns')
    _pj_names([names_from, values_from], data, 'names_from/values_from')
    if names_from in ids or values_from in ids:
        raise ValueError('Identifier, name and value columns must be distinct.')
    groups, levels, known_levels = {}, [], set()
    for row in range(len(data[names_from])):
        key = _pj_key([data[n][row] for n in ids])
        name = data[names_from][row]
        if not isinstance(name, str) or not name or name in ids:
            raise ValueError('names_from must contain non-empty text names distinct from identifiers.')
        if name not in known_levels:
            levels.append(name)
            known_levels.add(name)
        group = groups.setdefault(key, {})
        if name in group:
            raise ValueError(f'Duplicate identifier/name combination: {key!r}, {name!r}. Aggregate explicitly first.')
        group[name] = data[values_from][row]
    if not levels:
        raise ValueError('Cannot infer wide columns from an empty names_from column.')
    out = {n: [] for n in ids + levels}
    for key, group in groups.items():
        for n, value in zip(ids, key):
            out[n].append(value)
        for n in levels:
            out[n].append(group.get(n, fill))
    old = {c['name']: c for c in (document or {}).get('columns', [])}
    return _pj_frame_result(out, document, [old.get(n, {'name': n}) for n in ids] + [{'name': n} for n in levels])


def mzpjMerge(dataset, other, on, how='left', suffixes=('_left', '_right'), validate='one_to_one', max_rows=1000000):
    """Join datasets on shared keys; explicit cardinality validation prevents accidental expansion."""
    left, document = _pj_frame(dataset)
    right, right_document = _pj_frame(other)
    keys = _pj_names(on, left, 'on')
    _pj_names(keys, right, 'on')
    if how not in ('left', 'right', 'inner', 'outer'):
        raise ValueError("how must be 'left', 'right', 'inner' or 'outer'.")
    if validate not in ('one_to_one', 'one_to_many', 'many_to_one', 'many_to_many'):
        raise ValueError('Specify the intended join cardinality with validate.')
    if isinstance(max_rows, bool) or not isinstance(max_rows, int) or max_rows < 1:
        raise ValueError('max_rows must be a positive integer.')
    if len(suffixes) != 2 or any(not isinstance(x, str) for x in suffixes):
        raise ValueError('suffixes must contain two strings.')
    lk = [_pj_key([left[n][i] for n in keys]) for i in range(len(next(iter(left.values()))))]
    rk = [_pj_key([right[n][i] for n in keys]) for i in range(len(next(iter(right.values()))))]
    if validate in ('one_to_one', 'one_to_many') and len(set(lk)) != len(lk):
        raise ValueError('Left keys are not unique for the requested validate rule.')
    if validate in ('one_to_one', 'many_to_one') and len(set(rk)) != len(rk):
        raise ValueError('Right keys are not unique for the requested validate rule.')
    overlap = (left.keys() & right.keys()) - set(keys)
    ln = {n: n + suffixes[0] if n in overlap else n for n in left}
    rn = {n: n + suffixes[1] if n in overlap else n for n in right if n not in keys}
    output_names = list(ln.values()) + list(rn.values())
    if len(set(output_names)) != len(output_names):
        raise ValueError('Join suffixes produce duplicate column names.')
    out = {n: [] for n in output_names}
    index = {}
    for j, key in enumerate(rk):
        index.setdefault(key, []).append(j)
    matched = set()
    count = 0
    def append(i, j):
        nonlocal count
        count += 1
        if count > max_rows:
            raise ValueError('Join exceeds max_rows; review keys/cardinality or increase the limit explicitly.')
        for n, target in ln.items():
            out[target].append(left[n][i] if i is not None else right[n][j] if n in keys else None)
        for n, target in rn.items():
            out[target].append(right[n][j] if j is not None else None)
    for i, key in enumerate(lk):
        matches = index.get(key, [])
        for j in matches:
            append(i, j)
            matched.add(j)
        if not matches and how in ('left', 'outer'):
            append(i, None)
    if how in ('right', 'outer'):
        for j in range(len(rk)):
            if j not in matched:
                append(None, j)
    metadata = []
    for original, names in ((document, ln), (right_document, rn)):
        old = {c['name']: c for c in (original or {}).get('columns', [])}
        for name, target in names.items():
            spec = copy.deepcopy(old.get(name, {}))
            spec['name'] = target
            metadata.append(spec)
    if document and document.get('weights') in ln:
        document['weights'] = ln[document['weights']]
    return _pj_frame_result(out, document, metadata)
