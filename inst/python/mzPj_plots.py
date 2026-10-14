# Collegamento Python ai renderer D3: dati validati e HTML autonomo, senza dipendenze scientifiche.
def _pj_plot_columns(dataset, names, function):
    from collections.abc import Mapping
    if not isinstance(dataset, Mapping):
        raise TypeError(f'{function}(): expected a dictionary of column arrays, such as data.')
    names = [name for name in names if name is not None]
    if any(not isinstance(name, str) or not name for name in names):
        raise TypeError(f'{function}(): column names must be non-empty strings.')
    names = list(dict.fromkeys(names))
    for name in names:
        if not isinstance(name, str) or not name:
            raise TypeError(f'{function}(): column names must be non-empty strings.')
        if name not in dataset:
            raise ValueError(f'{function}(): column {name!r} is unavailable. Select it in Pjp or include it in Pj data.')
        values = dataset[name]
        if isinstance(values, (str, bytes)) or not hasattr(values, '__len__') or not hasattr(values, '__getitem__'):
            raise TypeError(f'{function}(): {name!r} must contain a column array.')
    sizes = {len(dataset[name]) for name in names}
    if len(sizes) != 1:
        raise ValueError(f'{function}(): requested columns must have the same number of rows.')
    return sizes.pop()


def _pj_plot_number(value, column, row, function):
    from numbers import Real
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f'{function}(): row {row + 1}, {column!r} must be numeric or missing; text and booleans are not numeric observations.')
    try:
        value = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(f'{function}(): row {row + 1}, {column!r} is outside the supported numeric range.') from error
    return value if math.isfinite(value) else None


def _pj_plot_domain(values, function):
    low, high = min(values), max(values)
    # Margini finiti anche per colonne costanti; evita domini infiniti in JavaScript.
    padding = max(1, abs(low) * .05) if low == high else (high - low) * .05
    if not all(math.isfinite(v) for v in (high - low, low - padding, high + padding)):
        raise ValueError(f'{function}(): numeric values are too extreme for a finite plotting domain.')
    return low, high


def _pj_plot_html(payload, name, width, height, accordion, expanded, color):
    import re
    import uuid
    if not isinstance(accordion, bool) or not isinstance(expanded, bool):
        raise TypeError('Plot options accordion and expanded must be True or False.')
    if not accordion and not expanded:
        raise ValueError('expanded=False requires accordion=True.')
    if not isinstance(color, str) or re.fullmatch(r'#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})', color) is None:
        raise ValueError('Plot color must be a hexadecimal CSS color, such as #3e6da9.')
    from numbers import Integral
    dimensions = []
    for parameter, value, fallback, minimum in (
            ('width', width, _pj_figure_dimension(FIGWIDTH, 800), 320),
            ('height', height, _pj_figure_dimension(FIGHEIGHT, 500), 240)):
        if value is None:
            value = max(minimum, fallback)
        if isinstance(value, bool) or not isinstance(value, Integral) or not minimum <= value <= 10000:
            raise ValueError(f'Plot {parameter} must be an integer between {minimum} and 10000 pixels.')
        dimensions.append(int(value))
    if not D3_INLINE or not _pj_plot_js or not _pj_plot_css:
        raise RuntimeError('The Pj D3 plot resources are unavailable. Reinstall the updated Pj module.')
    payload.update(width=dimensions[0], height=dimensions[1], accordion=accordion,
                   expanded=expanded, color=color)
    encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False)
    # I dati non devono chiudere il blocco script, neppure quando contengono etichette ostili.
    for character, escaped in (('&', '\\u0026'), ('<', '\\u003c'), ('>', '\\u003e'),
                               ('\u2028', '\\u2028'), ('\u2029', '\\u2029')):
        encoded = encoded.replace(character, escaped)
    root_id = 'mzpj_chart_' + uuid.uuid4().hex
    content = ('<style>' + _pj_plot_css + '</style><div id="' + root_id + '"></div>'
               '<script>' + D3_INLINE + '</script><script>' + _pj_plot_js + '</script>'
               '<script>(function(){const p=' + encoded + ';window.mzPjD3[p.kind]('
               'document.getElementById("' + root_id + '"),p);})();</script>')
    _pj_add_html(content, name=name, title='')


