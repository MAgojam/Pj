# Run in the Pjp editor; no external service script is needed.
# Pjp supplies the selected variables as data: do not load or recreate the dataset.
# Select author, tpos, tneg, cpos, cneg; year and D1-D5/Overall are optional.
# Works with either Python interpreter when SciPy is available; no pandas or matplotlib.
import json
import math
import statistics
import uuid
from collections import Counter

try:
    from scipy.optimize import minimize_scalar
    from scipy.stats import chi2, norm
except ImportError as error:
    raise ImportError('This example requires SciPy in the selected Python interpreter.') from error

# This map contains existing column names, not study data.
COLUMNS = {'study': 'author', 'year': 'year',
           'a': 'tpos', 'b': 'tneg', 'c': 'cpos', 'd': 'cneg'}
ROB_COLUMNS = ['D1', 'D2', 'D3', 'D4', 'D5', 'Overall']
SHOW_STUDY_TABLE = True
# Change False to True below, then Run, to add seven calculated columns to the dataset.
# Change back to False and Run to remove this analysis's output columns again.
# False displays only tables and the forest plot; original dataset columns are retained.
# The columns contain log RR, its variance and SE, RR, its CI limits, and study weight (%).
WRITE_COLUMNS = False
CONFIDENCE = 0.95

required = [COLUMNS[key] for key in ('study', 'a', 'b', 'c', 'd')]
missing = [name for name in required if name not in data]
if missing:
    raise ValueError('Select these variables in Pjp: ' + ', '.join(missing) + '.')
if not 0 < CONFIDENCE < 1:
    raise ValueError('CONFIDENCE must be between 0 and 1.')
if not d3_script:
    raise RuntimeError('The bundled D3 library is unavailable.')
row_count = len(data[required[0]])
if any(len(data[name]) != row_count for name in data):
    raise ValueError('Selected variables must have the same number of rows.')
z_critical = float(norm.ppf(0.5 + CONFIDENCE / 2))
studies, omitted, corrected = [], [], []
rob_columns = [name for name in ROB_COLUMNS if name in data]

for row in range(row_count):
    cells = [data[COLUMNS[key]][row] for key in ('a', 'b', 'c', 'd')]
    if any(value is None or (isinstance(value, float) and math.isnan(value)) for value in cells):
        omitted.append((row + 1, 'missing counts'))
        continue
    try:
        counts = [float(value) for value in cells]
    except (TypeError, ValueError) as error:
        raise ValueError(f'Row {row + 1}: counts must be non-negative integers.') from error
    if any(isinstance(value, bool) for value in cells) or any(
            not math.isfinite(value) or value < 0 or not value.is_integer() for value in counts):
        raise ValueError(f'Row {row + 1}: counts must be finite non-negative integers.')
    a, b, c, d = counts
    if a + b == 0 or c + d == 0:
        raise ValueError(f'Row {row + 1}: each treatment arm must contain participants.')
    # Exclude studies with no events in either arm, or no non-events in either arm.
    if (a == 0 and c == 0) or (b == 0 and d == 0):
        omitted.append((row + 1, 'double-zero events or non-events'))
        continue
    original_counts = [int(value) for value in counts]
    # Add 0.5 to all four cells only when at least one cell is zero.
    if min(counts) == 0:
        a, b, c, d = [value + 0.5 for value in counts]
        corrected.append(row + 1)
    yi = math.log(a / (a + b)) - math.log(c / (c + d))
    vi = 1 / a - 1 / (a + b) + 1 / c - 1 / (c + d)
    if not math.isfinite(yi) or not math.isfinite(vi) or vi <= 0:
        raise ValueError(f'Row {row + 1}: the sampling variance must be positive and finite.')
    label = str(data[COLUMNS['study']][row] or f'Study {row + 1}')
    if COLUMNS['year'] in data and data[COLUMNS['year']][row] is not None:
        label += ' (' + str(data[COLUMNS['year']][row]) + ')'
    se = math.sqrt(vi)
    studies.append({'row': row, 'label': label, 'counts': original_counts,
                    'yi': yi, 'vi': vi, 'se': se, 'rr': math.exp(yi),
                    'lower': math.exp(yi - z_critical * se),
                    'upper': math.exp(yi + z_critical * se),
                    'rob': [data[name][row] for name in rob_columns]})

