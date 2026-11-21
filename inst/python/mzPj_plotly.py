# Plotly: interactive Html, static Svg, or a native PNG Image.
def _pj_show_plotly(figure, *, name=None, title=None, height=None, config=None,
                    static=False, export_width=None, width=None, result_type=None,
                    accordion=True, expanded=True, accordion_type='line'):
    """Show a Figure or data/layout dictionary as Html, Svg or native Image.

    The interactive modebar is hidden by default. Pass
    config={'displayModeBar': True} to show it, or 'hover' to show it on hover.
    Svg/Image always exclude the modebar. Hover labels and the clickable
    legend remain available in Html when the modebar is hidden.
    """
    import json
    import uuid
    import html
    _pj_accordion_options(accordion, expanded, accordion_type)
    mode = _pj_graphic_mode(result_type, static)
    static = mode != 'html'
    if width is not None and export_width is not None and width != export_width:
        raise ValueError('width and export_width must agree when both are supplied.')
    if width is not None:
        export_width = width
    if export_width is None:
        export_width = _pj_figure_dimension(globals().get('FIGWIDTH'), 600)
    if height is None:
        height = _pj_figure_dimension(globals().get('FIGHEIGHT'), 500)
    if not isinstance(static, bool):
        raise TypeError('static must be True or False.')
    if isinstance(export_width, bool) or not isinstance(export_width, int) or not 400 <= export_width <= 2400:
        raise ValueError('export_width must be an integer between 400 and 2400.')
    if isinstance(height, bool) or not isinstance(height, int) or not 200 <= height <= 3000:
        raise ValueError('height must be an integer between 200 and 3000.')
    if isinstance(figure, dict):
        payload = json.loads(json.dumps(figure, allow_nan=False))
    elif hasattr(figure, 'to_json'):
        payload = json.loads(figure.to_json())
    else:
        raise TypeError('mzpjShowPlotly() expects a Plotly Figure or a data/layout dictionary.')
    if not isinstance(payload, dict) or not isinstance(payload.get('data'), list):
        raise TypeError('Plotly data must be a list of trace dictionaries.')
    if not isinstance(payload.get('layout', {}), dict):
        raise TypeError('Plotly layout must be a dictionary.')
    payload.setdefault('layout', {})['height'] = height
    payload['layout']['autosize'] = not static
    payload['layout'].pop('width', None)
    settings = dict(responsive=True, displaylogo=False, scrollZoom=False)
    if config is not None:
        if not isinstance(config, dict):
            raise TypeError('config must be a dictionary of Plotly configuration options.')
        settings.update(config)
    if static:
        payload['layout']['width'] = export_width
        settings.update(responsive=False, staticPlot=True, displayModeBar=False)
    def safe(value):
        return json.dumps(value, ensure_ascii=True, allow_nan=False).replace('<', '\\u003c')
    root_id = 'mzpj_plotly_' + uuid.uuid4().hex
    name = _pj_result_name(name, 'plotly', _plot_counter)
    plot_title = payload['layout'].get('title', {})
    plot_title = plot_title.get('text', 'Plotly figure') if isinstance(plot_title, dict) else str(plot_title)
    heading = html.escape(str(title or plot_title))
    if static:
        # La superficie temporanea scompare dopo toImage: nessun listener persistente.
        content = (f'<div id="{root_id}" class="mz-plotly" style="width:max-content;max-width:100%">'
                   '<p class="mz-plotly-status ignore-html" role="status" '
                   'style="font:12px Arial;color:#657b9b">Preparing static Plotly image...</p>'
                   f'<svg xmlns="http://www.w3.org/2000/svg" class="jmv-results-svg-content jmv-results-svg-selection" '
                   f'width="{export_width}" height="{height}" viewBox="0 0 {export_width} {height}" '
                   'style="max-width:100%;height:auto">'
                   f'<title>{heading}</title><image width="{export_width}" height="{height}" /></svg></div>')
    else:
        content = f'<div id="{root_id}" class="mz-plotly" style="width:{export_width}px;max-width:100%;height:{height}px">Loading Plotly...</div>'
    if not _pj_plotly_js or not _pj_plotly_css:
        raise RuntimeError('The shared Plotly renderer is unavailable. Reinstall the updated Pj module.')
    options = dict(figure=payload, config=settings, asset=_pj_plotly_gzip,
                   static=static, width=export_width, height=height,
                   libraryName='mzPjPlotly411')
    # Serialize once: user labels are never reinterpreted as template tokens.
    content = '<style>' + _pj_plotly_css + '</style>' + content
    if not static:
        content = ('<style>.jmv-results-html:has(#' + root_id + ':not([data-mz-size-zoom]))'
                   '{width:' + str(export_width) + 'px;min-width:0;max-width:100%}</style>') + content
    content += ('<script>' + _pj_plotly_js + '</script><script>(function(){'
                'const root=document.getElementById(' + safe(root_id) + ');'
                'window.mzPlotly.render(root,' + safe(options) + ').catch(()=>{});'
                '})();</script>')
    scripts = ['extdata/plotly.min.js'] if not _pj_plotly_gzip else None
    if static:
        _pj_emit_graphic(content, name, html.unescape(heading), mode, scripts=scripts,
                         accordion=accordion, expanded=expanded, accordion_type=accordion_type)
    else:
        content = _pj_wrap_accordion(content, html.unescape(heading), accordion, expanded, accordion_type)
        item = dict(type='Html', name=name, title='' if accordion else (title or ''), content=content)
        if scripts:
            item['scripts'] = scripts
        results['items'].append(item)
