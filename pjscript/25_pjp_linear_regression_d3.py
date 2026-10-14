# Run in Pjp. Select only final_score, study_hours and baseline for the model.
# participant_id is optional: it labels points and is never a statistical predictor.
# Both Python interpreters are supported; NumPy, SciPy and bundled D3 are required.
# All comments and results are editable teaching material; observations come from data.
import json
import math
import uuid
import numpy as np
from scipy.stats import t, f

OUTCOME = 'final_score'
PREDICTORS = ['study_hours', 'baseline']
# Optional label column; use dataset row numbers automatically when it is not selected.
ID = 'participant_id'
# Change False to True, then Run, to return four diagnostic columns through Pjp.
# Change back to False and Run to remove columns created by this analysis.
WRITE_COLUMNS = False
required = [OUTCOME] + PREDICTORS
if not PREDICTORS or len(set(required)) != len(required):
    raise ValueError('Choose distinct outcome and predictor columns, with at least one predictor.')
missing = [name for name in required if name not in data]
if missing:
    raise ValueError('Select these variables in Pjp: ' + ', '.join(missing) + '.')
if not d3_script:
    raise RuntimeError('The bundled D3 library is unavailable.')
row_count = len(data[OUTCOME])
if any(len(values) != row_count for values in data.values()):
    raise ValueError('Selected columns must have the same number of rows.')

included, observations = [], []
for row in range(row_count):
    values = [data[name][row] for name in required]
    if any(value is None or (isinstance(value, (int, float)) and math.isnan(value)) for value in values):
        continue
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) for value in values):
        raise ValueError(f'Row {row + 1}: outcome and predictors must be finite numeric values or missing.')
    included.append(row)
    observations.append(values)

n, p = len(observations), len(PREDICTORS) + 1
if n <= p:
    raise ValueError('More complete observations than model coefficients are required.')
values = np.asarray(observations, dtype=float)
y = values[:, 0]
X = np.column_stack([np.ones(n), values[:, 1:]])
beta, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
if rank != p:
    raise ValueError('The model is rank deficient. Remove constant or collinear predictors.')
Q, R = np.linalg.qr(X, mode='reduced')
inverse_R = np.linalg.solve(R, np.eye(p))
fitted = X @ beta
residual = y - fitted
sse = float(residual @ residual)
sst = float(np.sum((y - np.mean(y)) ** 2))
if sst <= np.finfo(float).eps * max(1, float(y @ y)):
    raise ValueError('The outcome has no usable variation.')
if sse <= np.finfo(float).eps * max(1, sst):
    raise ValueError('The model fits almost perfectly; residual-based inference is undefined.')
df_error = n - p
mse = sse / df_error
se = np.sqrt(np.diag(inverse_R @ inverse_R.T) * mse)
statistics = beta / se
p_values = 2 * t.sf(np.abs(statistics), df_error)
critical = float(t.ppf(.975, df_error))
r2 = 1 - sse / sst
adjusted_r2 = 1 - (1 - r2) * (n - 1) / df_error
f_statistic = max(0, (sst - sse) / (p - 1) / mse)
leverage = np.sum(Q ** 2, axis=1)
# Internally standardized residuals are undefined when leverage is effectively one.
standardized = [float(residual[i] / math.sqrt(mse * (1 - leverage[i])))
                if 1 - leverage[i] > 1e-12 else None for i in range(n)]
model = [{'N': n, 'R squared': r2, 'Adjusted R squared': adjusted_r2,
          'RMSE': math.sqrt(mse), 'F': f_statistic, 'df1': p - 1, 'df2': df_error,
          'p': float(f.sf(f_statistic, p - 1, df_error))}]
coefficients = [{'Term': name, 'Estimate': float(beta[i]), 'SE': float(se[i]),
                 't': float(statistics[i]), 'df': df_error, 'p': float(p_values[i]),
                 'Lower': float(beta[i] - critical * se[i]),
                 'Upper': float(beta[i] + critical * se[i])}
                for i, name in enumerate(['Intercept'] + PREDICTORS)]
mzpjShowTable(model, name='ols_fit', title='Linear regression — model fit',
              formats={'p': 'pvalue'}, notes=[
                  'Synthetic teaching data. Ordinary least squares with an intercept.',
                  f'{row_count - n} rows excluded by complete-case analysis of outcome and predictors.',
                  'Inference assumes independent errors with constant variance and normality for exact t/F tests.'])