k = len(studies)
if k < 2:
    raise ValueError('At least two complete studies with positive sampling variances are required.')
duplicates = Counter(study['label'] for study in studies)
for study in studies:
    if duplicates[study['label']] > 1:
        study['label'] += f" [row {study['row'] + 1}]"
ys, vs = [study['yi'] for study in studies], [study['vi'] for study in studies]


def reml_objective(tau_squared):
    """Profiled restricted negative log likelihood for an intercept-only model."""
    weights = [1 / (variance + tau_squared) for variance in vs]
    total = math.fsum(weights)
    mean = math.fsum(weight * y for weight, y in zip(weights, ys)) / total
    return 0.5 * (math.fsum(math.log(variance + tau_squared) for variance in vs)
                  + math.log(total)
                  + math.fsum(weight * (y - mean) ** 2 for weight, y in zip(weights, ys)))


# Expand the search interval until the objective increases at the upper end.
upper_bound = max(statistics.variance(ys), max(vs), 1e-4)
for attempt in range(60):
    if reml_objective(upper_bound * 2) > reml_objective(upper_bound):
        upper_bound *= 2
        break
    upper_bound *= 2
else:
    raise ArithmeticError('Could not bracket the REML variance estimate.')
fit = minimize_scalar(reml_objective, bounds=(0, upper_bound), method='bounded',
                      options={'xatol': 1e-12, 'maxiter': 1000})
if not fit.success or not math.isfinite(float(fit.fun)):
    raise ArithmeticError('REML estimation did not converge.')
tau2 = 0.0 if reml_objective(0) <= float(fit.fun) else float(fit.x)
weights = [1 / (variance + tau2) for variance in vs]
sw = math.fsum(weights)
estimate = math.fsum(weight * y for weight, y in zip(weights, ys)) / sw
se_model = math.sqrt(1 / sw)
statistic = estimate / se_model
p_model = float(2 * norm.sf(abs(statistic)))
ci_low, ci_high = estimate - z_critical * se_model, estimate + z_critical * se_model
# Normal-approximation prediction interval, matching predict.rma() with test='z'.
prediction_se = math.sqrt(tau2 + se_model ** 2)
pi_low, pi_high = estimate - z_critical * prediction_se, estimate + z_critical * prediction_se
sw2, sw3 = math.fsum(w ** 2 for w in weights), math.fsum(w ** 3 for w in weights)
se_tau2 = math.sqrt(2 / (sw2 - 2 * sw3 / sw + (sw2 / sw) ** 2))
fixed_weights = [1 / variance for variance in vs]
sfw = math.fsum(fixed_weights)
fixed_mean = math.fsum(w * y for w, y in zip(fixed_weights, ys)) / sfw
q = math.fsum(w * (y - fixed_mean) ** 2 for w, y in zip(fixed_weights, ys))
df = k - 1
p_q = float(chi2.sf(q, df))
# I2/H2 use metafor's typical sampling variance, rather than the Q-only approximation.
typical_variance = df / (sfw - math.fsum(w ** 2 for w in fixed_weights) / sfw)
i2, h2 = 100 * tau2 / (tau2 + typical_variance), 1 + tau2 / typical_variance
for study, weight in zip(studies, weights):
    study['weight'] = 100 * weight / sw
confidence_label = f'{100 * CONFIDENCE:g}% CI'
notes = ['Effect measure: log risk ratio; vaccinated group / control group.',
         'Tau-squared estimator: restricted maximum likelihood (REML). Test: z-test.',
         f'{100 * CONFIDENCE:g}% prediction interval (RR scale): '
         f'[{math.exp(pi_low):.4f}, {math.exp(pi_high):.4f}]. Normal approximation.',
         f'Analyzed {k} of {row_count} rows. Study order follows the selected dataset.']
if omitted:
    notes.append('Excluded rows: ' + '; '.join(f'{row}: {reason}' for row, reason in omitted) + '.')
if corrected:
    notes.append('Continuity correction: 0.5 added to all four cells in rows ' +
                 ', '.join(map(str, corrected)) + '.')