def _pj_show_scatter(dataset, x, y, group=None, labels=None, name=None, title=None,
                     x_label=None, y_label=None, color='#3e6da9', width=None,
                     height=None, accordion=True, expanded=True):
    """Costruisce punti e gruppi senza stime inferenziali o trasformazioni implicite."""
    function = 'mzpjShowScatter'
    if not all(isinstance(value, str) and value for value in (x, y)):
        raise TypeError(f'{function}(): x and y must be non-empty column names.')
    count = _pj_plot_columns(dataset, [x, y, group, labels], function)
    points = []
    for row in range(count):
        xv = _pj_plot_number(dataset[x][row], x, row, function)
        yv = _pj_plot_number(dataset[y][row], y, row, function)
        label = dataset[labels][row] if labels is not None else None
        if isinstance(label, float) and not math.isfinite(label):
            label = None
        category = dataset[group][row] if group is not None else ''
        if xv is None or yv is None or category is None or (isinstance(category, float) and math.isnan(category)):
            continue
        points.append(dict(x=xv, y=yv, label=str(label) if label is not None else f'Row {row + 1}', group=str(category)))
    if not points:
        raise ValueError(f'{function}(): no complete finite observations are available for the requested columns.')
    _pj_plot_domain([point['x'] for point in points], function)
    _pj_plot_domain([point['y'] for point in points], function)
    payload = dict(kind='scatter', points=points, grouped=group is not None,
                   groups=sorted({point['group'] for point in points}, key=str.casefold),
                   title=str(title) if title is not None else f'{y} versus {x}',
                   xLabel=str(x_label) if x_label is not None else x,
                   yLabel=str(y_label) if y_label is not None else y,
                   note=f'N = {len(points)}; {count - len(points)} rows excluded for missing or non-finite coordinates or missing groups. Group visibility does not change the axes. Plot-size zoom preserves the data scales.')
    _pj_plot_html(payload, name, width, height, accordion, expanded, color)


def _pj_plot_category(value):
    # Mantiene separate categorie con tipi diversi, evitando collisioni fra 1 e '1'.
    from numbers import Real, Integral
    if value is None:
        return None
    if isinstance(value, bool):
        return ('bool', str(value))
    if isinstance(value, Integral):
        return ('int', str(value))
    if isinstance(value, Real):
        return ('float', str(value)) if math.isfinite(float(value)) else None
    if isinstance(value, str):
        return ('str', value)
    raise TypeError('Plot categories and labels must be scalar text, numbers or booleans.')


def _pj_plot_categories(keys):
    ordered = sorted(set(keys), key=lambda key: (key[1].casefold(), key[0]))
    counts = {}
    for _, label in ordered:
        counts[label] = counts.get(label, 0) + 1
    result, used = {}, set()
    for key in ordered:
        base = key[1] if counts[key[1]] == 1 else f'{key[1]} ({key[0]})'
        label, suffix = base, 2
        while label in used:
            label = f'{base} [{suffix}]'
            suffix += 1
        result[key] = label
        used.add(label)
    return result


def _pj_plot_quantile(values, probability):
    position = (len(values) - 1) * probability
    low = int(math.floor(position))
    high = min(len(values) - 1, low + 1)
    return values[low] + (values[high] - values[low]) * (position - low)


