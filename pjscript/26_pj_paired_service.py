# Load this file with Service script / Browse..., then load script 27 in the editor.
# Both Python interpreters are supported. SciPy is required; pandas/matplotlib are not.
# This file defines reusable services only; the editor chooses which results to display.
import json
import math
import statistics
import uuid
from scipy.stats import t


def mzpjDemoPairedSummary(dataset, group='group', before='before', after='after', identifier='participant_id'):
    """Summarize complete pairs, with Student-t confidence intervals for mean change."""
    required = [group, before, after]
    missing = [name for name in required if name not in dataset]
    if missing:
        raise ValueError('Required dataset columns: ' + ', '.join(missing) + '.')
    count = len(dataset[group])
    if any(len(values) != count for values in dataset.values()):
        raise ValueError('Dataset columns must have the same number of rows.')
    participants = []
    for row in range(count):
        label, initial, final = (dataset[name][row] for name in required)
        values = (initial, final)
        if label is None or (isinstance(label, float) and math.isnan(label)) or any(
                value is None or (isinstance(value, (int, float)) and math.isnan(value)) for value in values):
            continue
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) for value in values):
            raise ValueError(f'Row {row + 1}: before and after must be finite numeric values or missing.')
        participants.append({'row': row + 1, 'group': str(label),
                             'label': str(dataset[identifier][row]) if identifier in dataset and dataset[identifier][row] is not None else f'Row {row + 1}',
                             'before': float(initial), 'after': float(final), 'change': float(final - initial)})
    if not participants:
        raise ValueError('At least one complete pair and a non-missing group are required.')
    summaries = []
    for label in sorted({row['group'] for row in participants}, key=str.casefold):
        pairs = [row for row in participants if row['group'] == label]
        changes = [row['change'] for row in pairs]
        n, mean = len(pairs), statistics.mean(changes)
        sd = statistics.stdev(changes) if n > 1 else None
        margin = float(t.ppf(.975, n - 1)) * sd / math.sqrt(n) if sd is not None else None
        summaries.append({'Group': label, 'N': n,
                          'Before': statistics.mean(row['before'] for row in pairs),
                          'After': statistics.mean(row['after'] for row in pairs),
                          'Change': mean, 'SD change': sd,
                          'Lower': mean - margin if margin is not None else None,
                          'Upper': mean + margin if margin is not None else None})
    return {'participants': participants, 'groups': summaries, 'total': count,
            'included': len(participants), 'excluded': count - len(participants)}