mzpjShowTable(
    [{'Term': 'Intercept', 'Estimate': estimate, 'SE': se_model, 'z': statistic,
      'p': p_model, 'LL': ci_low, 'UL': ci_high}],
    name='bcg_model', title=f'Random-effects model (k = {k})',
    formats={'Estimate': 'zto', 'SE': 'zto', 'z': 'zto', 'p': 'pvalue', 'LL': 'zto', 'UL': 'zto'},
    column_groups={'LL': confidence_label, 'UL': confidence_label}, notes=notes)
mzpjShowTable(
    [{'Tau': math.sqrt(tau2), 'Tau-squared': tau2, 'SE (Tau-squared)': se_tau2,
      'I-squared (%)': i2, 'H-squared': h2, 'Q': q, 'df': df, 'p': p_q}],
    name='bcg_heterogeneity', title='Heterogeneity statistics',
    formats={'Tau': 'zto', 'Tau-squared': 'zto', 'SE (Tau-squared)': 'zto',
             'I-squared (%)': 'zto', 'H-squared': 'zto', 'Q': 'zto', 'p': 'pvalue'},
    notes='I-squared and H-squared use the REML estimate and the typical sampling variance.')
if SHOW_STUDY_TABLE:
    mzpjShowTable(
        [{'Study': s['label'], 'log RR': s['yi'], 'Variance': s['vi'], 'RR': s['rr'],
          'LL': s['lower'], 'UL': s['upper'], 'Weight (%)': s['weight']} for s in studies],
        name='bcg_studies', title='Study effects and random-effects weights',
        formats={key: 'zto' for key in ('log RR', 'Variance', 'RR', 'LL', 'UL', 'Weight (%)')},
        column_groups={'LL': confidence_label, 'UL': confidence_label})

if WRITE_COLUMNS:
    outputs = {'pj_log_rr': 'yi', 'pj_var_log_rr': 'vi', 'pj_se_log_rr': 'se',
               'pj_rr': 'rr', 'pj_rr_ci_low': 'lower', 'pj_rr_ci_high': 'upper',
               'pj_re_weight_pct': 'weight'}
    # Avoid overwriting selected variables already present in the dataset.
    if any(name in data for name in outputs):
        raise ValueError('Output names already selected. Deselect the pj_* output columns before rerunning.')
    for name, key in outputs.items():
        values = [None] * row_count
        for study in studies:
            values[study['row']] = study[key]
        data[name] = values

payload = {'studies': studies, 'robColumns': rob_columns, 'confidence': confidence_label,
           'pooled': {'rr': math.exp(estimate), 'lower': math.exp(ci_low), 'upper': math.exp(ci_high),
                      'piLower': math.exp(pi_low), 'piUpper': math.exp(pi_high)},
           'heterogeneity': {'tau2': tau2, 'i2': i2, 'h2': h2, 'q': q, 'df': df, 'p': p_q}}