def _pj_show_boxplot(dataset, variable, group=None, labels=None, show_points=False,
                     name=None, title=None, x_label=None, y_label=None,
                     color='#3e6da9', width=None, height=None, accordion=True, expanded=True):
    """Quartili interpolati linearmente e baffi entro 1.5 IQR, senza test inferenziali."""
    function = 'mzpjShowBoxPlot'
    if not isinstance(variable, str) or not variable:
        raise TypeError(f'{function}(): variable must be a non-empty column name.')
    if not isinstance(show_points, bool):
        raise TypeError(f'{function}(): show_points must be True or False.')
    count = _pj_plot_columns(dataset, [variable, group, labels], function)
    rows = []
    for row in range(count):
        value = _pj_plot_number(dataset[variable][row], variable, row, function)
        key = _pj_plot_category(dataset[group][row]) if group is not None else ('str', variable)
        if value is None or key is None:
            continue
        label = dataset[labels][row] if labels is not None else None
        rows.append((key, value, row, str(label) if _pj_plot_category(label) is not None else f'Row {row + 1}'))
    if not rows:
        raise ValueError(f'{function}(): no complete finite observations are available.')
    _pj_plot_domain([row[1] for row in rows], function)
    categories = _pj_plot_categories([row[0] for row in rows])
    members_by_key = {}
    for row in rows:
        members_by_key.setdefault(row[0], []).append(row)
    boxes, points = [], []
    for key, category in categories.items():
        members = members_by_key[key]
        values = sorted(row[1] for row in members)
        q1, median, q3 = [_pj_plot_quantile(values, p) for p in (.25, .5, .75)]
        spread = q3 - q1
        inside = [value for value in values if q1 - 1.5 * spread <= value <= q3 + 1.5 * spread]
        # Nei campioni piccoli un quartile interpolato puo' superare gli estremi non anomali.
        lower, upper = min(q1, min(inside)), max(q3, max(inside))
        boxes.append(dict(kind='summary', group=category, n=len(values), q1=q1,
                          median=median, q3=q3, lower=lower, upper=upper))
        for _, value, row, label in members:
            outlier = value < lower or value > upper
            if show_points or outlier:
                points.append(dict(kind='observation', group=category, value=value,
                                   row=row, label=label, outlier=outlier))
    payload = dict(kind='boxplot', boxes=boxes, points=points, grouped=group is not None,
                   showPoints=show_points, groups=list(categories.values()),
                   title=str(title) if title is not None else f'Distribution of {variable}',
                   xLabel=str(x_label) if x_label is not None else (group or variable),
                   yLabel=str(y_label) if y_label is not None else variable,
                   note=f'N = {len(rows)}; {count - len(rows)} rows excluded. Quartiles use linear interpolation at (N - 1) p. Whiskers extend to observed values within 1.5 IQR, or stop at the quartile if no such value lies beyond it. Potential outliers are displayed, not excluded. Horizontal jitter only separates overlapping points.')
    _pj_plot_html(payload, name, width, height, accordion, expanded, color)


def _pj_show_bar(dataset, category, value=None, stat='count', orientation='vertical',
                 name=None, title=None, x_label=None, y_label=None,
                 color='#3e6da9', width=None, height=None, accordion=True, expanded=True):
    """Aggregazione esplicita: frequenze, somma, media o valori gia' riepilogati."""
    function = 'mzpjShowBar'
    if not isinstance(category, str) or not category:
        raise TypeError(f'{function}(): category must be a non-empty column name.')
    if stat not in ('count', 'sum', 'mean', 'identity'):
        raise ValueError(f"{function}(): stat must be 'count', 'sum', 'mean' or 'identity'.")
    if orientation not in ('vertical', 'horizontal'):
        raise ValueError(f"{function}(): orientation must be 'vertical' or 'horizontal'.")
    if (stat == 'count' and value is not None) or (stat != 'count' and (not isinstance(value, str) or not value)):
        raise ValueError(f'{function}(): count requires value=None; other statistics require a numeric value column.')
    count = _pj_plot_columns(dataset, [category, value], function)
    rows = []
    for row in range(count):
        key = _pj_plot_category(dataset[category][row])
        number = _pj_plot_number(dataset[value][row], value, row, function) if value is not None else 1
        if key is not None and number is not None:
            rows.append((key, number))
    if not rows:
        raise ValueError(f'{function}(): no complete observations are available.')
    categories = _pj_plot_categories([row[0] for row in rows])
    values_by_key = {}
    for key, number in rows:
        values_by_key.setdefault(key, []).append(number)
    bars = []
    for key, label in categories.items():
        values = values_by_key[key]
        if stat == 'identity' and len(values) != 1:
            raise ValueError(f'{function}(): identity requires one value per category; {label!r} occurs more than once.')
        try:
            number = (len(values) if stat == 'count' else values[0] if stat == 'identity'
                      else math.fsum(number / len(values) for number in values) if stat == 'mean'
                      else math.fsum(values))
        except OverflowError as error:
            raise ValueError(f'{function}(): aggregated values are outside the supported numeric range.') from error
        bars.append(dict(category=label, value=number, n=len(values)))
    _pj_plot_domain([0] + [bar['value'] for bar in bars], function)
    measure = 'Frequency' if stat == 'count' else f'{stat.capitalize()} of {value}' if stat != 'identity' else value
    xlabel, ylabel = (category, measure) if orientation == 'vertical' else (measure, category)
    payload = dict(kind='bar', bars=bars, stat=stat, orientation=orientation,
                   title=str(title) if title is not None else f'{measure} by {category}',
                   xLabel=str(x_label) if x_label is not None else xlabel,
                   yLabel=str(y_label) if y_label is not None else ylabel,
                   note=f'N = {len(rows)}; {count - len(rows)} rows excluded. Statistic: {stat}. Categories are sorted by label; the numeric axis includes zero. No uncertainty interval is calculated.')
    _pj_plot_html(payload, name, width, height, accordion, expanded, color)


