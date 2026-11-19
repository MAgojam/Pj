# Pj 1.6.2: HTML accordion styles and native Svg resizing.
# Open a NEW Pj/Pjp analysis, load this script and Run.
# Works with Embedded and System Python; no dataset or extra package is needed.
# HTML: accordion=True (default), expanded=True/False, accordion_type='line'/'bordered'.
# Native Svg: no accordion or HTML zoom; use jamovi's resize handle instead.
# All counts below are invented. The current jamovi dataset is not changed.

sample = {'Activity': ['Reading', 'Practice', 'Discussion'], 'Count': [12, 19, 8]}

# 1. Native vector figure: resize smaller AND larger, then release the handle.
# The chosen width and height should remain. There is no fold heading or zoom slider.
mzpjShowBar(
    sample, 'Activity', 'Count', stat='identity', orientation='horizontal',
    result_type='svg', name='native_svg', title='Native Svg: resize with jamovi',
    x_label='Illustrative response count', y_label='Activity', width=700, height=360
)

# 2. HTML charts: line starts open; bordered starts closed for comparison.
# Click a heading or use Enter/Space. The HTML zoom is inside the container.
for style in ('line', 'bordered'):
    mzpjShowBar(
        sample, 'Activity', 'Count', stat='identity', orientation='horizontal',
        result_type='html', name=style+'_chart', title='HTML chart: '+style,
        x_label='Illustrative response count', y_label='Activity',
        width=700, height=360, accordion_type=style, expanded=(style == 'line')
    )

# 3. HTML content: the same two styles, initially closed.
mzpjShowHtml(
    '<p>The line style uses animated SVG strokes, a short rule before the title, '
    'and a trailing rule that extends when opened. The open title becomes bold.</p>',
    name='line_html', title='HTML report: default line style', expanded=False
)
mzpjShowHtml(
    '<p>The bordered style has rules above and below the heading. '
    'Its SVG chevron rotates downward when opened.</p>',
    name='bordered_html', title='HTML report: bordered style',
    accordion_type='bordered', expanded=False
)

# 4. HTML tables support both containers; native jamovi Table results do not.
for style in ('line', 'bordered'):
    mzpjShowTable(
        sample, name='table_'+style, title='HTML table: '+style,
        render='html', accordion_type=style, expanded=False
    )

# 5. Explicit opt-out: HTML content displayed directly without a container.
mzpjShowHtml(
    '<p>This HTML paragraph is displayed directly with accordion=False.</p>',
    name='plain_html', title='HTML without an accordion', accordion=False
)

mzpjShowText(
    'Checks: native Svg keeps its size after dragging; HTML headings fold and '
    'unfold with animation; the line rule extends when open; bordered rules '
    'keep their width. HTML zoom remains available inside HTML charts. '
    'Accordion options apply only to HTML, including tables rendered as HTML. '
    'Native Svg, Image and Table results have no accordion. '
    'Folding an HTML container does not rerun Python.',
    name='accordion_help'
)
