# Normalizzazione e presentazione delle tabelle native e HTML.

def _pj_add_table(data, name=None, title=None, columns=None, formats=None,
                  notes=None, include_index=True, column_groups=None,
                  combine_below=None, footnotes=None, symbols=None,
                  render='native', zebra=False, column_styles=None,
                  row_styles=None, cell_styles=None, digits=3, transpose=False,
                  accordion=False, expanded=True, max_height=None, sticky_header=False,
                  max_width=None, scroll='auto'):
    """Converte dati tabellari in risultati nativi o HTML, senza dipendenze obbligatorie."""
    from collections.abc import Mapping
    import re
    from numbers import Integral

    if not isinstance(transpose, bool):
        raise TypeError('mzpjShowTable(): transpose must be True or False.')
    for parameter, value in (('accordion', accordion), ('expanded', expanded), ('sticky_header', sticky_header)):
        if not isinstance(value, bool):
            raise TypeError(f'mzpjShowTable(): {parameter} must be True or False.')
    if max_height is not None and (isinstance(max_height, bool) or
            not isinstance(max_height, Integral) or max_height <= 0):
        raise ValueError('mzpjShowTable(): max_height must be a positive integer in pixels or None.')
    if max_width is not None and (isinstance(max_width, bool) or
            not isinstance(max_width, Integral) or max_width <= 0):
        raise ValueError('mzpjShowTable(): max_width must be a positive integer in pixels or None.')
    if scroll not in ('auto', 'both', 'vertical', 'horizontal', 'none'):
        raise ValueError("mzpjShowTable(): scroll must be 'auto', 'both', 'vertical', 'horizontal' or 'none'.")
    if max_height is not None and scroll in ('horizontal', 'none'):
        raise ValueError('mzpjShowTable(): omit max_height when vertical scrolling is disabled; all rows remain visible.')
    if not accordion and not expanded:
        raise ValueError('mzpjShowTable(): expanded=False requires accordion=True.')
    if sticky_header and max_height is None:
        raise ValueError('mzpjShowTable(): sticky_header=True requires max_height.')
    if render == 'native' and (accordion or max_height is not None or sticky_header or
                               max_width is not None or scroll != 'auto'):
        raise ValueError("mzpjShowTable(): accordion, dimensions and scrolling require render='html'.")
    if render not in ('native', 'html'):
        raise ValueError("mzpjShowTable(): render must be 'native' or 'html'.")
    if render == 'native' and (zebra is not False or column_styles is not None or
                               row_styles is not None or cell_styles is not None or digits != 3):
        raise ValueError("mzpjShowTable(): colors, zebra and digits require render='html'.")

    if columns is not None:
        if isinstance(columns, (str, bytes)):
            raise TypeError('mzpjShowTable(): columns must be a sequence of column labels.')
        columns = list(columns)

    # Non importa pandas: riconosce i DataFrame solo se gia' utilizzati dall'utente.
    pandas = sys.modules.get('pandas')
    if pandas is not None and isinstance(data, pandas.DataFrame):
        labels = list(data.columns)
        rows = data.to_numpy(dtype=object).tolist()
        if columns is not None:
            if len(columns) != len(labels):
                raise ValueError('mzpjShowTable(): columns must match the number of data columns.')
            labels = columns
        if include_index:
            labels = [data.index.name if data.index.name is not None else 'Index'] + labels
            rows = [[index] + row for index, row in zip(data.index, rows)]
    elif isinstance(data, Mapping):
        labels = list(data) if columns is None else columns
        if any(label not in data for label in labels):
            raise ValueError('mzpjShowTable(): a requested column is missing from the data.')
        values = []
        for label in labels:
            column = data[label]
            if isinstance(column, (str, bytes, Mapping)):
                raise TypeError('mzpjShowTable(): dictionary values must be column sequences.')
            values.append(list(column))
        if len({len(column) for column in values}) > 1:
            raise ValueError('mzpjShowTable(): all columns must have the same length.')
        rows = [list(row) for row in zip(*values)]
    else:
        if isinstance(data, (str, bytes)):
            raise TypeError('mzpjShowTable(): data must be tabular.')
        rows = list(data)
        if rows and isinstance(rows[0], Mapping):
            if not all(isinstance(row, Mapping) for row in rows):
                raise TypeError('mzpjShowTable(): all rows must have the same structure.')
            labels = list(dict.fromkeys(key for row in rows for key in row)) if columns is None else columns
            rows = [[row.get(label) for label in labels] for row in rows]
        else:
            if any(isinstance(row, (str, bytes, Mapping)) for row in rows):
                raise TypeError('mzpjShowTable(): rows must be sequences or dictionaries.')
            rows = [list(row) for row in rows]
            width = len(rows[0]) if rows else 0
            labels = columns if columns is not None else [f'Column {i + 1}' for i in range(width)]

    labels = [str(label) for label in labels]
    if not labels or len(set(labels)) != len(labels):
        raise ValueError('mzpjShowTable(): column labels must be non-empty and unique.')
    if any(not label for label in labels) or any(len(row) != len(labels) for row in rows):
        raise ValueError('mzpjShowTable(): each row must match the column labels.')
    if formats is not None and not isinstance(formats, Mapping):
        raise TypeError('mzpjShowTable(): formats must be a dictionary keyed by column label.')
    formats = {} if formats is None else formats
    if any(key not in labels or not isinstance(value, str) for key, value in formats.items()):
        raise ValueError('mzpjShowTable(): formats must contain existing column labels and string values.')
    if notes is None:
        notes = []
    elif isinstance(notes, str):
        notes = [notes]
    else:
        notes = list(notes)
    if not all(isinstance(note, str) for note in notes):
        raise TypeError('mzpjShowTable(): notes must be strings.')

    def scalar(value):
        if pandas is not None and (value is pandas.NA or value is pandas.NaT):
            return None
        if isinstance(value, tuple):
            return ' / '.join(str(part) for part in value)
        value = _json_safe_value(value)
        # _json_safe_value puo' estrarre un float non finito da uno scalare NumPy.
        if isinstance(value, float) and not math.isfinite(value):
            return None
        if value is not None and not isinstance(value, (str, bool, int, float)):
            raise TypeError('mzpjShowTable(): cells must contain scalar strings, numbers or missing values.')
        return value

    rows = [[scalar(value) for value in row] for row in rows]
    if column_groups is None:
        column_groups = {}
    if not isinstance(column_groups, Mapping):
        raise TypeError('mzpjShowTable(): column_groups must be a dictionary keyed by column label.')
    if any(label not in labels or not isinstance(group, str) or not group.strip()
           for label, group in column_groups.items()):
        raise ValueError('mzpjShowTable(): column_groups requires existing columns and non-empty group titles.')
    if transpose and column_groups:
        raise ValueError('mzpjShowTable(): transpose cannot be combined with column_groups; omit grouped headers.')
    if combine_below is None:
        combine_below = []
    if isinstance(combine_below, (str, bytes, Mapping)):
        raise TypeError('mzpjShowTable(): combine_below must be a sequence of column labels.')
    combine_below = list(combine_below)
    if any(label not in labels for label in combine_below):
        raise ValueError('mzpjShowTable(): combine_below contains an unknown column label.')

    def cell_annotations(values, parameter):
        from numbers import Integral
        if values is None:
            return []
        if not isinstance(values, Mapping):
            raise TypeError(f'mzpjShowTable(): {parameter} must be a dictionary keyed by (row, column label).')
        annotations = []
        for key, text in values.items():
            if not isinstance(key, tuple) or len(key) != 2:
                raise ValueError(f'mzpjShowTable(): {parameter} keys must be (row, column label) tuples.')
            row, column = key
            if isinstance(row, bool) or not isinstance(row, Integral) or not 0 <= row < len(rows):
                raise ValueError(f'mzpjShowTable(): {parameter} row must be a valid zero-based row position.')
            if column not in labels:
                raise ValueError(f'mzpjShowTable(): {parameter} contains an unknown column label.')
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f'mzpjShowTable(): {parameter} text must be a non-empty string.')
            annotations.append({'row': int(row), 'column': f'c{labels.index(column) + 1}', 'text': text})
        return annotations

    cell_footnotes = cell_annotations(footnotes, 'footnotes')
    cell_symbols = cell_annotations(symbols, 'symbols')
    definitions = []
    for i, label in enumerate(labels):
        present = [row[i] for row in rows if row[i] is not None]
        numeric = bool(present) and all(isinstance(value, (int, float)) and
                                       not isinstance(value, bool) for value in present)
        kind = 'number' if numeric else 'text'
        if numeric and all(isinstance(value, int) and -2147483648 <= value <= 2147483647
                           for value in present):
            kind = 'integer'
        if not numeric:
            for row in rows:
                if row[i] is not None:
                    row[i] = str(row[i])
        definitions.append({'name': f'c{i + 1}', 'title': label, 'type': kind,
                            'format': formats.get(label, ''),
                            'superTitle': column_groups.get(label),
                            'combineBelow': label in combine_below})

    name = _pj_result_name(name, 'table', _table_counter, table=True)
    item = {'type': 'Table', 'name': name, 'title': str(title) if title is not None else 'Python table',
            'columns': definitions, 'rows': rows, 'notes': notes,
            'footnotes': cell_footnotes, 'symbols': cell_symbols, 'transpose': transpose}
    if render == 'html':
        item = {'type': 'Html', 'name': name, 'title': item['title'], '_pjTable': True,
                'content': _pj_table_html(item, zebra, column_styles, row_styles, cell_styles, digits,
                                          accordion, expanded, max_height, sticky_header, max_width, scroll)}
    # Un nome esplicito aggiorna la stessa tabella senza duplicare il risultato.
    for i, existing in enumerate(results['items']):
        if existing.get('name') == name:
            if existing.get('type') != 'Table' and not existing.get('_pjTable'):
                raise ValueError('mzpjShowTable(): this name is already used by another result type.')
            results['items'][i] = item
            return
    results['items'].append(item)

