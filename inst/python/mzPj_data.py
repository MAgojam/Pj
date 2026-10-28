# Preparazione dati: nessuna mutazione implicita, nessuna formula nel motore server.
def _pj_data_vector(values, label):
    from collections.abc import Mapping
    if isinstance(values, (str, bytes, Mapping)):
        raise TypeError(f'{label} must be a one-dimensional sequence.')
    try:
        return list(values)
    except TypeError:
        raise TypeError(f'{label} must be a one-dimensional sequence.') from None


def _pj_data_scalar(value):
    import math
    from numbers import Real, Integral
    if value is None or isinstance(value, (str, bool)):
        return value
    if np is not None and isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, Real):
        value = float(value)
        if math.isnan(value):
            return None
        if math.isfinite(value):
            return value
    raise TypeError('Values must be strings, finite numbers, booleans or missing values.')


def _pj_data_numeric(values, label):
    from numbers import Real
    if np is None:
        raise ImportError('This data helper requires NumPy in the selected Python.')
    cleaned = []
    for value in _pj_data_vector(values, label):
        if value is None:
            cleaned.append(float('nan'))
        elif isinstance(value, Real) and not isinstance(value, (bool, np.bool_)):
            value = float(value)
            if np.isinf(value):
                raise ValueError(f'{label} contains an infinite value.')
            cleaned.append(value)
        else:
            raise TypeError(f'{label} must contain numeric values or missing values; booleans are not numeric inputs.')
    return np.asarray(cleaned, dtype=float)


def _pj_data_groups(length, by):
    if by is None:
        return [list(range(length))]
    groups = _pj_data_vector(by, 'by')
    if len(groups) != length:
        raise ValueError('by must have the same number of rows as values.')
    positions = {}
    for index, value in enumerate(groups):
        value = _pj_data_scalar(value)
        # Gruppo mancante: risultato mancante, non gruppo statistico aggiuntivo.
        if value is not None:
            positions.setdefault(value, []).append(index)
    return list(positions.values())


def _pj_recode(values, mapping, *, unmatched='keep'):
    from collections.abc import Mapping
    if not isinstance(mapping, Mapping):
        raise TypeError('mapping must be a dictionary of old values to new values.')
    if unmatched not in ('keep', 'missing', 'raise'):
        raise ValueError("unmatched must be 'keep', 'missing' or 'raise'.")
    rules = {_pj_data_scalar(key): _pj_data_scalar(value) for key, value in mapping.items()}
    result = []
    for value in _pj_data_vector(values, 'values'):
        value = _pj_data_scalar(value)
        if value in rules:
            result.append(rules[value])
        elif value is None or unmatched == 'missing':
            result.append(None)
        elif unmatched == 'raise':
            raise ValueError(f'No recoding rule for {value!r}.')
        else:
            result.append(value)
    return result