def _pj_show_line(dataset, x, y, group=None, labels=None, sort_x=False, connect_gaps=False,
                  show_points=True, name=None, title=None, x_label=None, y_label=None,
                  color='#3e6da9', width=None, height=None, accordion=True, expanded=True):
    """Collega le osservazioni nel loro ordine; i mancanti interrompono la linea per default."""
    function = 'mzpjShowLine'
    if not all(isinstance(value, str) and value for value in (x, y)):
        raise TypeError(f'{function}(): x and y must be non-empty column names.')
    if any(not isinstance(value, bool) for value in (sort_x, connect_gaps, show_points)):
        raise TypeError(f'{function}(): sort_x, connect_gaps and show_points must be True or False.')
    count = _pj_plot_columns(dataset, [x, y, group, labels], function)
    rows = []
    for row in range(count):
        key = _pj_plot_category(dataset[group][row]) if group is not None else ('str', '')
        xv = _pj_plot_number(dataset[x][row], x, row, function)
        yv = _pj_plot_number(dataset[y][row], y, row, function)
        if key is None:
            continue
        if sort_x and xv is None:
            raise ValueError(f'{function}(): sort_x=True requires finite x for every included group row; use sort_x=False to preserve gaps with missing x.')
        label = dataset[labels][row] if labels is not None else None
        rows.append((key, dict(x=xv, y=yv, label=str(label) if _pj_plot_category(label) is not None else f'Row {row + 1}')))
    complete = [point for _, point in rows if point['x'] is not None and point['y'] is not None]
    if not complete:
        raise ValueError(f'{function}(): no complete finite observations are available.')
    _pj_plot_domain([point['x'] for point in complete], function)
    _pj_plot_domain([point['y'] for point in complete], function)
    categories = _pj_plot_categories([key for key, point in rows if point['x'] is not None and point['y'] is not None])
    points_by_key = {}
    for key, point in rows:
        points_by_key.setdefault(key, []).append(point)
    series = []
    for key, label in categories.items():
        points = points_by_key[key]
        if sort_x:
            points.sort(key=lambda point: point['x'])
        if connect_gaps:
            points = [point for point in points if point['x'] is not None and point['y'] is not None]
        series.append(dict(group=label, points=points))
    payload = dict(kind='line', series=series, groups=list(categories.values()),
                   grouped=group is not None, showPoints=show_points,
                   title=str(title) if title is not None else f'{y} across {x}',
                   xLabel=str(x_label) if x_label is not None else x,
                   yLabel=str(y_label) if y_label is not None else y,
                   note=f'N = {len(complete)}; {count - len(complete)} incomplete rows excluded from marks. ' +
                   ('Rows sorted by x within each series. ' if sort_x else 'Lines follow dataset order within each series. ') +
                   ('Gaps are connected explicitly. ' if connect_gaps else 'Missing coordinates break the line. ') +
                   'No interpolation, smoothing or statistical model is fitted.')
    _pj_plot_html(payload, name, width, height, accordion, expanded, color)


