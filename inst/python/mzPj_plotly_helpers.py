"""Guided Plotly helpers: host preparation, shared JavaScript recipes, no plotly import."""

def _pj_plotly_style(*, color='#3e6da9', palette=None, show_legend=True,
                     hover_mode='closest', drag_mode='zoom', modebar=None):
    import re
    if not isinstance(show_legend, bool):
        raise TypeError('show_legend must be True or False.')
    if hover_mode is not False and (not isinstance(hover_mode, str) or hover_mode not in ('closest', 'x', 'y', 'x unified', 'y unified')):
        raise ValueError('hover_mode must be closest, x, y, x unified, y unified or False.')
    if drag_mode is not False and (not isinstance(drag_mode, str) or drag_mode not in ('zoom', 'pan', 'select', 'lasso')):
        raise ValueError('drag_mode must be zoom, pan, select, lasso or False.')
    if modebar is not None and not (isinstance(modebar, bool) or modebar == 'hover'):
        raise TypeError('modebar must be None, True, False or hover.')
    def check(value):
        if not isinstance(value, str) or re.fullmatch(r'#[0-9a-fA-F]{6}', value) is None:
            raise ValueError('Colors must use six-digit hexadecimal notation, such as #3e6da9.')
        return value
    check(color)
    if palette is None:
        palette = [color, '#c77a18', '#268477', '#8767a9', '#b85664', '#64748b']
    elif not isinstance(palette, (list, tuple)) or not palette:
        raise TypeError('palette must be a non-empty list or tuple of colors.')
    return dict(palette=[check(value) for value in palette], showLegend=show_legend,
                hoverMode=hover_mode, dragMode=drag_mode, modebar=modebar)


def _pj_plotly_prepare(kind, *args, **kwargs):
    names = {'scatter': 'Scatter', 'line': 'Line', 'bar': 'Bar', 'boxplot': 'BoxPlot'}
    try:
        return globals()['_pj_prepare_' + kind](*args, **kwargs)
    except (TypeError, ValueError) as error:
        raise type(error)(str(error).replace('mzpjShow' + names[kind],
                                            'mzpjShowPlotly' + names[kind])) from None


def _pj_plotly_finish(kind, payload, style, display):
    import json
    display = dict(display)
    layout = display.pop('layout', {})
    if not isinstance(layout, dict):
        raise TypeError('layout must be a dictionary of Plotly layout options.')
    layout = json.loads(json.dumps(layout, allow_nan=False))
    config = display.get('config')
    if config is not None and not isinstance(config, dict):
        raise TypeError('config must be a dictionary.')
    config = dict(config or {})
    if style['modebar'] is not None:
        config['displayModeBar'] = style['modebar']
    display['config'] = config
    display.setdefault('title', payload['title'])
    figure = dict(data=[], layout=layout, mzGraphics=dict(
        protocol=1, kind=kind, payload=payload, options=style))
    _pj_show_plotly(figure, **display)


def _pj_show_plotly_scatter(dataset, x, y, group=None, labels=None, *,
                           marker_size=8, opacity=0.85, color='#3e6da9', palette=None,
                           x_label=None, y_label=None, show_legend=True,
                           hover_mode='closest', drag_mode='zoom', modebar=None, **display):
    """Interactive grouped scatter. Select/lasso/pan through drag_mode; modebar hidden by default.

    display accepts name, title, height, config, layout, result_type, static,
    export_width and Html accordion options. No regression is fitted.
    """
    if isinstance(marker_size, bool) or not isinstance(marker_size, (int, float)) or not 2 <= marker_size <= 40:
        raise ValueError('marker_size must be between 2 and 40.')
    if isinstance(opacity, bool) or not isinstance(opacity, (int, float)) or not 0 < opacity <= 1:
        raise ValueError('opacity must be above 0 and at most 1.')
    payload = _pj_plotly_prepare('scatter', dataset, x, y, group=group, labels=labels,
                                 x_label=x_label, y_label=y_label)
    style = _pj_plotly_style(color=color, palette=palette, show_legend=show_legend,
                            hover_mode=hover_mode, drag_mode=drag_mode, modebar=modebar)
    style.update(markerSize=marker_size, opacity=opacity)
    _pj_plotly_finish('scatter', payload, style, display)