def _pj_table_html(item, zebra, column_styles, row_styles, cell_styles, digits,
                   accordion=False, expanded=True, max_height=None, sticky_header=False,
                   max_width=None, scroll='auto'):
    """Rende i dati gia' normalizzati; gli stili restano confinati alla tabella."""
    from collections.abc import Mapping
    from numbers import Integral
    from html import escape
    import re

    columns, rows = item['columns'], item['rows']
    labels = [column['title'] for column in columns]
    if isinstance(digits, bool) or not isinstance(digits, Integral) or not 0 <= digits <= 12:
        raise ValueError('mzpjShowTable(): digits must be an integer between 0 and 12.')

    def color(value):
        names = {'black', 'white', 'red', 'green', 'blue', 'navy', 'teal', 'purple',
                 'maroon', 'olive', 'gray', 'grey', 'silver', 'yellow', 'orange',
                 'aqua', 'fuchsia', 'lime', 'transparent'}
        if not isinstance(value, str) or not (value.lower() in names or
                re.fullmatch(r'#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})', value)):
            raise ValueError('mzpjShowTable(): colors must be hex colors or supported basic CSS color names.')
        return value

    if isinstance(zebra, str):
        stripes = (None, color(zebra))
    elif isinstance(zebra, bool):
        stripes = (None, '#f0f4fa' if zebra else None)
    elif isinstance(zebra, (tuple, list)):
        if len(zebra) != 2:
            raise ValueError('mzpjShowTable(): zebra requires exactly two alternating colors.')
        stripes = tuple(None if value is None else color(value) for value in zebra)
    else:
        raise TypeError('mzpjShowTable(): zebra must be True, False, a color or a pair of colors.')

    def valid_row(row):
        return not isinstance(row, bool) and isinstance(row, Integral) and 0 <= row < len(rows)

    def styles(values, parameter):
        if values is None:
            return {}
        if not isinstance(values, Mapping):
            raise TypeError(f'mzpjShowTable(): {parameter} must be a dictionary.')
        out = {}
        for key, style in values.items():
            valid = (key in labels) if parameter == 'column_styles' else (
                valid_row(key) if parameter == 'row_styles' else
                isinstance(key, tuple) and len(key) == 2 and valid_row(key[0]) and key[1] in labels)
            if not valid:
                raise ValueError(f'mzpjShowTable(): invalid row or column in {parameter}.')
            if not isinstance(style, Mapping) or any(prop not in ('color', 'background', 'bold') for prop in style):
                raise ValueError(f'mzpjShowTable(): {parameter} styles support color, background and bold only.')
            out[key] = {}
            for prop, value in style.items():
                if prop == 'bold':
                    if not isinstance(value, bool):
                        raise TypeError('mzpjShowTable(): bold must be True or False.')
                    out[key]['font-weight'] = '600' if value else '400'
                else:
                    out[key]['background-color' if prop == 'background' else 'color'] = color(value)
        return out

    col_css = styles(column_styles, 'column_styles')
    row_css = styles(row_styles, 'row_styles')
    cell_css = styles(cell_styles, 'cell_styles')
    supported = {'pvalue', 'zto'}
    for column in columns:
        tokens = {token.strip() for token in column['format'].split(',') if token.strip()}
        if not tokens <= supported:
            raise ValueError("mzpjShowTable(): HTML formats support 'pvalue' and 'zto'; use digits for precision.")

    footnotes, footnote_marks = [], {}
    def marker(index):
        text = ''
        while index:
            index, remainder = divmod(index - 1, 26)
            text = chr(97 + remainder) + text
        return text

    annotations = {}
    for note in item['footnotes']:
        text = note['text']
        if text not in footnote_marks:
            footnotes.append(text)
            footnote_marks[text] = marker(len(footnotes))
        annotations.setdefault((note['row'], note['column']), []).append(footnote_marks[text])
    for symbol in item['symbols']:
        annotations.setdefault((symbol['row'], symbol['column']), []).append(symbol['text'])

    def display(value, column):
        if value is None:
            return '.'
        if column['type'] == 'text':
            return str(value)
        tokens = [token.strip() for token in column['format'].split(',')]
        if 'pvalue' in tokens:
            precision = max(1, digits)
            cutoff = 10 ** -precision
            if 0 <= value < cutoff:
                return '< ' + f'{cutoff:.{precision}f}'.lstrip('0')
            return f'{value:.{precision}f}'.lstrip('0') if 0 <= value < 1 else f'{value:.{precision}f}'
        if column['type'] == 'integer' and 'zto' not in tokens:
            return str(value)
        return f'{value:.{digits}f}'

    body = []
    for row_no, row in enumerate(rows):
        rendered_row = []
        for col_no, column in enumerate(columns):
            css = {'padding': '7px 10px', 'border-bottom': '1px solid #e2e8f0',
                   'text-align': 'left' if column['type'] == 'text' else 'right'}
            css.update(col_css.get(column['title'], {}))
            css.update(row_css.get(row_no, {}))
            css.update(cell_css.get((row_no, column['title']), {}))
            value = display(row[col_no], column)
            if column['combineBelow'] and row_no and row[col_no] == rows[row_no-1][col_no]:
                value = ''
            text = escape(value)
            for mark in annotations.get((row_no, column['name']), []):
                text += '<sup style="margin-left:2px;font-size:75%">' + escape(mark) + '</sup>'
            rendered_row.append({'text': text, 'css': css})
        body.append(rendered_row)

    def header(text, align='left'):
        return {'text': text, 'css': {'text-align': align, 'padding': '8px 10px',
                'border-bottom': '1px solid #3e6da9', 'font-weight': '600', 'white-space': 'nowrap'}}

    headers = [header(escape(column['title']), 'left' if column['type'] == 'text' else 'right')
               for column in columns]
    if item['transpose']:
        original = body
        headers = [headers[0]] + [dict(cell[0], css=dict(cell[0]['css'], **{
            'font-weight': cell[0]['css'].get('font-weight', '600'),
            'border-bottom': '1px solid #3e6da9'})) for cell in original]
        body = [[header(escape(columns[col]['title']))] + [row[col] for row in original]
                for col in range(1, len(columns))]

    layout = accordion or max_height is not None or max_width is not None or scroll != 'auto'
    horizontal = scroll in ('auto', 'both', 'horizontal')

    def cell_html(cell, tag, stripe_color=None):
        css = {}
        if stripe_color:
            css['background-color'] = stripe_color
        css.update(cell['css'])
        if layout and not horizontal:
            css.update({'white-space': 'normal', 'overflow-wrap': 'anywhere'})
        style = ';'.join(f'{key}:{value}' for key, value in css.items())
        scope = ' scope="col"' if tag == 'th' else ''
        return f'<{tag}{scope} style="' + escape(style, quote=True) + '">' + cell['text'] + f'</{tag}>'

    wrapper_class = 'mzpj-styled-table' + (' mzpj-table-layout' if layout else '')
    parts = ['<div class="' + wrapper_class + '" style="max-width:100%;' +
             (('width:' + (f'{int(max_width)}px' if max_width is not None else '100%') +
               ';min-width:0;contain:inline-size;box-sizing:border-box;') if layout else '') +
             'color:#1e293b;font:13px/1.45 Arial,sans-serif">']
    if layout:
        # Selettori confinati al contenitore Pj; nessuno script o stile del core.
        parts.append('''<style>
.mzpj-table-layout { margin-bottom:12px; }
.mzpj-table-layout .mzpj-table-accordion > summary { display:flex;align-items:center;gap:8px;list-style:none;cursor:pointer;color:#3e6da9;padding:5px 0;font-weight:500; }
.mzpj-table-layout .mzpj-table-accordion > summary::-webkit-details-marker { display:none; }
.mzpj-table-layout .mzpj-table-accordion > summary:focus-visible { outline:2px solid #3e6da9;outline-offset:3px;border-radius:2px; }
.mzpj-table-layout .mzpj-table-icon { display:flex;flex-shrink:0;padding-right:7px;border-right:1px solid rgba(62,109,169,.35); }
.mzpj-table-layout .mzpj-table-icon svg { width:16px;height:16px; }
.mzpj-table-layout .mzpj-table-icon-v { transform-origin:8px 8px;transition:opacity .15s ease,transform .15s ease; }
.mzpj-table-layout .mzpj-table-accordion[open] > summary .mzpj-table-icon-v { opacity:0;transform:rotate(90deg); }
.mzpj-table-layout .mzpj-table-title { display:flex;align-items:center;gap:8px;flex:1;min-width:0;overflow-wrap:anywhere; }
.mzpj-table-layout .mzpj-table-title::before,.mzpj-table-layout .mzpj-table-title::after { content:'';height:1px;background:rgba(62,109,169,.35);flex:0 0 24px; }
.mzpj-table-layout .mzpj-table-accordion[open] > summary { font-weight:600; }
.mzpj-table-layout .mzpj-table-accordion[open] > summary .mzpj-table-title::after { flex:1 0 24px; }
.mzpj-table-layout .mzpj-table-body { padding-top:9px; }
.mzpj-table-layout .mzpj-table-viewport { scrollbar-gutter:stable; }
.mzpj-table-layout .mzpj-table-viewport th,.mzpj-table-layout .mzpj-table-viewport td { white-space:nowrap; }
.mzpj-table-layout .mzpj-table-viewport[data-wrap] th,.mzpj-table-layout .mzpj-table-viewport[data-wrap] td { white-space:normal;overflow-wrap:anywhere; }
@media (prefers-reduced-motion:reduce) { .mzpj-table-layout .mzpj-table-icon-v { transition:none; } }
</style>''')
    if accordion:
        parts.append('<details class="mzpj-table-accordion"' + (' open' if expanded else '') + '><summary>'
                     '<span class="mzpj-table-icon" aria-hidden="true"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2">'
                     '<line x1="4" y1="8" x2="12" y2="8"/><line class="mzpj-table-icon-v" x1="8" y1="4" x2="8" y2="12"/>'
                     '</svg></span><span class="mzpj-table-title">' + escape(item['title']) + '</span></summary><div class="mzpj-table-body">')
    viewport = 'max-width:100%;overflow-x:auto'
    if layout:
        # clip non attiva uno scroll container sull'asse disabilitato.
        # Con un asse auto, hidden evita barre sull'altro; le celle vengono adattate.
        overflow_x = 'auto' if horizontal else ('clip' if scroll == 'none' else 'hidden')
        overflow_y = 'auto' if scroll in ('auto', 'both', 'vertical') else ('clip' if scroll == 'none' else 'hidden')
        viewport = f'width:100%;max-width:100%;min-width:0;box-sizing:border-box;overflow-x:{overflow_x};overflow-y:{overflow_y}'
    if max_height is not None:
        viewport += f';max-height:{int(max_height)}px;overflow-y:auto'
    parts.append('<div' + (' class="mzpj-table-viewport"' if layout else '') +
                 (' data-wrap="true"' if layout and not horizontal else '') +
                 (' tabindex="0" role="region" aria-label="' + escape(item['title'], quote=True) + '"' if layout else '') +
                 ' style="' + viewport + '">')
    table_style = ('border-collapse:separate;border-spacing:0' if sticky_header else 'border-collapse:collapse')
    if layout and not horizontal:
        table_style += ';table-layout:fixed'
    parts.append('<table style="' + table_style + ';width:100%;font:inherit;color:inherit"' +
                 (' aria-label="' + escape(item['title'], quote=True) + '"' if accordion else '') + '>')
    if not accordion:
        parts.append('<caption style="text-align:left;font-weight:600;padding:0 0 9px;color:#3e6da9">' + escape(item['title']) + '</caption>')
    # L'intero thead resta fisso: anche le intestazioni su due righe dei gruppi.
    parts.append('<thead' + (' style="position:sticky;top:0;z-index:1;background:#fff"' if sticky_header else '') + '>')
    if any(column['superTitle'] for column in columns):
        parts.append('<tr>')
        i = 0
        while i < len(columns):
            group = columns[i]['superTitle'] or ''
            j = i + 1
            while j < len(columns) and (columns[j]['superTitle'] or '') == group:
                j += 1
            parts.append(f'<th scope="colgroup" colspan="{j-i}" style="padding:7px 10px;text-align:center;border-top:1px solid #3e6da9;border-bottom:1px solid #cbd5e1;font-weight:600">{escape(group)}</th>')
            i = j
        parts.append('</tr>')
    parts.append('<tr>' + ''.join(cell_html(cell, 'th') for cell in headers) + '</tr></thead><tbody>')
    for row_no, row in enumerate(body):
        stripe_color = stripes[row_no % 2]
        parts.append('<tr>' + ''.join(cell_html(cell, 'td', stripe_color) for cell in row) + '</tr>')
    parts.append('</tbody></table></div>')
    if item['notes'] or footnotes:
        parts.append('<div style="margin-top:9px;font-size:12px;color:#475569">')
        for note in item['notes']:
            parts.append('<div style="margin-top:3px"><em>Note.</em> ' + escape(note) + '</div>')
        for note in footnotes:
            parts.append('<div style="margin-top:3px"><sup>' + footnote_marks[note] + '</sup> ' + escape(note) + '</div>')
        parts.append('</div>')
    if accordion:
        parts.append('</div></details>')
    parts.append('</div>')
    return ''.join(parts)


