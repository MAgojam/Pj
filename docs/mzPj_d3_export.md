# Native D3 figures and document export

Native D3 Svg results are available in Pj 1.4.0 or newer.
All ten D3 plotting helpers accept an optional final argument:

```python
mzpjShowDistribution(mean=0, sd=1, n=30, result_type='svg')
mzpjShowScatter(data, x='x', y='y', result_type='svg')
```

| Mode | Results behaviour | Export route |
|---|---|---|
| `result_type='html'` (default) | Existing interactive HTML panel and accordion | HTML/PDF use the original HTML/script configuration. This does not provide reliable DOCX/ODT figure export. |
| `result_type='svg'` | Native jamovi Svg figure with D3 controls and interactions | SVG/PNG from the figure menu; documents through Analysis/All → Export. |

Native mode exports **D3 vector geometry**, unlike Chart.js static mode's PNG
inside SVG. Both Python interpreters use the same bundled D3 renderer; no
external renderer or statistical dependency is added. Choosing a result type
does not change any calculation or modify dataset columns.

## Figure and controls

Each renderer uses one main SVG; correlation and paired explorers already
contain their linked views in that single SVG. Native mode marks it with
`jmv-results-svg-content`, embeds scoped styles and preserves dimensions/viewBox.
An accordion icon is not selected as the exported image.

Native mode uses the result's heading and an open layout, without an accordion.
The accordion arguments retain validation but do not collapse a native figure.
A footer inside the SVG includes supplied notes, current-view context and
coloured group keys. It adds height below the requested drawing area and updates
when parameters/selections change. Thus the exported figure does not rely on
HTML controls to communicate essential context.

HTML controls remain usable in Results but are excluded from figure export.
Native HTML/PDF document exports are static figure images. Choose
`result_type='html'` for an interactive standalone HTML document; it restarts from
the Python-supplied configuration, rather than preserving every browser action.

Selections remain descriptive. They do not refit models, update native tables
or write back analysis options. OMV save/reopen and control-state restoration
are separate tests: a native snapshot is not a saved analysis option.

## Script 58

Load `pjscript/58_d3_native_svg_export.py` through **Scripts → Load**.
No dataset is required. It provides a native table, supplied estimates/intervals
and a normal sampling-distribution explorer. `RESULT_TYPE = 'svg'` is set for
the trial; change to `'html'` to compare the previous mode.

First try **Analysis → Export → DOCX**. Check figures, axes, colours, notes,
proportions and page fit. Export SVG separately from the figure's own menu.
Change N in Results and check the updated curve/context in a new export.
Existing Data Library files do not need to be changed for this trial.

## Validation scope and limits

Manual Windows testing of example 58 confirmed the script and its Word DOCX
export: native table, both figures, notes and good document formatting. This
acceptance concerns that example and format; it does not certify all ten helpers,
ODT, SVG-file export, OMV reopening or other operating systems.

Automated Windows checks render all ten native types, verify self-contained
styles/vector geometry and exercise N/group changes in the footer. Representative
figures are processed by jamovi's figure extraction and DOCX/ODT converter sources:
packages contain figure PNGs without JavaScript text. These checks are not manual
desktop acceptance for all helpers, formats or operating systems.

Document sizing belongs to jamovi. In the inspected sources, native Svg
hydration leaves width/height unspecified; DOCX/ODT may choose default dimensions.
Check aspect ratio and fit. SVG-file and document-page exports are different
paths. The existing HTML default remains unchanged. Removed client instances
disconnect listeners/observers. Minifier sources remain local; generated bundles
are the distributed resources.

## Public Python service

The same keyword works through `mzPjRunPython`, without an editor. A host choosing
native mode must map a returned `Svg` item to `jmvcore::Svg` and `setContent()`.
Inspect `mzPjServiceInfo()` result types; existing hosts can continue requesting
HTML. See the [service guide](mzPj_service_api.md).