def _pj_show_plotly_line(dataset, x, y, group=None, labels=None, *, sort_x=False,
                        connect_gaps=False, show_points=True, color='#3e6da9', palette=None,
                        x_label=None, y_label=None, show_legend=True,
                        hover_mode='x unified', drag_mode='zoom', modebar=None, **display):
    """Grouped profiles with explicit sorting, missing-value gaps and unified hover.

    Interactions do not fit or change a statistical model. See mzpjShowPlotlyScatter
    for the shared display options; the toolbar is hidden unless requested.
    """
    payload = _pj_plotly_prepare('line', dataset, x, y, group=group, labels=labels,
        sort_x=sort_x, connect_gaps=connect_gaps, show_points=show_points,
        x_label=x_label, y_label=y_label)
    style = _pj_plotly_style(color=color, palette=palette, show_legend=show_legend,
                            hover_mode=hover_mode, drag_mode=drag_mode, modebar=modebar)
    _pj_plotly_finish('line', payload, style, display)


def _pj_show_plotly_bar(dataset, category, value=None, group=None, *, stat='count',
                       orientation='vertical', bar_mode='group', show_values=False,
                       color='#3e6da9', palette=None, x_label=None, y_label=None,
                       show_legend=True, hover_mode='closest', drag_mode='zoom', modebar=None,
                       **display):
    """Count/sum/mean/identity bars with grouped, stacked or relative presentation.

    Counts and aggregation are computed in Python, not by Plotly. Empty cells
    are zero for counts and missing for other statistics. No interval is implied.
    """
    function = 'mzpjShowPlotlyBar'
    if not isinstance(show_values, bool):
        raise TypeError('show_values must be True or False.')
    if bar_mode not in ('group', 'stack', 'relative'):
        raise ValueError('bar_mode must be group, stack or relative.')
    _pj_bar_arguments(category, value, stat, orientation, function)
    if group is None:
        base = _pj_plotly_prepare('bar', dataset, category, value, stat=stat,
                                  orientation=orientation, x_label=x_label, y_label=y_label)
        series = [dict(name=value or 'Count', bars=base['bars'])]
    else:
        count = _pj_plot_columns(dataset, [category, value, group], function)
        rows = []
        for i in range(count):
            category_key = _pj_plot_category(dataset[category][i])
            group_key = _pj_plot_category(dataset[group][i])
            number = 1 if stat == 'count' else _pj_plot_number(dataset[value][i], value, i, function)
            if category_key is not None and group_key is not None and number is not None:
                rows.append((category_key, group_key, number))
        if not rows:
            raise ValueError(function + '(): no complete finite observations are available.')
        categories = _pj_plot_categories([row[0] for row in rows])
        groups = _pj_plot_categories([row[1] for row in rows])
        series = []
        for key, label in groups.items():
            selected = [row for row in rows if row[1] == key]
            subset = {'category': [categories[row[0]] for row in selected],
                      'value': [row[2] for row in selected]}
            prepared = _pj_plotly_prepare('bar', subset, 'category',
                None if stat == 'count' else 'value', stat=stat, orientation=orientation)
            series.append(dict(name=label, bars=prepared['bars']))
        base = dict(prepared)
        measure = 'Frequency' if stat == 'count' else value if stat == 'identity' else f'{stat.capitalize()} of {value}'
        base['title'] = f'{measure} by {category}'
        xlabel, ylabel = (category, measure) if orientation == 'vertical' else (measure, category)
        base['xLabel'] = x_label if x_label is not None else xlabel
        base['yLabel'] = y_label if y_label is not None else ylabel
        base['categories'] = list(categories.values())
        base['note'] = (f'N = {len(rows)}; {count-len(rows)} rows excluded. Statistic: {stat}. '
                        'Aggregation is within category and group. No uncertainty interval is calculated.')
    base['series'] = series
    base['stat'] = stat
    if group is None:
        base['categories'] = [bar['category'] for bar in base['bars']]
    style = _pj_plotly_style(color=color, palette=palette, show_legend=show_legend,
                            hover_mode=hover_mode, drag_mode=drag_mode, modebar=modebar)
    style.update(barMode=bar_mode, showValues=show_values)
    _pj_plotly_finish('bar', base, style, display)