def mzpjDemoPairedDashboard(summary, d3_source):
    """Build an offline D3 view with fixed scales, linked cases and group controls."""
    if not d3_source:
        raise RuntimeError('The bundled D3 library is unavailable.')
    encoded = json.dumps(summary, ensure_ascii=True, allow_nan=False)
    encoded = encoded.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    root_id = 'paired_' + uuid.uuid4().hex
    html = d3_source + r'''
<style>
.mzpj-paired{font:13px/1.5 sans-serif;color:#334155;max-width:100%}
.mzpj-paired summary{cursor:pointer;color:#3e6da9;font-weight:600;padding:10px 0;border-block:1px solid #d9e4f1;list-style:none}
.mzpj-paired summary::-webkit-details-marker{display:none}
.mzpj-paired summary svg{vertical-align:-2px;margin-right:9px}
.mzpj-paired[open]>summary .vertical{display:none}
.mzpj-paired .tools,.mzpj-paired .groups{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin:12px 0}
.mzpj-paired button{font:inherit;background:white;border:1px solid #b9cce3;border-radius:5px;padding:5px 10px;cursor:pointer;color:#3e6da9}
.mzpj-paired button[aria-pressed=false]{opacity:.45}
.mzpj-paired .groups button::before{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--group-color);margin-right:7px}
.mzpj-paired .viewport{max-width:100%;max-height:570px;overflow:auto}
.mzpj-paired .inspect{border-left:3px solid #3e6da9;background:#f3f7fc;min-height:43px;padding:11px 14px;white-space:pre-wrap}
.mzpj-paired .note{color:#64748b;font-size:12px}
.mzpj-paired .case,.mzpj-paired .interval{cursor:pointer;outline:none}
.mzpj-paired .case:focus,.mzpj-paired .interval:focus{stroke:#1e293b;stroke-width:3}
</style>
<details class="mzpj-paired" id="__ROOT__" open>
<summary><svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7h10" stroke="currentColor" stroke-width="1.5"/><path class="vertical" d="M7 2v10" stroke="currentColor" stroke-width="1.5"/></svg>Paired-change explorer — individuals and uncertainty</summary>
<div class="groups" role="group" aria-label="Visible groups"></div>
<div class="tools"><label><input class="individuals" type="checkbox" checked> Show individual pairs</label><button class="reset" type="button">Reset view</button><span class="count"></span></div>
<div class="viewport" tabindex="0" aria-label="Scrollable paired-change plot"></div>
<div class="inspect" role="status" aria-live="polite">Hover or focus a participant or a mean for details. Click or press Enter to pin a participant.</div>
<p class="note">Left: paired measurements; thick segments connect group means calculated from complete pairs. Right: individual changes and group mean change with a 95% Student-t CI. The dashed line marks zero change. Intervals describe within-group mean changes, not differences between groups. Missing pairs are excluded from both panels and tables.</p>
<p class="note">Group controls change visibility only. Axes, estimates and intervals stay fixed. Transitions respect reduced-motion preferences. Use Tab/Enter for keyboard inspection; Escape clears a pinned case. Fictional data, with no causal or treatment-effect interpretation.</p>
</details><script>
(() => {
const root=document.getElementById('__ROOT__'), payload=__PAYLOAD__, rows=payload.participants, groups=payload.groups;
const duration=window.matchMedia('(prefers-reduced-motion: reduce)').matches?0:280;
const colors=['#3e6da9','#d48132','#258478','#8b6ba6','#a85c70'];
const color=d3.scaleOrdinal().domain(groups.map(d=>d.Group)).range(colors);
const active=new Set(groups.map(d=>d.Group));let pinned=null;
const W=Math.max(980,groups.length*155+500),H=Math.max(440,groups.length*70+200),top=85,bottom=H-100;
const split=W*.54, right=W-35;
const svg=d3.select(root.querySelector('.viewport')).append('svg').attr('width',W).attr('height',H).attr('viewBox',`0 0 ${W} ${H}`).attr('role','img').attr('aria-label','Linked before-after measurements and mean change intervals');
const fmt=d3.format('.2f');
function padded(values){let [lo,hi]=d3.extent(values);const pad=(hi-lo||1)*.12;return [lo-pad,hi+pad];}
const y=d3.scaleLinear().domain(padded(rows.flatMap(d=>[d.before,d.after]))).nice().range([bottom,top]);
const xGroup=d3.scalePoint().domain(groups.map(d=>d.Group)).range([135,split-80]);
const xChange=d3.scaleLinear().domain(padded([0,...rows.map(d=>d.change),...groups.flatMap(d=>[d.Lower,d.Upper]).filter(d=>d!==null)])).nice().range([split+125,right]);
const yGroup=d3.scalePoint().domain(groups.map(d=>d.Group)).range([top+45,bottom-40]);
function text(x,y,value,anchor='middle',size=12){return svg.append('text').attr('x',x).attr('y',y).attr('fill','#334155').attr('text-anchor',anchor).attr('font-size',size).text(value);}
text(split/2,28,'Before → after', 'middle',15);text((split+right)/2,28,'Change = after − before','middle',15);
text(60,62,'Score','start',11);
svg.append('g').attr('transform','translate(60,0)').call(d3.axisLeft(y).ticks(6));
svg.append('g').attr('transform','translate(60,0)').call(d3.axisLeft(y).ticks(6).tickSize(-(split-100)).tickFormat('')).attr('color','#e8eef5').select('.domain').remove();
svg.append('g').attr('transform',`translate(0,${bottom+15})`).call(d3.axisBottom(xChange).ticks(5));
text((split+125+right)/2,bottom+57,'Change in score');
svg.append('line').attr('class','zero-line').attr('x1',xChange(0)).attr('x2',xChange(0)).attr('y1',top).attr('y2',bottom).attr('stroke','#94a3b8').attr('stroke-dasharray','5 4');
const groupLayers=new Map(),meanMarks=[];
for(const group of groups){
 const label=group.Group, gx=xGroup(label),gy=yGroup(label), layer=svg.append('g').attr('class','group-layer');groupLayers.set(label,layer);
 const groupRows=rows.filter(d=>d.group===label);
 text(gx,bottom+30,label,'middle',11).attr('fill',color(label));
 text(gx-25,top-10,'Before','middle',10);text(gx+25,top-10,'After','middle',10);
 text(split+110,gy-26,label,'end',11).attr('fill',color(label));
 layer.selectAll('line.pair').data(groupRows).join('line').attr('class','pair').attr('data-row',d=>d.row)
  .attr('x1',gx-25).attr('x2',gx+25).attr('y1',d=>y(d.before)).attr('y2',d=>y(d.after)).attr('stroke',color(label)).attr('stroke-opacity',.18).attr('stroke-width',1.2);
 const cases=layer.append('g').attr('class','individual-layer');
 for(const time of ['before','after'])cases.selectAll(`circle.${time}`).data(groupRows).join('circle').attr('class',`case ${time}`).attr('data-row',d=>d.row)
  .attr('cx',gx+(time==='before'?-25:25)).attr('cy',d=>y(d[time])).attr('r',3.3).attr('fill',color(label)).attr('fill-opacity',.55).attr('stroke','white');
 cases.selectAll('circle.change').data(groupRows).join('circle').attr('class','case change').attr('data-row',d=>d.row)
  .attr('cx',d=>xChange(d.change)).attr('cy',d=>gy+(((d.row*17)%23)/22-.5)*38).attr('r',3.8).attr('fill',color(label)).attr('fill-opacity',.55).attr('stroke','white');
 layer.selectAll('.case').attr('tabindex',0).attr('role','button').attr('aria-label',d=>`${d.label}, ${d.group}: before ${fmt(d.before)}, after ${fmt(d.after)}, change ${fmt(d.change)}. Press Enter to select.`)
  .on('pointerenter',(_,d)=>inspectCase(d)).on('pointerleave',()=>inspectCase(pinned)).on('focus',(_,d)=>inspectCase(d)).on('blur',()=>inspectCase(pinned))
  .on('click',(_,d)=>pin(d)).on('keydown',(event,d)=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();pin(d);}if(event.key==='Escape'){pinned=null;inspectCase(null);}});
 layer.append('line').attr('x1',gx-25).attr('x2',gx+25).attr('y1',y(group.Before)).attr('y2',y(group.After)).attr('stroke',color(label)).attr('stroke-width',4);
 for(const time of ['Before','After'])layer.append('circle').attr('cx',gx+(time==='Before'?-25:25)).attr('cy',y(group[time])).attr('r',5.5).attr('fill',color(label)).attr('stroke','white');
 const mean=layer.append('g').attr('class','interval').attr('tabindex',0).attr('role','img');meanMarks.push(mean);
 if(group.Lower!==null){mean.append('line').attr('class','ci').attr('x1',xChange(group.Lower)).attr('x2',xChange(group.Upper)).attr('y1',gy).attr('y2',gy).attr('stroke',color(label)).attr('stroke-width',3);
  for(const value of [group.Lower,group.Upper])mean.append('line').attr('x1',xChange(value)).attr('x2',xChange(value)).attr('y1',gy-7).attr('y2',gy+7).attr('stroke',color(label)).attr('stroke-width',2);}
 mean.append('circle').attr('class','mean').attr('cx',xChange(group.Change)).attr('cy',gy).attr('r',6).attr('fill',color(label)).attr('stroke','white').attr('stroke-width',2);
 const info=`${label}: ${group.N} complete pairs · mean change ${fmt(group.Change)} · 95% CI ${group.Lower===null?'undefined (N < 2)':`[${fmt(group.Lower)}, ${fmt(group.Upper)}]`}`;
 mean.attr('aria-label',info).on('pointerenter',()=>{inspectCase(null);root.querySelector('.inspect').textContent=info;}).on('pointerleave',()=>inspectCase(pinned)).on('focus',()=>{root.querySelector('.inspect').textContent=info;}).on('blur',()=>inspectCase(pinned));
}
function pin(d){pinned=pinned?.row===d.row?null:d;inspectCase(pinned);}
function inspectCase(d){
 svg.selectAll('.case').attr('r',v=>d&&v.row===d.row?6:3.5).attr('stroke',v=>d&&v.row===d.row?'#1e293b':'white').attr('stroke-width',v=>d&&v.row===d.row?2:1);
 svg.selectAll('.pair').attr('stroke-opacity',v=>d&&v.row===d.row?1:.18).attr('stroke-width',v=>d&&v.row===d.row?3:1.2);
 root.querySelector('.inspect').textContent=d?`${pinned?.row===d.row?'Selected':'Participant'}: ${d.label} · ${d.group} · dataset row ${d.row}\nBefore ${fmt(d.before)} → after ${fmt(d.after)} · change ${fmt(d.change)}`:'Hover or focus a participant or a mean for details. Click or press Enter to pin a participant.';
}
function update(){const individuals=root.querySelector('.individuals').checked;
 for(const [name,layer] of groupLayers){const visible=active.has(name);layer.interrupt().attr('visibility',visible?null:'hidden').attr('aria-hidden',visible?'false':'true');
  layer.selectAll('.case').attr('tabindex',visible&&individuals?0:-1);layer.selectAll('.interval').attr('tabindex',visible?0:-1);
  if(visible)layer.attr('opacity',.25).transition().duration(duration).attr('opacity',1);
  layer.selectAll('.individual-layer,.pair').attr('visibility',individuals?null:'hidden');}
 if(pinned&&(!active.has(pinned.group)||!individuals)){pinned=null;inspectCase(null);}
 root.querySelector('.count').textContent=`${rows.filter(d=>active.has(d.group)).length} of ${payload.included} complete pairs visible · ${payload.excluded} incomplete rows excluded`;
}
const buttons=d3.select(root.querySelector('.groups')).selectAll('button').data(groups).join('button').attr('type','button')
 .style('--group-color',d=>color(d.Group)).attr('aria-pressed','true').text(d=>`${d.Group} (N = ${d.N})`)
 .on('click',function(_,d){active.has(d.Group)?active.delete(d.Group):active.add(d.Group);d3.select(this).attr('aria-pressed',String(active.has(d.Group)));update();});
root.querySelector('.individuals').addEventListener('change',update);
root.querySelector('.reset').addEventListener('click',()=>{groups.forEach(d=>active.add(d.Group));buttons.attr('aria-pressed','true');root.querySelector('.individuals').checked=true;pinned=null;inspectCase(null);update();});
update();
})();</script>
'''
    return html.replace('__ROOT__', root_id).replace('__PAYLOAD__', encoded)