def _pj_show_intervals(dataset, estimate, lower, upper, labels=None, reference=None,
                       interval_label='Interval', name=None, title=None, x_label=None,
                       y_label=None, color='#3e6da9', width=None, height=None,
                       accordion=True, expanded=True):
    """Mostra stime e limiti forniti dallo script, senza attribuire loro un livello di confidenza."""
    function = 'mzpjShowIntervals'
    if not all(isinstance(value, str) and value for value in (estimate, lower, upper)):
        raise TypeError(f'{function}(): estimate, lower and upper must be non-empty column names.')
    count = _pj_plot_columns(dataset, [estimate, lower, upper, labels], function)
    if reference is not None:
        reference = _pj_plot_number(reference, 'reference', 0, function)
        if reference is None:
            raise ValueError(f'{function}(): reference must be a finite number or None.')
    intervals = []
    for row in range(count):
        center, lo, hi = [_pj_plot_number(dataset[column][row], column, row, function) for column in (estimate, lower, upper)]
        if any(value is None for value in (center, lo, hi)):
            continue
        if lo > hi:
            raise ValueError(f'{function}(): row {row + 1} has lower > upper.')
        label = dataset[labels][row] if labels is not None else None
        intervals.append(dict(estimate=center, lower=lo, upper=hi,
                              label=str(label) if _pj_plot_category(label) is not None else f'Row {row + 1}'))
    if not intervals:
        raise ValueError(f'{function}(): no complete finite estimates and intervals are available.')
    values = [value for item in intervals for value in (item['estimate'], item['lower'], item['upper'])]
    _pj_plot_domain(values + ([reference] if reference is not None else []), function)
    payload = dict(kind='intervals', intervals=intervals, reference=reference, intervalLabel=str(interval_label),
                   title=str(title) if title is not None else 'Estimates and supplied intervals',
                   xLabel=str(x_label) if x_label is not None else estimate,
                   yLabel=str(y_label) if y_label is not None else '',
                   note=f'N = {len(intervals)}; {count - len(intervals)} incomplete rows excluded. Estimates and interval bounds are supplied by the script; no confidence level or statistical model is inferred. Original row order is preserved.')
    _pj_plot_html(payload, name, width, height, accordion, expanded, color)


def _pj_show_histogram(dataset, variable, bins=10, density=False, name=None, title=None,
                       x_label=None, y_label=None, color='#3e6da9', width=None,
                       height=None, accordion=True, expanded=True):
    """Calcola intervalli di uguale ampiezza: l'ultimo include il massimo."""
    from numbers import Integral
    function = 'mzpjShowHistogram'
    if not isinstance(variable, str) or not variable:
        raise TypeError(f'{function}(): variable must be a non-empty column name.')
    if isinstance(bins, bool) or not isinstance(bins, Integral) or not 1 <= bins <= 200:
        raise ValueError(f'{function}(): bins must be an integer between 1 and 200.')
    if not isinstance(density, bool):
        raise TypeError(f'{function}(): density must be True or False.')
    count = _pj_plot_columns(dataset, [variable], function)
    values = [_pj_plot_number(value, variable, row, function) for row, value in enumerate(dataset[variable])]
    values = [value for value in values if value is not None]
    if not values:
        raise ValueError(f'{function}(): no finite numeric observations are available.')
    low, high = _pj_plot_domain(values, function)
    if low == high:
        padding = max(.5, abs(low) * .05)
        low, high = low - padding, high + padding
    step = (high - low) / int(bins)
    if step <= 0 or not math.isfinite(step):
        raise ValueError(f'{function}(): the requested bin width is outside the supported numeric range.')
    edges = [low + (high - low) * (i / int(bins)) for i in range(int(bins))] + [high]
    if any(b <= a for a, b in zip(edges, edges[1:])):
        raise ValueError(f'{function}(): reduce bins; distinct interval boundaries cannot be represented at this scale.')
    from bisect import bisect_right
    counts = [0] * int(bins)
    for value in values:
        index = min(int(bins) - 1, max(0, bisect_right(edges, value) - 1))
        counts[index] += 1
    bars = []
    for i, n in enumerate(counts):
        value = n / len(values) / (edges[i + 1] - edges[i]) if density else n
        if not math.isfinite(value):
            raise ValueError(f'{function}(): density is outside the supported numeric range.')
        bars.append(dict(lower=edges[i], upper=edges[i + 1], count=n, value=value, last=i == int(bins) - 1))
    payload = dict(kind='histogram', bars=bars, density=density,
                   title=str(title) if title is not None else f'Distribution of {variable}',
                   xLabel=str(x_label) if x_label is not None else variable,
                   yLabel=str(y_label) if y_label is not None else ('Density' if density else 'Frequency'),
                   note=f'N = {len(values)}; {count - len(values)} missing or non-finite values excluded. {int(bins)} equal-width bins; intervals are left-closed and right-open, except the last includes the maximum. Plot-size zoom preserves the data scales.')
    _pj_plot_html(payload, name, width, height, accordion, expanded, color)


