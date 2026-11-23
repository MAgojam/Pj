"""Hospital bed-use nomograms. Calculations belong to the host, not the renderer."""

def _pj_bj_text(text, **values):
    """Translate literal message templates supplied by the R host."""
    translated = globals().get('_pj_bj_messages', {}).get(text, text)
    return translated.format(**values) if values else translated

def _pj_barber_johnson_prepare(dataset, *, view='toi_alos', input_mode='raw',
        unit='unit', period='period', period_days='period_days', beds='beds',
        available_bed_days=None, occupied_bed_days='occupied_bed_days',
        discharges='discharges', toi='toi', alos='alos', bor='bor',
        order=None, facet=None, group=None, turnover_days=365,
        occupancy_lines=(.5, .7, .8, .85, .9), turnover_lines=(15, 25, 35, 50),
        alos_lines=(3, 5, 7, 10, 14), scenarios=None, size_by_beds=False,
        max_toi=None, max_alos=None, max_bto=None, point_labels=False, title=None):
    """Return validated indicators; no input mutation or inferred clinical targets."""
    from numbers import Real
    from collections.abc import Mapping
    fn = 'mzpjShowBarberJohnson'
    def number(value, label, positive=False):
        if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(float(value)):
            raise ValueError(_pj_bj_text('{_v0}: {_v1} must be a finite number.', _v0=fn, _v1=label))
        value = float(value)
        if value < 0 or (positive and value == 0):
            raise ValueError(_pj_bj_text('{_v0}: {_v1} must be {_v2}.', _v0=fn, _v1=label, _v2='positive' if positive else 'non-negative'))
        return value
    if view not in ('toi_alos', 'toi_bto', 'trajectory', 'faceted'):
        raise ValueError(_pj_bj_text('view must be toi_alos, toi_bto, trajectory or faceted.'))
    if input_mode not in ('raw', 'toi_alos', 'alos_bor'):
        raise ValueError(_pj_bj_text('input_mode must be raw, toi_alos or alos_bor.'))
    if not isinstance(size_by_beds, bool):
        raise TypeError(_pj_bj_text('size_by_beds must be True or False.'))
    if not isinstance(point_labels, bool):
        raise TypeError(_pj_bj_text('point_labels must be True or False.'))
    turnover_days = number(turnover_days, 'turnover_days', True)
    if view == 'trajectory' and order is None:
        raise ValueError(_pj_bj_text('trajectory requires an explicit numeric order column.'))
    cols = [unit, period, order, facet, group]
    if isinstance(period_days, str):
        cols.append(period_days)
    else:
        number(period_days, 'period_days', True)
    if input_mode == 'raw':
        cols += [occupied_bed_days, discharges, available_bed_days if available_bed_days else beds]
    else:
        cols += [alos, toi if input_mode == 'toi_alos' else bor]
        if size_by_beds:
            cols.append(beds)
    n = _pj_plot_columns(dataset, cols, fn)
    points, excluded, keys = [], [], set()
    def missing(v):
        return v is None or (isinstance(v, Real) and not math.isfinite(float(v))) or (isinstance(v, str) and not v.strip())
    for i in range(n):
        if any(missing(dataset[c][i]) for c in dict.fromkeys(c for c in cols if c is not None)):
            excluded.append(i + 1)
            continue
        u, label = str(dataset[unit][i]), str(dataset[period][i])
        key = (u, label)
        if key in keys:
            raise ValueError(_pj_bj_text('{_v0}: duplicate unit/period at row {_v1}: {_v2} / {_v3}. Aggregate or correct the source data first.', _v0=fn, _v1=i + 1, _v2=u, _v3=label))
        keys.add(key)
        days = number(dataset[period_days][i] if isinstance(period_days, str) else period_days, f'row {i+1} period_days', True)
        b = None
        if input_mode == 'raw':
            capacity = number(dataset[available_bed_days][i], f'row {i+1} available_bed_days', True) if available_bed_days else number(dataset[beds][i], f'row {i+1} beds', True) * days
            occupied = number(dataset[occupied_bed_days][i], f'row {i+1} occupied_bed_days')
            exits = number(dataset[discharges][i], f'row {i+1} discharges', True)
            if not exits.is_integer():
                raise ValueError(_pj_bj_text('{_v0}: discharges must be whole counts (row {_v1}).', _v0=fn, _v1=i + 1))
            if occupied > capacity:
                raise ValueError(_pj_bj_text('{_v0}: occupied bed-days exceed available bed-days at row {_v1}; check the capacity definition.', _v0=fn, _v1=i + 1))
            a, t, p, b = occupied / exits, (capacity - occupied) / exits, occupied / capacity, capacity / days
            actual_bto = exits / b
        else:
            a = number(dataset[alos][i], f'row {i+1} alos', True)
            if input_mode == 'toi_alos':
                t = number(dataset[toi][i], f'row {i+1} toi')
                p = a / (a + t)
            else:
                p = number(dataset[bor][i], f'row {i+1} bor', True)
                if p > 1:
                    raise ValueError(_pj_bj_text('{_v0}: bor is a proportion in (0, 1], not a percentage (row {_v1}).', _v0=fn, _v1=i + 1))
                t = a * (1 / p - 1)
            actual_bto = days / (a + t)
            if size_by_beds:
                b = number(dataset[beds][i], f'row {i+1} beds', True)
        if not all(math.isfinite(v) for v in (a, t, p, actual_bto, turnover_days / (a + t))):
            raise ValueError(_pj_bj_text('{_v0}: row {_v1} produces indicators outside the supported finite range.', _v0=fn, _v1=i + 1))
        point = dict(row=i+1, unit=u, period=label, days=days, alos=a, toi=t, bor=p,
                     bto=actual_bto, btoStandard=turnover_days/(a+t), beds=b,
                     group=str(dataset[group][i]) if group else u,
                     facet=str(dataset[facet][i]) if facet else u,
                     order=number(dataset[order][i], f'row {i+1} order') if order else i)
        points.append(point)
    if not points:
        raise ValueError(_pj_bj_text('{_v0}: no complete observations are available.', _v0=fn))
    if len(points) > 2000:
        raise ValueError(_pj_bj_text('{_v0}: use at most 2000 complete unit-period observations per result.', _v0=fn))
    if view == 'trajectory':
        ordered = [(p['unit'], p['order']) for p in points]
        if len(ordered) != len(set(ordered)):
            raise ValueError(_pj_bj_text('Each unit must have a unique numeric order in trajectory view.'))
    if view == 'faceted' and len({p['facet'] for p in points}) > 12:
        raise ValueError(_pj_bj_text('Use at most 12 facets per result; filter or split the dataset.'))
    def levels(values, label, proportion=False):
        if isinstance(values, (str, bytes)):
            raise TypeError(_pj_bj_text('{_v0} must be a sequence of numbers.', _v0=label))
        result = sorted(set(number(v, label, True) for v in values))
        if len(result) > 12 or (proportion and any(v >= 1 for v in result)):
            raise ValueError(_pj_bj_text('{_v0}: use at most 12 values; occupancy lines must be proportions strictly between 0 and 1.', _v0=label))
        return result
    references = []
    if scenarios is not None:
        if isinstance(scenarios, (str, bytes, Mapping)):
            raise TypeError(_pj_bj_text('scenarios must be a sequence of dictionaries.'))
        for scenario in scenarios:
            if not isinstance(scenario, Mapping) or not isinstance(scenario.get('label'), str) or not scenario['label'].strip():
                raise ValueError(_pj_bj_text('Each scenario needs a non-empty label and a bor proportion or two-value interval.'))
            if set(scenario) - {'label', 'bor', 'toi', 'alos'}:
                raise ValueError(_pj_bj_text('Scenario fields are label, bor, toi and alos.'))
            value = scenario.get('bor')
            values = [value, value] if isinstance(value, Real) else list(value or [])
            if len(values) != 2:
                raise ValueError(_pj_bj_text('Scenario bor must be a proportion or two-value interval.'))
            low, high = (number(v, 'scenario bor', True) for v in values)
            if not 0 < low <= high < 1:
                raise ValueError(_pj_bj_text('Scenario bor must satisfy 0 < lower <= upper < 1.'))
            ref = dict(label=scenario['label'], bor=[low, high])
            for key in ('toi', 'alos'):
                bounds = scenario.get(key)
                if bounds is not None:
                    if isinstance(bounds, (str, bytes)) or len(bounds) != 2:
                        raise ValueError(_pj_bj_text('Scenario {_v0} needs two bounds.', _v0=key))
                    ref[key] = [number(v, 'scenario '+key) for v in bounds]
                    if ref[key][0] > ref[key][1]:
                        raise ValueError(_pj_bj_text('Scenario {_v0} bounds must be ordered.', _v0=key))
            references.append(ref)
        if len(references) > 6 or len({r['label'] for r in references}) != len(references):
            raise ValueError(_pj_bj_text('Use at most six scenarios with distinct labels.'))
    x_max = number(max_toi, 'max_toi', True) if max_toi is not None else max(1., max(p['toi'] for p in points)*1.25)
    y_max = number(max_alos, 'max_alos', True) if max_alos is not None else max(1., max(p['alos'] for p in points)*1.25)
    bto_max = number(max_bto, 'max_bto', True) if max_bto is not None else max(1., max(p['btoStandard'] for p in points)*1.25)
    outside = sum(p['toi'] > x_max or (p['btoStandard'] > bto_max if view == 'toi_bto' else p['alos'] > y_max) for p in points)
    note = _pj_bj_text('N = {n} unit-periods; {excluded} incomplete rows excluded; {outside} observations outside the displayed limits. BTO reference period: {days} days.',
                       n=len(points), excluded=len(excluded), outside=outside, days=f'{turnover_days:g}') + ' ' + _pj_bj_text(
            'BTO on this basis is a rate rescaling, not a forecast. Reference scenarios are user-selected, not quality or efficiency classifications.')
    if references:
        note += ' ' + _pj_bj_text('References:') + ' ' + '; '.join(r['label'] + ': BOR ' +
            '–'.join(f'{v*100:g}%' for v in dict.fromkeys(r['bor'])) +
            (f'; TOI {r["toi"][0]:g}–{r["toi"][1]:g} d' if 'toi' in r else '') +
            (f'; ALOS {r["alos"][0]:g}–{r["alos"][1]:g} d' if 'alos' in r else '') for r in references) + '.'
    ui = {key: _pj_bj_text(text) for key, text in (
        ('xLabel', 'Turnover interval (TOI, days)'),
        ('yLabel', 'ALOS (bed-days / discharges, days)'),
        ('btoLabel', 'BTO per {days} days'),
        ('status', 'Hover or focus a point to read its indicators. Click or press Enter to pin; Escape clears the selection.'),
        ('detail', '{unit} / {period} · {days} days · ALOS {alos} d · TOI {toi} d · BOR {bor}% · BTO {bto} per observed period; {reference} per {basis} d'),
        ('beds', 'mean beds'))}
    return dict(kind='barberJohnson', view=view, title=title or _pj_bj_text('Barber–Johnson: hospital bed utilisation'), ui=ui,
                points=points, turnoverDays=turnover_days, occupancyLines=levels(occupancy_lines, 'occupancy_lines', True),
                turnoverLines=levels(turnover_lines, 'turnover_lines'), alosLines=levels(alos_lines, 'alos_lines'),
                scenarios=references, sizeByBeds=size_by_beds, pointLabels=point_labels, xMax=x_max, yMax=y_max, btoMax=bto_max,
                note=note, excludedRows=excluded, outside=outside)