def _pj_row_statistic(dataset, columns, *, statistic='mean', reverse=None, bounds=None, min_valid=None, ddof=1, mad_scale=1):
    from collections.abc import Mapping
    from numbers import Integral
    if not isinstance(dataset, Mapping):
        raise TypeError('dataset must be a dictionary of columns, such as data.')
    columns = _pj_data_vector(columns, 'columns')
    if not columns or any(not isinstance(c, str) for c in columns) or len(set(columns)) != len(columns):
        raise ValueError('columns must contain distinct column names.')
    if any(c not in dataset for c in columns):
        raise ValueError('Some score columns are missing from data.')
    method = statistic
    if method not in ('mean', 'sum', 'sd', 'var', 'median', 'mad', 'min', 'max', 'range', 'n'):
        raise ValueError('statistic must be mean, sum, sd, var, median, mad, min, max, range or n.')
    if isinstance(ddof, bool) or not isinstance(ddof, Integral) or ddof < 0:
        raise ValueError('ddof must be a non-negative integer.')
    minimum = len(columns) if min_valid is None else min_valid
    if isinstance(minimum, bool) or not isinstance(minimum, Integral) or not 1 <= minimum <= len(columns):
        raise ValueError('min_valid must be between 1 and the number of score columns.')
    reverse = [] if reverse is None else _pj_data_vector(reverse, 'reverse')
    if any(c not in columns for c in reverse) or len(set(reverse)) != len(reverse):
        raise ValueError('reverse must contain distinct names from columns.')
    if reverse and bounds is None:
        raise ValueError('bounds=(minimum, maximum) is required for reverse scoring.')
    limits = None
    if bounds is not None:
        limits = _pj_data_numeric(bounds, 'bounds')
        if len(limits) != 2 or not np.isfinite(limits).all() or limits[0] >= limits[1]:
            raise ValueError('bounds must contain two finite values with minimum < maximum.')
    arrays = [_pj_data_numeric(dataset[c], c) for c in columns]
    if any(len(a) != len(arrays[0]) for a in arrays):
        raise ValueError('Score columns must have the same number of rows.')
    for column, array in zip(columns, arrays):
        if limits is not None and ((array < limits[0]) | (array > limits[1])).any():
            raise ValueError(f'{column} contains values outside bounds.')
        if column in reverse:
            array[:] = limits.sum() - array
    matrix = np.column_stack(arrays)
    counts = np.sum(~np.isnan(matrix), axis=1)
    if method == 'n':
        return [int(count) for count in counts]
    scores = np.nansum(matrix, axis=1)
    if method == 'mean':
        scores = np.divide(scores, counts, out=np.full(len(scores), np.nan), where=counts > 0)
    elif method in ('median', 'sd', 'var', 'mad', 'min', 'max', 'range'):
        eligible = counts > (ddof if method in ('sd', 'var') else 0)
        scores = np.full(len(counts), np.nan)
        if method == 'mad':
            from numbers import Real
            if stats is None:
                raise ImportError('The MAD statistic requires SciPy in the selected Python.')
            if mad_scale != 'normal' and (isinstance(mad_scale, bool) or not isinstance(mad_scale, Real)
                                         or not np.isfinite(mad_scale) or mad_scale <= 0):
                raise ValueError("mad_scale must be 'normal' or a positive finite numeric divisor; use 1 for raw MAD.")
        if eligible.any():
            selected = matrix[eligible]
            if method == 'sd': scores[eligible] = np.nanstd(selected, axis=1, ddof=ddof)
            elif method == 'var': scores[eligible] = np.nanvar(selected, axis=1, ddof=ddof)
            elif method == 'median': scores[eligible] = np.nanmedian(selected, axis=1)
            elif method == 'mad': scores[eligible] = stats.median_abs_deviation(selected, axis=1, scale=mad_scale, nan_policy='omit')
            elif method == 'min': scores[eligible] = np.nanmin(selected, axis=1)
            elif method == 'max': scores[eligible] = np.nanmax(selected, axis=1)
            else: scores[eligible] = np.nanmax(selected, axis=1) - np.nanmin(selected, axis=1)
    if np.isinf(scores[counts >= minimum]).any():
        raise ValueError('Score computation produced an infinite value.')
    return [float(score) if count >= minimum and not np.isnan(score) else None for score, count in zip(scores, counts)]


def _pj_standardize(values, *, by=None, ddof=1, center=True, scale=True, on_constant='missing'):
    from numbers import Integral
    if isinstance(ddof, bool) or not isinstance(ddof, Integral) or ddof < 0:
        raise ValueError('ddof must be a non-negative integer.')
    if not isinstance(center, bool) or not isinstance(scale, bool):
        raise TypeError('center and scale must be True or False.')
    if on_constant not in ('missing', 'raise'):
        raise ValueError("on_constant must be 'missing' or 'raise'.")
    array = _pj_data_numeric(values, 'values')
    result = [None] * len(array)
    for group in _pj_data_groups(len(array), by):
        indices = [i for i in group if not np.isnan(array[i])]
        if not indices:
            continue
        selected = array[indices]
        denominator = 1.0
        if scale:
            denominator = float(np.std(selected, ddof=ddof)) if len(indices) > ddof else 0.0
            if denominator == 0 or not np.isfinite(denominator):
                if on_constant == 'raise':
                    raise ValueError('Standardization requires enough observations and a positive finite standard deviation in each group.')
                continue
        transformed = (selected - np.mean(selected) if center else selected) / denominator
        for index, value in zip(indices, transformed):
            if not np.isfinite(value):
                raise ValueError('Standardization produced a non-finite value.')
            result[index] = float(value)
    return result


def _pj_rank(values, *, by=None, method='average', descending=False):
    if stats is None:
        raise ImportError('mzpjRank requires SciPy in the selected Python.')
    if method not in ('average', 'min', 'max', 'dense', 'ordinal'):
        raise ValueError('method must be average, min, max, dense or ordinal.')
    if not isinstance(descending, bool):
        raise TypeError('descending must be True or False.')
    array = _pj_data_numeric(values, 'values')
    result = [None] * len(array)
    for group in _pj_data_groups(len(array), by):
        indices = [i for i in group if not np.isnan(array[i])]
        selected = array[indices]
        ranks = stats.rankdata(-selected if descending else selected, method=method)
        for index, rank in zip(indices, ranks):
            result[index] = float(rank)
    return result