# Prevent dataset names and labels from closing the HTML script block.
encoded = json.dumps(payload, ensure_ascii=True, allow_nan=False)
encoded = encoded.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
root_id = 'bcg_' + uuid.uuid4().hex
html = d3_script + '''
<style>
.mzpj-bcg { max-width:100%; color:#1e293b; font:13px/1.5 sans-serif; }
.mzpj-bcg summary { cursor:pointer; color:#3e6da9; font-weight:600; }
.mzpj-bcg > summary { display:flex; align-items:center; gap:8px; padding:8px 0;
    border-top:1px solid #dce5ef; border-bottom:1px solid #dce5ef; }
.mzpj-bcg summary svg { flex:none; }
.mzpj-bcg[open] > summary .vertical { display:none; }
.mzpj-bcg .controls { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin:8px 0; min-height:24px; }
.mzpj-bcg .zoom-control { position:relative; width:110px; height:20px; flex:none; }
.mzpj-bcg .zoom { appearance:none; -webkit-appearance:none; position:absolute; width:110px;
    height:20px; margin:0; background:transparent; cursor:pointer; }
.mzpj-bcg .zoom::-webkit-slider-runnable-track { height:2px; background:#3e6da9; border-radius:1px; }
.mzpj-bcg .zoom::-webkit-slider-thumb { appearance:none; -webkit-appearance:none;
    width:16px; height:16px; margin-top:-7px; opacity:0; }
.mzpj-bcg .zoom::-moz-range-track { height:2px; background:#3e6da9; border-radius:1px; }
.mzpj-bcg .zoom::-moz-range-thumb { width:16px; height:16px; opacity:0; border:0; }
.mzpj-bcg .zoom-control:focus-within { outline:2px solid #bdcde2; outline-offset:3px; border-radius:3px; }
.mzpj-bcg .zoom:focus { outline:none; }
.mzpj-bcg .zoom-marker { position:absolute; top:2px; width:16px; height:16px;
    border-radius:50%; background:#e87352; color:white; font:700 9px/16px sans-serif;
    text-align:center; pointer-events:none; transform:translateX(-50%); }
.mzpj-bcg .zoom-value { color:#64748b; font-size:11px; min-width:30px; }
.mzpj-bcg button { border:1px solid #bdcde2; border-radius:4px; background:white; color:#3e6da9; padding:3px 10px; }
.mzpj-bcg .viewport { max-width:100%; max-height:780px; overflow:auto; border-bottom:1px solid #dce5ef; }
.mzpj-bcg .legend { margin:10px 0; }
.mzpj-bcg .legend span { margin-right:16px; display:inline-flex; align-items:center; gap:5px; }
.mzpj-bcg .legend i { width:15px; height:15px; border-radius:50%; display:inline-block; }
.mzpj-bcg .note { color:#64748b; font-size:12px; margin:10px 0; }
</style>
<details class="mzpj-bcg" id="__ROOT__" open>
<summary><svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7h10" stroke="currentColor" stroke-width="1.6"/><path class="vertical" d="M7 2v10" stroke="currentColor" stroke-width="1.6"/></svg>Forest plot — risk ratio (REML)</summary>
<div class="controls"><span class="zoom-control"><input class="zoom" type="range" min="0.5" max="2" step="0.05" value="1" aria-label="Forest plot zoom" title="Resize the entire forest plot proportionally"><span class="zoom-marker" aria-hidden="true">Z</span></span><span class="zoom-value" aria-hidden="true">100%</span><button type="button">Reset</button></div>
<details class="legend"><summary>Risk-of-bias legend</summary><div>
<span><i style="background:#168c4e"></i>Low risk (+)</span>
<span><i style="background:#eca038"></i>Some concerns (?)</span>
<span><i style="background:#c0392b"></i>High risk (−)</span>
<span><i style="background:#bdbdbd"></i>No information</span>
</div></details>
<div class="viewport" tabindex="0" aria-label="Scrollable forest plot"></div>
<p class="note">Diamond: confidence interval for the pooled effect. Orange horizontal dashed line: prediction interval. Orange vertical dashed line: pooled effect. Gray vertical dotted line: no effect (RR = 1).</p>
<p class="note">Risk-of-bias judgments are taken from the selected dataset columns, not calculated by this script. Hover over a study or judgment for details. Zoom resizes the whole plot; effect sizes and the risk-ratio axis remain unchanged.</p>
</details>
<script>
(function () {
    const payload = __PAYLOAD__;
    const root = document.getElementById('__ROOT__');
    const rows = payload.studies, rob = payload.robColumns;
    const W = Math.max(1180, 1060 + 36 * rob.length), H = 130 + rows.length * 32 + 130;
    const left = 470, right = W - (rob.length * 34 + 270), firstY = 116;
    const pooledY = firstY + rows.length * 32 + 26, axisY = pooledY + 60;
    const svg = d3.select(root.querySelector('.viewport')).append('svg')
        .attr('width', W).attr('height', H).attr('viewBox', `0 0 ${W} ${H}`)
        .attr('role','img').attr('aria-label','BCG vaccine random-effects forest plot');
    const format = d3.format('.2f'), fmtWeight = d3.format('.1f');
    const ciText = d => `${format(d.rr)} [${format(d.lower)}, ${format(d.upper)}]`;
    const totals = [0,0,0,0]; rows.forEach(d => d.counts.forEach((v,i) => totals[i] += v));
    const low = Math.min(0.5, d3.min(rows,d=>d.lower),payload.pooled.lower,payload.pooled.piLower) / 1.3;
    const high = Math.max(2,d3.max(rows,d=>d.upper),payload.pooled.upper,payload.pooled.piUpper) * 1.3;
    function text(parent,x,y,value,anchor='start',weight=400,color='#334155') {
        return parent.append('text').attr('x',x).attr('y',y).attr('text-anchor',anchor)
            .attr('dominant-baseline','middle').attr('fill',color).attr('font-size',12)
            .attr('font-weight',weight).text(value);
    }
    function judgment(value) {
        const label = value == null ? '' : String(value).trim().toLowerCase();
        if (['low','low risk','+'].includes(label)) return ['#168c4e','+','Low risk'];
        if (['high','high risk','-','−'].includes(label)) return ['#c0392b','−','High risk'];
        if (['some concerns','unclear','?'].includes(label)) return ['#eca038','?','Some concerns'];
        return ['#bdbdbd','','No information'];
    }
    function draw() {
        svg.selectAll('*').remove();
        svg.append('rect').attr('width',W).attr('height',H).attr('fill','white');
        const x = d3.scaleLog().domain([low,high]).range([left,right]);
        const clipId = '__ROOT___clip';
        svg.append('defs').append('clipPath').attr('id',clipId).append('rect')
            .attr('x',left).attr('y',96).attr('width',right-left).attr('height',pooledY-76);
        text(svg,14,24,`Risk ratio — ${payload.confidence}`, 'start',600,'#3e6da9');
        text(svg,270,58,'Vaccinated','middle',600);text(svg,399,58,'Control','middle',600);
        text(svg,14,82,'Study','start',600);
        [238,302,367,431].forEach((cx,i)=>text(svg,cx,82,i%2?'(−)':'(+)','end',600));
        text(svg,right+110,82,`RR [${payload.confidence}]`,'middle',600);
        text(svg,right+218,82,'W%','end',600);
        rob.forEach((name,j)=>text(svg,right+262+j*34,82,name==='Overall'?'OA':name,'middle',600));
        svg.append('line').attr('x1',10).attr('x2',W-10).attr('y1',98).attr('y2',98).attr('stroke','#8a8a8a');
        rows.forEach((d,i)=>{
            const y=firstY+i*32;
            if(i%2===0) svg.append('rect').attr('x',10).attr('y',y-14).attr('width',W-20).attr('height',28).attr('fill','#f4f7fb');
            text(svg,14,y,d.label.length>31?d.label.slice(0,30)+'…':d.label).append('title').text(d.label);
            d.counts.forEach((v,j)=>text(svg,[238,302,367,431][j],y,String(v),'end'));
            text(svg,right+110,y,ciText(d),'middle');text(svg,right+218,y,fmtWeight(d.weight)+'%','end');
            d.rob.forEach((v,j)=>{
                const [color,symbol,label]=judgment(v),cx=right+262+j*34;
                const g=svg.append('g');g.append('circle').attr('cx',cx).attr('cy',y).attr('r',10).attr('fill',color);
                text(g,cx,y,symbol,'middle',700,'white');
                g.append('title').text(`${rob[j]}: ${v==null?'No information':String(v)} (${label})`);
            });
        });
        const marks=svg.append('g').attr('clip-path',`url(#${clipId})`);
        marks.append('line').attr('class','no-effect-line').attr('x1',x(1)).attr('x2',x(1)).attr('y1',100).attr('y2',pooledY+20)
            .attr('stroke','#94a3b8').attr('stroke-dasharray','2 4')
            .append('title').text('No effect: RR = 1');
        marks.append('line').attr('class','pooled-effect-line').attr('x1',x(payload.pooled.rr)).attr('x2',x(payload.pooled.rr)).attr('y1',100).attr('y2',pooledY+20)
            .attr('stroke','#ed7953').attr('stroke-dasharray','5 4')
            .append('title').text(`Pooled RR: ${format(payload.pooled.rr)}`);
        const maxWeight=d3.max(rows,d=>d.weight);
        rows.forEach((d,i)=>{
            const y=firstY+i*32,g=marks.append('g'),size=18*Math.sqrt(d.weight/maxWeight);
            g.append('line').attr('x1',x(d.lower)).attr('x2',x(d.upper)).attr('y1',y).attr('y2',y).attr('stroke','#3e6da9').attr('stroke-width',1.8);
            [d.lower,d.upper].forEach(v=>g.append('line').attr('x1',x(v)).attr('x2',x(v)).attr('y1',y-4).attr('y2',y+4).attr('stroke','#3e6da9'));
            g.append('rect').attr('x',x(d.rr)-size/2).attr('y',y-size/2).attr('width',size).attr('height',size).attr('fill','#3e6da9');
            g.append('title').text(`${d.label}: ${ciText(d)}; weight ${fmtWeight(d.weight)}%`);
        });
        svg.append('line').attr('x1',10).attr('x2',W-10).attr('y1',pooledY-23).attr('y2',pooledY-23).attr('stroke','#8a8a8a');
        text(svg,14,pooledY,'Random-effects model [REML]','start',600);
        totals.forEach((v,j)=>text(svg,[238,302,367,431][j],pooledY,String(v),'end',600));
        const p=payload.pooled;
        const prediction=marks.append('g').attr('class','prediction-interval');
        prediction.append('line').attr('x1',x(p.piLower)).attr('x2',x(p.piUpper))
            .attr('y1',pooledY).attr('y2',pooledY).attr('stroke','#ed7953')
            .attr('stroke-width',1.6).attr('stroke-dasharray','5 3');
        [p.piLower,p.piUpper].forEach(value=>prediction.append('line')
            .attr('x1',x(value)).attr('x2',x(value)).attr('y1',pooledY-5).attr('y2',pooledY+5)
            .attr('stroke','#ed7953').attr('stroke-width',1.6));
        prediction.append('title').text(`${payload.confidence.replace('CI','PI')}: [${format(p.piLower)}, ${format(p.piUpper)}]`);
        marks.append('polygon').attr('class','pooled-diamond').attr('points',`${x(p.lower)},${pooledY} ${x(p.rr)},${pooledY-10} ${x(p.upper)},${pooledY} ${x(p.rr)},${pooledY+10}`)
            .attr('fill','#ed7953').append('title').text(`Pooled RR: ${ciText(p)}`);
        text(svg,right+110,pooledY,ciText(p),'middle',600);text(svg,right+218,pooledY,'100%','end',600);
        const h=payload.heterogeneity;
        text(svg,14,pooledY+27,`Heterogeneity: τ² = ${h.tau2.toFixed(4)}, I² = ${h.i2.toFixed(2)}%, H² = ${h.h2.toFixed(3)}, Q(${h.df}) = ${h.q.toFixed(3)}, p ${h.p<.001?'< .001':'= '+h.p.toFixed(3)}`);
        text(svg,14,pooledY+44,`${payload.confidence.replace('CI','prediction interval')}: [${format(p.piLower)}, ${format(p.piUpper)}]`);
        const ticks=[];for(let power=Math.ceil(Math.log2(x.domain()[0]));power<=Math.floor(Math.log2(x.domain()[1]));power++)ticks.push(2**power);
        svg.append('g').attr('transform',`translate(0,${axisY})`).call(d3.axisBottom(x).tickValues(ticks).tickFormat(d3.format('.3~g')));
        text(svg,(left+right)/2,axisY+37,'Risk ratio (logarithmic axis)','middle');
    }
    // Resize only the SVG viewport: keep the viewBox, coordinates and statistical domain fixed.
    function updateZoom() {
        const slider=root.querySelector('.zoom'), zoom=Number(slider.value);
        svg.attr('width',W*zoom).attr('height',H*zoom);
        root.querySelector('.zoom-marker').style.left=
            (8+(110-16)*(zoom-Number(slider.min))/(Number(slider.max)-Number(slider.min)))+'px';
        root.querySelector('.zoom-value').textContent=Math.round(zoom*100)+'%';
        slider.setAttribute('aria-valuetext',Math.round(zoom*100)+' percent');
    }
    root.querySelector('.zoom').addEventListener('input',updateZoom);
    root.querySelector('button').addEventListener('click',()=>{root.querySelector('.zoom').value=1;updateZoom();});
    if(!rob.length) root.querySelector('.legend').hidden=true;
    draw();
    updateZoom();
})();
</script>
'''
html = html.replace('__ROOT__', root_id).replace('__PAYLOAD__', encoded)
mzpjShowHtml(html, name='bcg_forest', title='BCG vaccine — forest plot')
print(f'Analyzed {k} studies using REML. Pooled RR = {math.exp(estimate):.4f}; '
      f'{confidence_label}: [{math.exp(ci_low):.4f}, {math.exp(ci_high):.4f}].')