def _pj_show_barber_johnson(dataset, *, name=None, width=None, height=None,
        result_type='html', accordion=True, expanded=True, accordion_type='line',
        tables=True, **options):
    """Draw hospital TOI–ALOS, TOI–BTO, trajectories or facets using shared D3.

    See the bilingual Barber–Johnson manuals for column definitions, formulas,
    explicit period handling, reference scenarios and interpretation limits.
    width/height override popup values; in faceted view height is per panel.
    Returns the numerical report; tables=True emits a native indicator table.
    """
    if not isinstance(tables, bool):
        raise TypeError(_pj_bj_text('tables must be True or False.'))
    payload = _pj_barber_johnson_prepare(dataset, **options)
    base = _pj_result_name(name, 'barber_johnson', _plot_counter)
    if tables and any(item.get('name') == base+'_indicators' for item in results['items']):
        raise ValueError(_pj_bj_text('The indicator table name already exists; choose a different name.'))
    _pj_plot_html(payload, base, width, height, accordion, expanded, '#587295', result_type, accordion_type)
    rows = [dict(Unit=p['unit'], Period=p['period'], Days=p['days'],
                 ALOS=p['alos'], TOI=p['toi'], BOR_percent=100*p['bor'],
                 BTO_period=p['bto'], BTO_reference=p['btoStandard'], Mean_beds=p['beds']) for p in payload['points']]
    if tables:
        headings = dict(Unit=_pj_bj_text('Unit'), Period=_pj_bj_text('Period'), Days=_pj_bj_text('Period days'),
            ALOS=_pj_bj_text('ALOS (days)'), TOI=_pj_bj_text('TOI (days)'), BOR_percent=_pj_bj_text('BOR (%)'),
            BTO_period=_pj_bj_text('BTO observed period'), BTO_reference=_pj_bj_text('BTO reference period'),
            Mean_beds=_pj_bj_text('Mean available beds'))
        _pj_add_table([{headings[k]:v for k,v in row.items()} for row in rows], name=base+'_indicators', title=_pj_bj_text('Hospital bed utilisation indicators'), notes=payload['note'])
    return dict(indicators=rows, excluded_rows=payload['excludedRows'], outside=payload['outside'],
                turnover_days=payload['turnoverDays'], scenarios=payload['scenarios'])