def _pj_show_plotly_boxplot(dataset, variable, group=None, labels=None, *, show_points=False,
                           color='#3e6da9', palette=None, x_label=None, y_label=None,
                           show_legend=True, hover_mode='closest', drag_mode='zoom', modebar=None,
                           **display):
    """Host-computed linear quartiles and 1.5-IQR whiskers, with outliers retained.

    show_points displays all observed points; otherwise only potential outliers.
    Quartile calculation is the same as the D3 boxplot, with no inference test.
    """
    payload = _pj_plotly_prepare('boxplot', dataset, variable, group=group, labels=labels,
                                 show_points=show_points, x_label=x_label, y_label=y_label)
    payload['note'] = payload['note'].replace('Horizontal jitter only separates overlapping points.',
        'Points retain their category position; overlapping values are not jittered.')
    style = _pj_plotly_style(color=color, palette=palette, show_legend=show_legend,
                            hover_mode=hover_mode, drag_mode=drag_mode, modebar=modebar)
    _pj_plotly_finish('boxplot', payload, style, display)


def _pj_show_plotly_heatmap(matrix, x_labels=None, y_labels=None, *, color_scale='Viridis',
                          show_values=False, zmin=None, zmax=None, reverse_scale=False,
                          x_label='', y_label='', hover_mode='closest', modebar=None, **display):
    """Display a rectangular numeric matrix, without implicit correlation or normalization.

    None/nonfinite cells are gaps. Labels must be unique. For a fixed color scale
    supply both zmin and zmax. Up to 10000 cells are supported.
    """
    if not isinstance(matrix, (list, tuple)) or not matrix:
        raise TypeError('matrix must be a non-empty list or tuple of rows.')
    if any(not isinstance(row, (list, tuple)) or not row for row in matrix):
        raise TypeError('Each matrix row must be a non-empty list or tuple.')
    columns = len(matrix[0])
    if any(len(row) != columns for row in matrix) or len(matrix)*columns > 10000:
        raise ValueError('matrix must be rectangular and contain at most 10000 cells.')
    allowed = ('Viridis', 'Cividis', 'Blues', 'RdBu', 'Plasma', 'Inferno', 'Greys')
    if color_scale not in allowed:
        raise ValueError('color_scale must be one of: ' + ', '.join(allowed))
    if not isinstance(show_values, bool) or not isinstance(reverse_scale, bool):
        raise TypeError('show_values and reverse_scale must be True or False.')
    values = [[_pj_plot_number(v, 'matrix', i, 'mzpjShowPlotlyHeatmap') for v in row]
              for i, row in enumerate(matrix)]
    finite = [v for row in values for v in row if v is not None]
    if not finite:
        raise ValueError('matrix must contain at least one finite observation.')
    if (zmin is None) != (zmax is None):
        raise ValueError('Supply both zmin and zmax, or neither.')
    if zmin is not None:
        zmin = _pj_plot_number(zmin, 'zmin', 0, 'mzpjShowPlotlyHeatmap')
        zmax = _pj_plot_number(zmax, 'zmax', 0, 'mzpjShowPlotlyHeatmap')
        if zmin is None or zmax is None or zmin >= zmax:
            raise ValueError('zmin and zmax must be finite, with zmin below zmax.')
    def labels(value, length, prefix):
        if value is None:
            return [f'{prefix} {i+1}' for i in range(length)]
        if not isinstance(value, (list, tuple)) or len(value) != length:
            raise ValueError(prefix + ' labels must match the matrix dimensions.')
        result = [str(v) for v in value]
        if len(set(result)) != length:
            raise ValueError(prefix + ' labels must be unique.')
        return result
    payload = dict(z=values, x=labels(x_labels, columns, 'Column'),
                   y=labels(y_labels, len(values), 'Row'), title='Matrix heatmap',
                   xLabel=str(x_label), yLabel=str(y_label),
                   note='Raw supplied values; missing/nonfinite cells are gaps. No normalization or correlation is computed.')
    style = _pj_plotly_style(show_legend=False, hover_mode=hover_mode, modebar=modebar)
    style.update(colorScale=color_scale, showValues=show_values, zmin=zmin,
                 zmax=zmax, reverseScale=reverse_scale)
    _pj_plotly_finish('heatmap', payload, style, display)