def _pj_show_distribution(mean=0, sd=1, n=30, mode='sample_mean', interactive=True,
                          name=None, title=None, x_label=None, y_label=None,
                          color='#3e6da9', width=None, height=None, accordion=True, expanded=True):
    """Modello didattico normale esplicito: la dispersione della media e' sigma / sqrt(N)."""
    from numbers import Integral
    function = 'mzpjShowDistribution'
    mean = _pj_plot_number(mean, 'mean', 0, function)
    sd = _pj_plot_number(sd, 'sd', 0, function)
    if mean is None or sd is None or sd <= 0:
        raise ValueError(f'{function}(): mean must be finite and sd must be finite and positive.')
    if isinstance(n, bool) or not isinstance(n, Integral) or not 1 <= n <= 10000:
        raise ValueError(f'{function}(): n must be an integer between 1 and 10000.')
    if mode not in ('population', 'sample_mean'):
        raise ValueError(f"{function}(): mode must be 'population' or 'sample_mean'.")
    if not isinstance(interactive, bool):
        raise TypeError(f'{function}(): interactive must be True or False.')
    maximum_n = max(500, int(n))
    narrowest_sd = .5 * sd / math.sqrt(maximum_n)
    if (narrowest_sd <= 0 or not math.isfinite(1 / narrowest_sd) or
            not math.isfinite(mean - 7 * sd) or not math.isfinite(mean + 7 * sd) or
            mean - narrowest_sd == mean + narrowest_sd):
        raise ValueError(f'{function}(): parameters cannot be represented reliably at this numeric scale.')
    payload = dict(kind='distribution', mean=mean, sd=sd, n=int(n), maxN=maximum_n,
                   mode=mode, interactive=interactive,
                   title=str(title) if title is not None else ('Normal population' if mode == 'population' else 'Sampling distribution of the mean'),
                   xLabel=str(x_label) if x_label is not None else ('Observation' if mode == 'population' else 'Observation / sample mean'),
                   yLabel=str(y_label) if y_label is not None else 'Probability density',
                   note='Teaching model: independent observations from a normal population with known mean and population SD. The sample mean is exactly normal with SE = SD / sqrt(N); no sample is generated and no test is fitted. Changing N does not change the population distribution. The x-axis is fixed while density height rescales; native tables outside this graphic do not update when its controls move.')
    _pj_plot_html(payload, name, width, height, accordion, expanded, color)


def _pj_plot_ranks(values):
    # Ranghi medi per i pareggi, calcolati soltanto sulle coppie complete.
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = (start + 1 + end) / 2
        for index in order[start:end]:
            ranks[index] = rank
        start = end
    return ranks


def _pj_plot_correlation(x, y):
    # Scala prima di centrare, evitando overflow nei prodotti e nelle somme.
    if len(x) < 3:
        return None
    sx, sy = max(map(abs, x)), max(map(abs, y))
    if sx == 0 or sy == 0:
        return None
    xx, yy = [v / sx for v in x], [v / sy for v in y]
    mx, my = math.fsum(xx) / len(xx), math.fsum(yy) / len(yy)
    dx, dy = [v - mx for v in xx], [v - my for v in yy]
    vx, vy = math.fsum(v*v for v in dx), math.fsum(v*v for v in dy)
    if vx == 0 or vy == 0:
        return None
    return max(-1.0, min(1.0, math.fsum(a*b for a,b in zip(dx,dy)) / math.sqrt(vx) / math.sqrt(vy)))