mzpjShowTable(coefficients, name='ols_coefficients', title='Regression coefficients',
              formats={'p': 'pvalue'}, column_groups={'Lower': '95% CI', 'Upper': '95% CI'},
              notes='Unstandardized coefficients; associations do not establish causation.')

points = [{'index': i, 'row': row + 1,
           'label': str(data[ID][row]) if ID in data and data[ID][row] is not None else f'Row {row + 1}',
           'observed': float(y[i]), 'fitted': float(fitted[i]), 'residual': float(residual[i]),
           'standardized': standardized[i], 'leverage': float(leverage[i])}
          for i, row in enumerate(included)]
if WRITE_COLUMNS:
    for name, source in [('pj_fitted', fitted), ('pj_residual', residual),
                         ('pj_standardized_residual', standardized), ('pj_leverage', leverage)]:
        output = [None] * row_count
        for i, row in enumerate(included):
            output[row] = None if source[i] is None else float(source[i])
        data[name] = output

payload = json.dumps({'points': points, 'n': n, 'r2': r2}, allow_nan=False, ensure_ascii=True)
payload = payload.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
root_id = 'ols_' + uuid.uuid4().hex
html = d3_script + r'''
<style>
.mzpj-ols{font:13px/1.5 sans-serif;color:#334155;max-width:100%}
.mzpj-ols summary{cursor:pointer;color:#3e6da9;font-weight:600;padding:9px 0;border-block:1px solid #d9e4f1}
.mzpj-ols .tools{display:flex;gap:14px;flex-wrap:wrap;align-items:center;margin:15px 0}
.mzpj-ols button,.mzpj-ols select{font:inherit;color:#3e6da9;background:white;border:1px solid #b9cce3;border-radius:5px;padding:4px 9px}
.mzpj-ols .viewport{overflow:auto;max-width:100%;max-height:540px}
.mzpj-ols .inspect{border-left:3px solid #3e6da9;background:#f3f7fc;padding:10px 14px;min-height:40px;white-space:pre-wrap}
.mzpj-ols .note{color:#64748b;font-size:12px}
.mzpj-ols circle.point{cursor:pointer;outline:none}
.mzpj-ols circle.point:focus{stroke:#1e293b;stroke-width:3}
</style>
<details class="mzpj-ols" id="__ROOT__" open><summary>Regression explorer — linked diagnostics</summary>
<div class="tools"><label>Residual scale <select class="mode"><option value="residual">Raw residuals</option><option value="standardized">Internally standardized</option></select></label>
<label><input class="references" type="checkbox" checked> Reference lines</label><button type="button">Clear selection</button></div>
<div class="viewport" tabindex="0" aria-label="Scrollable regression diagnostics"></div>
<div class="inspect" role="status" aria-live="polite">Hover or focus a point for details. Click or press Enter to pin it in both panels.</div>
<p class="note">Each point is one complete case. Left: observed versus fitted values, with the identity line. Right: residuals versus fitted values, with zero and (when standardized) ±2 guides. Guides are visual aids, not automatic outlier tests. Selection does not refit the model.</p>
</details><script>
(() => {
const root=document.getElementById('__ROOT__'), payload=__PAYLOAD__, rows=payload.points;
const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches, duration=reduced?0:240;
const W=960,H=400,top=60,bottom=325, left=[65,555],right=[435,925];
const svg=d3.select(root.querySelector('.viewport')).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`).attr('role','img').attr('aria-label','Linked observed and residual plots');
const fmt=d3.format('.3f');
function domain(values){let [lo,hi]=d3.extent(values);const pad=(hi-lo||1)*.08;return [lo-pad,hi+pad];}
const common=domain(rows.flatMap(d=>[d.observed,d.fitted]));
const x0=d3.scaleLinear().domain(common).range([left[0],right[0]]),y0=d3.scaleLinear().domain(common).range([bottom,top]);
const x1=d3.scaleLinear().domain(domain(rows.map(d=>d.fitted))).range([left[1],right[1]]);
const domains={residual:domain([0,...rows.map(d=>d.residual)]),standardized:domain([-2,2,...rows.filter(d=>d.standardized!==null).map(d=>d.standardized)])};
const y1=d3.scaleLinear().domain(domains.residual).range([bottom,top]);
function text(x,y,value,size=12,anchor='middle'){return svg.append('text').attr('x',x).attr('y',y).attr('fill','#334155').attr('font-size',size).attr('text-anchor',anchor).text(value);}
text(250,25,'Observed versus fitted',14);text(740,25,'Residuals versus fitted',14);
for(let i=0;i<2;i++){const scale=i?x1:x0;svg.append('g').attr('transform',`translate(0,${bottom})`).call(d3.axisBottom(scale).ticks(5));text((left[i]+right[i])/2,370,'Fitted value');}
svg.append('g').attr('transform',`translate(${left[0]},0)`).call(d3.axisLeft(y0).ticks(5));
const residualAxis=svg.append('g').attr('transform',`translate(${left[1]},0)`).call(d3.axisLeft(y1).ticks(5));
text(left[0],46,'Observed',11,'start');const residualLabel=text(left[1],46,'Raw residual',11,'start');
const refs=svg.append('g').attr('class','refs');
refs.append('line').attr('x1',x0(common[0])).attr('x2',x0(common[1])).attr('y1',y0(common[0])).attr('y2',y0(common[1])).attr('stroke','#94a3b8').attr('stroke-dasharray','5 4');
const guides=refs.append('g');
let pinned=null, mode='residual';
const layers=[svg.append('g'),svg.append('g')];
const dots=layers.map((layer,panel)=>layer.selectAll('circle').data(rows).join('circle').attr('class','point').attr('data-index',d=>d.index)
 .attr('cx',d=>panel?x1(d.fitted):x0(d.fitted)).attr('cy',d=>panel?y1(d.residual):y0(d.observed)).attr('r',4.3)
 .attr('fill','#3e6da9').attr('fill-opacity',.7).attr('stroke','white').attr('tabindex',0).attr('role','button')
 .attr('aria-label',d=>`${d.label}, observed ${fmt(d.observed)}, fitted ${fmt(d.fitted)}, residual ${fmt(d.residual)}. Press Enter to select.`)
 .on('pointerenter',(_,d)=>inspect(d)).on('pointerleave',()=>inspect(pinned)).on('focus',(_,d)=>inspect(d))
 .on('blur',()=>inspect(pinned)).on('click',(_,d)=>{pinned=pinned?.index===d.index?null:d;inspect(pinned);})
 .on('keydown',(event,d)=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();pinned=pinned?.index===d.index?null:d;inspect(pinned);}if(event.key==='Escape'){pinned=null;inspect(null);}}));
function inspect(d){
 for(const selection of dots)selection.attr('r',v=>d&&v.index===d.index?7:4.3).attr('fill',v=>d&&v.index===d.index?'#ed7953':'#3e6da9').attr('fill-opacity',v=>d&&v.index!==d.index?.35:.8);
 root.querySelector('.inspect').textContent=d?`${pinned?.index===d.index?'Selected':'Case'}: ${d.label} · dataset row ${d.row}\nObserved ${fmt(d.observed)} · fitted ${fmt(d.fitted)} · residual ${fmt(d.residual)} · standardized ${d.standardized===null?'undefined':fmt(d.standardized)} · leverage ${fmt(d.leverage)}`:'Hover or focus a point for details. Click or press Enter to pin it in both panels.';
}
function update(){mode=root.querySelector('.mode').value;y1.domain(domains[mode]);
 residualAxis.transition().duration(duration).call(d3.axisLeft(y1).ticks(5));
 residualLabel.text(mode==='residual'?'Raw residual':'Internally standardized residual');
 dots[1].attr('visibility',d=>d[mode]===null?'hidden':null).transition().duration(duration).attr('cy',d=>y1(d[mode]??0));
 const values=mode==='residual'?[0]:[-2,0,2];guides.selectAll('line').data(values,d=>d).join('line').attr('x1',left[1]).attr('x2',right[1]).attr('stroke',d=>d===0?'#ed7953':'#cbd5e1').attr('stroke-dasharray','5 4').transition().duration(duration).attr('y1',d=>y1(d)).attr('y2',d=>y1(d));
}
root.querySelector('.mode').addEventListener('change',update);
root.querySelector('.references').addEventListener('change',event=>refs.attr('visibility',event.target.checked?null:'hidden'));
root.querySelector('button').addEventListener('click',()=>{pinned=null;inspect(null);});
update();
})();</script>
'''
html = html.replace('__ROOT__', root_id).replace('__PAYLOAD__', payload)
mzpjShowHtml(html, name='ols_diagnostics', title='Linear regression — interactive diagnostics')
print(f'OLS: {n} complete cases, {row_count - n} excluded; R squared = {r2:.4f}.')
