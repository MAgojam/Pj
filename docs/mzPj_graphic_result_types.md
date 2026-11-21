# Graphic result types: Html, Svg and Image

[Shared accordion options](mzPj_accordions.md) — Pj 1.6.2.

> **Pj 1.6.1 / jamovi 28.18 (18 November 2026).** The minimum is now
> jamovi 28.18.0, inclusive. The official runtime includes the native SVG
> document-save fix. Earlier advisories below describe the affected 28.17
> baseline. The separate Office aspect-ratio and Rj resize limitations remain;
> see the [1.6.1 release notes](mzPj_release_1_6_1.md).


Pj 1.6.0 provides `result_type='html'`, `'svg'` or `'image'` for Chart.js,
Plotly and all ten D3 plotting helpers. The option selects the native jamovi
Results container. It does not change the statistical calculations.

| Choice | Behaviour | Native result after preparation |
|---|---|---|
| `html` | Interactive plot with its controls | `Html` |
| `svg` | Figure content, axes, legend and notes; no interactive controls | `Svg` |
| `image` | PNG snapshot of that same figure content | `Image` |

D3 Svg retains vector geometry. Chart.js and Plotly Svg wrap a PNG snapshot
inside an SVG container; they are not vector conversions. `image` gives them a
true native Image instead. Captured images have a white background.

## Choosing the type in Python

```python
mzpjShowChart('bar', [{'label': 'Mean', 'data': [2.5, 3.8]}],
              labels=['A', 'B'], name='group_means',
              title='Group means', result_type='image', width=700, height=360,
              options={'locale': 'en-US'})

mzpjShowLine({'Time': [0, 1, 2], 'Score': [3, 5, 4]}, 'Time', 'Score',
             name='profile', title='Observed profile', result_type='svg')

# figure is a Plotly Figure constructed by the caller.
# mzpjShowPlotly(figure, name='plotly_image', result_type='image')
```

Image capture runs in the Pj/Pjp Results browser after Python returns. A short
preparation message is replaced with the native Image. Wait for all these
messages to disappear before exporting or saving the jamovi document. A failure
is displayed explicitly; there is no silent conversion back to Html or Svg.
Accordion controls, zoom buttons, tooltips and floating control panels are not
part of the captured image. Plot titles are native Results headings.

The callback is bound to the current figure's unique token. It replaces only
that pending result, preserves other Results, Output and dataext, and does not
rerun the Python script. Old or duplicate callbacks are ignored.

Large images are downsampled to at most 4 million pixels with an edge limit of
4000 pixels; displayed dimensions are at most 2000 pixels. PNG payloads are
limited to 1 million base64 characters each. Pending captures share a 1.5 million
character / 20 figure callback limit, in addition to Pj's overall Results budget.
Reduce figure size or split a large report into separate analyses if needed.

## Compatibility and service hosts

Existing calls are preserved. D3 defaults to Html. For Chart.js and Plotly,
`static=False` keeps Html and `static=True` keeps Svg. An explicit `result_type`
selects the type; `static=True, result_type='html'` is rejected as contradictory.
Prefer `result_type` for new code.

Browser-generated `image` requires the updated Pj/Pjp editor capture bridge.
The R Python service API does not enable this bridge: it rejects this selection
with a clear error. Another module must provide its own supported capture
integration; it must not merely enable a flag without implementing the callback.

The original PNG path remains available in both editors and service hosts:

```python
import io
# figure is a Matplotlib Figure; Matplotlib must be installed in this interpreter.
buffer = io.BytesIO()
figure.savefig(buffer, format='png', dpi=150, facecolor='white')
mzpjShowImage(buffer, name='my_plot', title='My plot')
buffer.close()
```

`mzpjShowImage` accepts valid PNG bytes or a binary buffer/stream directly.
Matplotlib `plt.show()` captured by Pj also produces Image. `mzpjShowHtml` keeps
Html; arbitrary HTML pages are not automatically rasterized by this selector.
Examples 05, 06 and 24 illustrate the existing PNG route. Example 74 compares
the new modes; examples 71–73 now use native Image for their statistical plots.

## Verification and export scope — 16 November 2026

Only Windows is compiled and tested for this update. Pj remains 1.6.0 and Rust
1.1.0 is unchanged. The minimum jamovi version remains 28.17.0 inclusive.

Browser tests captured Chart.js, D3 and Plotly to PNG, including a closed D3
accordion and multiple concurrent figures. Engine lifecycle tests cover Pj and
Pjp with Embedded and System Python, state persistence, stale/duplicate callbacks,
invalid PNG rejection and no Python rerun. The resulting native Image renders
to PDF through the normal R renderer.

These checks do not certify complete desktop PDF/DOCX/LaTeX/OMV workflows for
the new selector. Those remain manual acceptance tests on the Windows portable
28.17.2. Prior Word checks included native Svg figures, but prior LaTeX ZIPs
omitted them; successful PNG Image export does not certify native Svg export.
The corrected portable 28.17.2 is Windows-only. No new Ubuntu/macOS build or test
is performed for this change. Wide Word table layout and full TeX compilation
remain separate checks.


## Quiet native Image preparation

Pending Image capture containers and their temporary headings are rendered
offscreen until the native Image replaces them. No Preparing Image text is
shown in Results. The original title is retained for the final Image.
The container remains renderable; display:none is not used because it can
break plot measurement. Capture/decode errors, backend errors and a missing
acknowledgement restore a visible error result. Timers are cleared when the
pending result is removed. Python is not rerun during that replacement.
This applies to D3, Chart.js and Plotly Image capture; direct PNG results and
Html/Svg behavior are unchanged. Wait for final Images before export.