def _pj_show_correlation(dataset, columns, labels=None, missing='pairwise', method='pearson',
                         name=None, title=None, color='#3e6da9', width=None, height=None,
                         accordion=True, expanded=True):
    """Matrice e scatter collegati; nessuna inferenza o selezione modifica i dati originali."""
    function = 'mzpjShowCorrelation'
    if not isinstance(columns, (list, tuple)) or not 2 <= len(columns) <= 12:
        raise ValueError(f'{function}(): columns must list 2 to 12 distinct numeric column names.')
    if any(not isinstance(column, str) or not column for column in columns) or len(set(columns)) != len(columns):
        raise ValueError(f'{function}(): columns must contain distinct non-empty names.')
    if missing not in ('pairwise', 'complete') or method not in ('pearson', 'spearman'):
        raise ValueError(f'{function}(): missing must be pairwise/complete and method pearson/spearman.')
    count = _pj_plot_columns(dataset, list(columns) + [labels], function)
    if count > 10000:
        raise ValueError(f'{function}(): this interactive explorer supports at most 10000 rows; pass an explicit subset.')
    rows = []
    for index in range(count):
        values = [_pj_plot_number(dataset[column][index], column, index, function) for column in columns]
        if missing == 'complete' and any(v is None for v in values):
            continue
        label = dataset[labels][index] if labels is not None else None
        rows.append(dict(id=index, values=values, label=str(label) if _pj_plot_category(label) is not None else f'Row {index + 1}'))
    cells = []
    for i in range(len(columns)):
        for j in range(i, len(columns)):
            pairs = [(row['values'][i], row['values'][j]) for row in rows
                     if row['values'][i] is not None and row['values'][j] is not None]
            x, y = map(list, zip(*pairs)) if pairs else ([], [])
            if pairs:
                _pj_plot_domain(x, function); _pj_plot_domain(y, function)
            cell = dict(i=i, j=j, n=len(pairs), pearson=_pj_plot_correlation(x,y),
                        spearman=_pj_plot_correlation(_pj_plot_ranks(x),_pj_plot_ranks(y)))
            cells.append(cell)
            if i != j:
                cells.append(dict(cell, i=j, j=i))
    if not any(cell['pearson'] is not None and cell['i'] != cell['j'] for cell in cells):
        raise ValueError(f'{function}(): at least one nonconstant pair with three complete observations is required.')
    payload = dict(kind='correlation', columns=list(columns), rows=rows, cells=cells,
                   method=method, missing=missing, title=str(title) if title is not None else 'Correlation explorer',
                   note=f'Missing-data rule: {missing}. Coefficients require at least 3 complete observations and nonzero variation. Spearman uses average ranks for ties. Scatter coordinates remain in original units. Brushing highlights rows only: it does not recompute coefficients, infer significance or change the dataset. Pairwise matrices need not be positive semidefinite.')
    _pj_plot_html(payload, name, width, height, accordion, expanded, color)


def _pj_show_paired(dataset, first, second, group=None, labels=None, name=None, title=None,
                    first_label=None, second_label=None, y_label=None, color='#3e6da9',
                    width=None, height=None, accordion=True, expanded=True):
    """Profili individuali e differenze collegati con selezione e riepiloghi descrittivi."""
    function = 'mzpjShowPaired'
    if not all(isinstance(column,str) and column for column in (first,second)):
        raise TypeError(f'{function}(): first and second must be non-empty column names.')
    if str(first if first_label is None else first_label) == str(second if second_label is None else second_label):
        raise ValueError(f'{function}(): first_label and second_label must be different.')
    count = _pj_plot_columns(dataset, [first, second, group, labels], function)
    if first == second:
        raise ValueError(f'{function}(): first and second must be different columns.')
    if count > 10000:
        raise ValueError(f'{function}(): this interactive explorer supports at most 10000 rows; pass an explicit subset.')
    rows = []
    for index in range(count):
        a = _pj_plot_number(dataset[first][index], first, index, function)
        b = _pj_plot_number(dataset[second][index], second, index, function)
        category = _pj_plot_category(dataset[group][index]) if group is not None else ('str','All observations')
        if a is None or b is None or category is None:
            continue
        if not math.isfinite(b-a):
            raise ValueError(f'{function}(): row {index + 1} has a difference outside the numeric range.')
        label = dataset[labels][index] if labels is not None else None
        rows.append(dict(id=index, first=a, second=b, change=b-a, category=category,
                         label=str(label) if _pj_plot_category(label) is not None else f'Row {index + 1}'))
    if not rows:
        raise ValueError(f'{function}(): no complete finite pairs with available groups.')
    categories = _pj_plot_categories([row['category'] for row in rows])
    for row in rows:
        row['group'] = categories[row.pop('category')]
    _pj_plot_domain([v for row in rows for v in (row['first'],row['second'])], function)
    _pj_plot_domain([row['change'] for row in rows], function)
    payload = dict(kind='paired', rows=rows, groups=list(categories.values()), grouped=group is not None,
                   firstLabel=str(first_label) if first_label is not None else first,
                   secondLabel=str(second_label) if second_label is not None else second,
                   yLabel=str(y_label) if y_label is not None else 'Observed value',
                   title=str(title) if title is not None else f'{second} minus {first}: paired explorer',
                   note=f'{len(rows)} complete pairs; {count-len(rows)} rows excluded. Pairs are matched by dataset row. Measurements must have comparable units. Drag a rectangle over the change points or click a subject to highlight its profile. Filters and selections update descriptive summaries only; no test or confidence interval is calculated. Axes remain fixed across filters.')
    _pj_plot_html(payload, name, width, height, accordion, expanded, color)


def _pj_show_test_distribution(distribution='t', df=10, df2=20, statistic=2, tail='right',
                               alpha=.05, name=None, title=None, color='#3e6da9',
                               width=None, height=None, accordion=True, expanded=True):
    """Modello teorico con aree di coda: non stima una statistica a partire dai dati."""
    from numbers import Integral
    function = 'mzpjShowTestDistribution'
    if distribution not in ('t','chi2','f'):
        raise ValueError(f'{function}(): distribution must be t, chi2 or f.')
    for parameter, value in (('df',df),('df2',df2)):
        if isinstance(value,bool) or not isinstance(value,Integral) or not 1 <= value <= 120:
            raise ValueError(f'{function}(): {parameter} must be an integer between 1 and 120.')
    statistic = _pj_plot_number(statistic,'statistic',0,function)
    alpha = _pj_plot_number(alpha,'alpha',0,function)
    if statistic is None or not (-10 <= statistic <= 10 if distribution == 't' else 0 <= statistic <= 400):
        raise ValueError(f'{function}(): statistic must be finite, in [-10,10] for t or [0,400] otherwise.')
    if alpha is None or not .001 <= alpha <= .2:
        raise ValueError(f'{function}(): alpha must be between .001 and .2.')
    if tail not in ('left','right','two-sided') or (tail == 'two-sided' and distribution != 't'):
        raise ValueError(f'{function}(): use left/right tails; two-sided is available only for t.')
    payload = dict(kind='testDistribution', distribution=distribution, df=int(df), df2=int(df2),
                   statistic=statistic, tail=tail, alpha=alpha,
                   title=str(title) if title is not None else 'Theoretical test-distribution explorer',
                   xLabel='Statistic', yLabel='Probability density',
                   note='Theoretical null model, not a test fitted to the dataset. Move degrees of freedom, statistic and alpha to explore tail probabilities and critical regions. Two-sided t uses 2 × the smaller tail. The visible curve may omit extreme tails; probabilities use the full distribution. Controls do not rerun Python or update other results. A probability below alpha alone does not establish model assumptions or practical importance.')
    _pj_plot_html(payload, name, width, height, accordion, expanded, color)
