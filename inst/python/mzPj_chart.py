# Ponte Chart.js: configurazioni JSON, nessuna installazione nel Python scelto.
def _pj_chart_json(value, path='configuration'):
    from collections.abc import Mapping
    from numbers import Integral, Real
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, Integral):
        if abs(value) > 9007199254740991:
            raise ValueError(f'mzpjShowChart(): {path} exceeds JavaScript safe integer precision.')
        return int(value)
    if isinstance(value, Real):
        value = float(value)
        if not math.isfinite(value):
            raise ValueError(f'mzpjShowChart(): {path} must be finite; use None for a missing value.')
        return value
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise TypeError(f'mzpjShowChart(): {path} keys must be strings.')
        if any(key in ('__proto__', 'constructor', 'prototype') for key in value):
            raise ValueError('mzpjShowChart(): reserved JavaScript configuration key.')
        return {key: _pj_chart_json(item, f'{path}.{key}') for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_pj_chart_json(item, f'{path}[{index}]') for index, item in enumerate(value)]
    if hasattr(value, 'tolist'):
        return _pj_chart_json(value.tolist(), path)
    raise TypeError(f'mzpjShowChart(): {path} must contain JSON values, lists or NumPy arrays; callbacks are not supported.')


def _pj_show_chart(chart_type, datasets, *, labels=None, name=None, title=None,
                   options=None, width=None, height=None, accordion=True, expanded=True,
                   static=False, floating_legend=None):
    """Configura un grafico Chart.js autonomo, con dati numerici gia calcolati."""
    import html
    import uuid
    from numbers import Integral, Real
    types = ('bar', 'line', 'scatter', 'bubble', 'pie', 'doughnut', 'radar', 'polarArea')
    if chart_type not in types:
        raise ValueError('mzpjShowChart(): chart_type must be one of: ' + ', '.join(types) + '.')
    datasets = _pj_chart_json(datasets, 'datasets')
    labels = _pj_chart_json(labels, 'labels')
    options = _pj_chart_json({} if options is None else options, 'options')
    if not isinstance(options, dict):
        raise TypeError('mzpjShowChart(): options must be a dictionary.')
    if 'plugins' in options and not isinstance(options['plugins'], dict):
        raise TypeError('mzpjShowChart(): options.plugins must be a dictionary; disable individual plugins by name.')
    if labels is not None and not isinstance(labels, list):
        raise TypeError('mzpjShowChart(): labels must be a list.')
    if not isinstance(datasets, list) or not datasets:
        raise ValueError('mzpjShowChart(): datasets must be a non-empty list of dictionaries.')
    valid = 0
    for dataset in datasets:
        if not isinstance(dataset, dict) or not isinstance(dataset.get('data'), list):
            raise TypeError('mzpjShowChart(): each dataset needs a data list.')
        kind = dataset.get('type', chart_type)
        if kind not in types:
            raise ValueError('mzpjShowChart(): unsupported dataset type.')
        if kind not in ('scatter', 'bubble') and labels is not None and len(dataset['data']) != len(labels):
            raise ValueError('mzpjShowChart(): labels and each categorical dataset must have the same length.')
        for point in dataset['data']:
            if point is None:
                continue
            if kind in ('scatter', 'bubble') or (kind == 'line' and isinstance(point, dict)):
                if not isinstance(point, dict) or any(isinstance(point.get(axis), bool) or
                        not isinstance(point.get(axis), Real) for axis in ('x', 'y')):
                    raise ValueError('mzpjShowChart(): coordinate points need finite numeric x and y.')
                if kind == 'bubble' and (isinstance(point.get('r'), bool) or
                        not isinstance(point.get('r'), Real) or point['r'] < 0):
                    raise ValueError('mzpjShowChart(): bubble points need a non-negative numeric r.')
            elif isinstance(point, bool) or not isinstance(point, Real):
                raise ValueError('mzpjShowChart(): categorical data must contain numbers or None.')
            valid += 1
    if not valid:
        raise ValueError('mzpjShowChart(): at least one non-missing observation is required.')
    if not isinstance(accordion, bool) or not isinstance(expanded, bool):
        raise TypeError('mzpjShowChart(): accordion and expanded must be True or False.')
    if not isinstance(static, bool):
        raise TypeError('mzpjShowChart(): static must be True or False.')
    legend = None
    if floating_legend is not None and floating_legend is not False:
        legend = {} if floating_legend is True else _pj_chart_json(floating_legend, 'floating_legend')
        if not isinstance(legend, dict):
            raise TypeError('mzpjShowChart(): floating_legend must be True, False, None or a dictionary.')
        if set(legend) - {'title', 'text', 'items', 'collapsed'}:
            raise ValueError('mzpjShowChart(): floating_legend supports title, text, items and collapsed.')
        if any(key in legend and not isinstance(legend[key], str) for key in ('title', 'text')):
            raise TypeError('mzpjShowChart(): floating legend title/text must be strings.')
        if 'collapsed' in legend and not isinstance(legend['collapsed'], bool):
            raise TypeError('mzpjShowChart(): floating legend collapsed must be True or False.')
        if 'items' in legend:
            if not isinstance(legend['items'], list):
                raise TypeError('mzpjShowChart(): floating legend items must be a list.')
            for item in legend['items']:
                if not isinstance(item, dict) or set(item) - {'label', 'text', 'color', 'dataset'}:
                    raise ValueError('mzpjShowChart(): legend items support label, text, color and dataset.')
                if not isinstance(item.get('label'), str):
                    raise TypeError('mzpjShowChart(): each floating legend item needs a text label.')
                if any(key in item and not isinstance(item[key], str) for key in ('text', 'color')):
                    raise TypeError('mzpjShowChart(): legend item text/color must be strings.')
                index = item.get('dataset')
                if index is not None and (isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(datasets)):
                    raise ValueError('mzpjShowChart(): legend dataset indexes start at zero and must reference an existing series.')
    if not accordion and not expanded:
        raise ValueError('mzpjShowChart(): expanded=False requires accordion=True.')
    dimensions = []
    for key, value, default, minimum in (
            ('width', width, _pj_figure_dimension(FIGWIDTH, 800), 320),
            ('height', height, _pj_figure_dimension(FIGHEIGHT, 420), 240)):
        value = max(minimum, default) if value is None else value
        if isinstance(value, bool) or not isinstance(value, Integral) or not minimum <= value <= 10000:
            raise ValueError(f'mzpjShowChart(): {key} must be an integer between {minimum} and 10000 pixels.')
        dimensions.append(int(value))
    if not _pj_chart_js:
        raise RuntimeError('Chart.js is unavailable. Install the updated Pj module containing Chart.js.')
    payload = dict(type=chart_type, data=dict(datasets=datasets), options=options)
    if legend is not None and not static:
        payload['_mzpjLegend'] = legend
    if labels is not None:
        payload['data']['labels'] = labels
    # I valori dell'utente restano dati anche se contengono tag o separatori JavaScript.
    encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False)
    for char, replacement in (('&', '\\u0026'), ('<', '\\u003c'), ('>', '\\u003e'),
                              ('\u2028', '\\u2028'), ('\u2029', '\\u2029')):
        encoded = encoded.replace(char, replacement)
    root_id = 'mzpj_chartjs_' + uuid.uuid4().hex
    heading = html.escape(str(title) if title is not None else 'Chart.js plot')
    if static:
        _pj_chart_static(payload, name, heading, root_id, dimensions)
        return
    style = '''<style>
.mzpj-chartjs{font-family:Arial,sans-serif;color:#34445b;margin:12px 0;max-width:100%}
.mzpj-chartjs summary{cursor:pointer;list-style:none;color:#3e6da9;font-weight:600;padding:11px 2px;border-top:1px solid #d7e3f3;border-bottom:1px solid #d7e3f3}
.mzpj-chartjs summary::-webkit-details-marker{display:none}
.mzpj-chartjs summary::before{content:'+';display:inline-block;width:22px;font-size:18px}
.mzpj-chartjs details[open]>summary::before{content:'−'}
.mzpj-chartjs .mzpj-cj-body{padding:12px 0 4px}
.mzpj-chartjs .mzpj-cj-surface{position:relative;max-width:100%;background-size:100% 100%;background-repeat:no-repeat;background-color:white}
.mzpj-chartjs .mzpj-cj-note{font-size:12px;color:#657b9b;margin:8px 0;line-height:1.5}
.mzpj-chartjs .mzpj-cj-error{color:#ad3131}
.mzpj-chartjs .mzpj-cj-float{position:absolute;z-index:3;left:10px;top:10px;width:228px;max-width:calc(100% - 16px);max-height:calc(100% - 16px);display:flex;flex-direction:column;box-sizing:border-box;border:1px solid #c8d8ed;border-radius:8px;background:rgba(255,255,255,.97);box-shadow:0 3px 12px #243c5d22;font-size:12px;color:#506786}
.mzpj-chartjs .mzpj-cj-float-head{display:flex;align-items:center;gap:8px;padding:6px 8px 6px 11px;cursor:grab;touch-action:none;color:#3e6da9;font-weight:600;border-radius:8px}
.mzpj-chartjs .mzpj-cj-float-head:focus-visible{outline:2px solid #3e6da9;outline-offset:2px}
.mzpj-chartjs .mzpj-cj-float-title{flex:1;min-width:0;overflow-wrap:anywhere}
.mzpj-chartjs .mzpj-cj-float-toggle{width:26px;height:26px;border:0;border-radius:5px;background:#edf3fb;color:#3e6da9;font-size:18px;cursor:pointer}
.mzpj-chartjs .mzpj-cj-float-body{padding:2px 10px 10px;min-height:0;max-height:190px;overflow:auto;scrollbar-width:thin}
.mzpj-chartjs .mzpj-cj-float-note{line-height:1.45;margin:5px 0 9px}
.mzpj-chartjs .mzpj-cj-float-item{display:flex;align-items:flex-start;gap:8px;padding:6px 0;width:100%;text-align:left;box-sizing:border-box;font:inherit;color:inherit;border:0;background:transparent}
.mzpj-chartjs button.mzpj-cj-float-item{cursor:pointer;border-radius:4px}
.mzpj-chartjs button.mzpj-cj-float-item:hover{background:#f1f6fc}
.mzpj-chartjs .mzpj-cj-float-marker{width:10px;height:10px;border-radius:3px;margin-top:3px;flex:none}
.mzpj-chartjs .mzpj-cj-float-item[aria-pressed=false]{opacity:.55}
.mzpj-chartjs .mzpj-cj-float-item[aria-pressed=false] strong{text-decoration:line-through}
.mzpj-chartjs .mzpj-cj-float-description{display:block;font-size:11px;line-height:1.4;margin-top:2px;font-weight:400}
@media print{.mzpj-chartjs canvas{visibility:visible!important}.mzpj-chartjs summary::before{content:''}
.mzpj-chartjs .mzpj-cj-note,.mzpj-chartjs .mzpj-cj-float{display:none!important}.mzpj-chartjs .mzpj-cj-surface{background-image:none!important;break-inside:avoid}}
</style>'''
    surface = (f'<div class="mzpj-cj-body"><div class="mzpj-cj-surface" '
               f'style="width:{dimensions[0]}px;height:{dimensions[1]}px" role="img" '
               f'aria-label="{heading}"><canvas aria-label="{heading}" role="img"></canvas></div>'
               '<p class="mzpj-cj-note ignore-html">Hover for values. Click a legend item to show or hide a series. '
               'Interactions affect this view only; run Python again to recalculate results.</p>'
               '<p class="mzpj-cj-error" hidden></p></div>')
    content = (f'<div id="{root_id}" class="mzpj-chartjs">' +
               (f'<details{" open" if expanded else ""}><summary>{heading}</summary>{surface}</details>'
                if accordion else f'<div style="color:#3e6da9;font-weight:600">{heading}</div>{surface}') + '</div>')
    # Il costruttore privato evita di sostituire window.Chart usato da altri moduli.
    library = ('<script>(function(){if(window.mzPjChart461)return;const previous=window.Chart;'
               'const module=undefined,exports=undefined,define=undefined;' + _pj_chart_js +
               '\nwindow.mzPjChart461=window.Chart;window.Chart=previous;})();</script>')
    renderer = r'''<script>(function(){
const root=document.getElementById('__ROOT__'),config=__PAYLOAD__;
const legendInfo=config._mzpjLegend;delete config._mzpjLegend;
const surface=root.querySelector('.mzpj-cj-surface'),canvas=surface.querySelector('canvas');
const details=root.querySelector('details'),error=root.querySelector('.mzpj-cj-error');
const C=window.mzPjChart461;let chart=null,frame=0,observer,printing=false,floating=null,legendResize=null;
function snapshot(c){if(c.width&&c.height)surface.style.backgroundImage='url("'+c.toBase64Image()+'")';}
function dispose(){cancelAnimationFrame(frame);if(observer)observer.disconnect();
 if(legendResize)legendResize.disconnect();
 window.removeEventListener('beforeprint',preparePrint);window.removeEventListener('afterprint',finishPrint);
 if(chart){chart.destroy();chart=null;}}
function showError(e){error.hidden=false;error.textContent='Chart.js: '+e.message;}
// Il PDF di jamovi stampa l'HTML in una finestra separata, senza sfondi e senza attendere animazioni.
function preparePrint(){printing=true;render();if(chart){chart.stop();chart.resize();chart.update('none');snapshot(chart);}}
function finishPrint(){printing=false;if(chart)chart.resize();}
function refreshLegend(c){if(floating)floating.querySelectorAll('[data-dataset-index]').forEach(b=>
 b.setAttribute('aria-pressed',String(c.isDatasetVisible(Number(b.dataset.datasetIndex)))));}
function makeLegend(){
 if(!legendInfo||floating)return;
 floating=document.createElement('aside');floating.className='mzpj-cj-float';floating.setAttribute('aria-label',legendInfo.title||'Legend and notes');
 const head=document.createElement('div');head.className='mzpj-cj-float-head';head.tabIndex=0;head.setAttribute('role','group');
 head.setAttribute('aria-label','Move legend: drag or use arrow keys. Shift moves farther.');
 const title=document.createElement('span');title.className='mzpj-cj-float-title';title.textContent=legendInfo.title||'Legend & notes';
 const toggle=document.createElement('button');toggle.type='button';toggle.className='mzpj-cj-float-toggle';
 const body=document.createElement('div');body.className='mzpj-cj-float-body';body.id=root.id+'_legend_body';
 toggle.setAttribute('aria-controls',body.id);let collapsed=legendInfo.collapsed===true;
 let x=0,y=10,drag=null;
 function place(nx,ny){x=Math.max(0,Math.min(nx,surface.clientWidth-floating.offsetWidth));
  y=Math.max(0,Math.min(ny,surface.clientHeight-floating.offsetHeight));floating.style.left=x+'px';floating.style.top=y+'px';}
 function fold(){body.hidden=collapsed;toggle.textContent=collapsed?'+':'−';toggle.setAttribute('aria-expanded',String(!collapsed));
  toggle.setAttribute('aria-label',collapsed?'Expand legend and notes':'Collapse legend and notes');place(x,y);}
 toggle.addEventListener('click',e=>{e.stopPropagation();collapsed=!collapsed;fold();});
 head.append(title,toggle);floating.append(head,body);surface.appendChild(floating);
 if(legendInfo.text){const p=document.createElement('p');p.className='mzpj-cj-float-note';p.textContent=legendInfo.text;body.appendChild(p);}
 const items=legendInfo.items||chart.data.datasets.map((d,i)=>({label:d.label||'Series '+(i+1),dataset:i}));
 items.forEach(item=>{const linked=Number.isInteger(item.dataset),row=document.createElement(linked?'button':'div');
  row.className='mzpj-cj-float-item';if(linked){row.type='button';row.dataset.datasetIndex=item.dataset;
   row.addEventListener('click',()=>{chart.setDatasetVisibility(item.dataset,!chart.isDatasetVisible(item.dataset));chart.update();});}
  const marker=document.createElement('span');marker.className='mzpj-cj-float-marker';marker.setAttribute('aria-hidden','true');
  const dataset=linked?chart.data.datasets[item.dataset]:{},raw=item.color||dataset.borderColor||'#3e6da9';
  const color=Array.isArray(raw)?raw[0]:raw;marker.style.backgroundColor=typeof color==='string'&&CSS.supports('color',color)?color:'#3e6da9';
  const text=document.createElement('span'),label=document.createElement('strong');label.textContent=item.label;text.appendChild(label);
  if(item.text){const description=document.createElement('span');description.className='mzpj-cj-float-description';description.textContent=item.text;text.appendChild(description);}
  row.append(marker,text);body.appendChild(row);});
 head.addEventListener('pointerdown',e=>{if(e.button!==0||e.target.closest('button'))return;
  e.preventDefault();e.stopPropagation();drag={id:e.pointerId,mx:e.clientX,my:e.clientY,x,y};head.setPointerCapture(e.pointerId);});
 head.addEventListener('pointermove',e=>{if(drag&&e.pointerId===drag.id)place(drag.x+e.clientX-drag.mx,drag.y+e.clientY-drag.my);});
 const end=e=>{if(drag&&e.pointerId===drag.id)drag=null;};
 head.addEventListener('pointerup',end);head.addEventListener('pointercancel',end);head.addEventListener('lostpointercapture',end);
 head.addEventListener('keydown',e=>{if(e.target!==head)return;const moves={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]};
  const d=moves[e.key];if(d){e.preventDefault();place(x+d[0]*(e.shiftKey?20:5),y+d[1]*(e.shiftKey?20:5));}});
 fold();place(surface.clientWidth-floating.offsetWidth-10,10);refreshLegend(chart);
 legendResize=new ResizeObserver(()=>place(x,y));legendResize.observe(surface);legendResize.observe(floating);
}
function render(){
 if(!root.isConnected||(details&&!details.open))return;
 try{
  if(chart){chart.resize();return;}
  const colors=['#3e6da9','#ed9950','#429587','#a580b7','#d66a70','#7e929c'];
  config.data.datasets.forEach((d,i)=>{if(d.borderColor===undefined)d.borderColor=colors[i%colors.length];
   if(d.backgroundColor===undefined)d.backgroundColor=colors[i%colors.length]+'99';});
  config.options.responsive=true;config.options.maintainAspectRatio=false;
  config.options.plugins=config.options.plugins||{};config.options.plugins.mzpjSnapshot={};
  if(printing||window.matchMedia('print').matches)config.options.animation=false;
  else if(config.options.animation===undefined)config.options.animation={duration:450};
  config.plugins=[{id:'mzpjSnapshot',afterRender:snapshot,afterUpdate:refreshLegend,beforeDraw(c){
   const ctx=c.ctx;ctx.save();ctx.globalCompositeOperation='destination-over';
   ctx.fillStyle='white';ctx.fillRect(0,0,c.width,c.height);ctx.restore();}}];
  chart=new C(canvas,config);
  canvas.style.backgroundColor='white';
  makeLegend();
 }catch(e){const partial=C.getChart(canvas);if(partial)partial.destroy();chart=null;showError(e);}
}
if(details)details.addEventListener('toggle',()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(render);});
observer=new MutationObserver(()=>{if(!root.isConnected)dispose();});
observer.observe(document.documentElement,{childList:true,subtree:true});
window.addEventListener('beforeprint',preparePrint);window.addEventListener('afterprint',finishPrint);
render();
})();</script>'''
    renderer = renderer.replace('__ROOT__', root_id).replace('__PAYLOAD__', encoded)
    _pj_add_html(style + content + library + renderer, name=name, title='')


def _pj_chart_static(payload, name, heading, root_id, dimensions):
    # Svg e il contratto nativo per fotografie client: il contenuto PNG resta raster.
    encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False)
    for char, replacement in (('&', '\\u0026'), ('<', '\\u003c'), ('>', '\\u003e'),
                              ('\u2028', '\\u2028'), ('\u2029', '\\u2029')):
        encoded = encoded.replace(char, replacement)
    width, height = dimensions
    content = (f'<div id="{root_id}">'
               f'<svg xmlns="http://www.w3.org/2000/svg" class="jmv-results-svg-content" '
               f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
               'style="max-width:100%;height:auto" role="img">'
               f'<title>{heading}</title><image width="{width}" height="{height}" /></svg>'
               '<p class="mzpj-cj-error" hidden></p></div>')
    library = ('<script>(function(){if(window.mzPjChart461)return;const previous=window.Chart;'
               'const module=undefined,exports=undefined,define=undefined;' + _pj_chart_js +
               '\nwindow.mzPjChart461=window.Chart;window.Chart=previous;})();</script>')
    renderer = r'''<script>(function(){
const root=document.getElementById('__ROOT__'),config=__PAYLOAD__,svg=root.querySelector('svg');
const host=root.closest('.jmv-results-svg');if(host){host.style.width='__WIDTH__px';host.style.maxWidth='100%';}
const canvas=document.createElement('canvas');canvas.width=__WIDTH__;canvas.height=__HEIGHT__;
const holder=document.createElement('div');holder.style.cssText='position:absolute;left:-100000px;top:0';
holder.appendChild(canvas);root.appendChild(holder);let chart;
try{
 const colors=['#3e6da9','#ed9950','#429587','#a580b7','#d66a70','#7e929c'];
 config.data.datasets.forEach((d,i)=>{if(d.borderColor===undefined)d.borderColor=colors[i%colors.length];
  if(d.backgroundColor===undefined)d.backgroundColor=colors[i%colors.length]+'99';});
 config.options.responsive=false;config.options.animation=false;config.options.events=[];
 config.options.devicePixelRatio=2;
 config.plugins=[{id:'mzpjWhite',beforeDraw(c){const ctx=c.ctx;ctx.save();
  ctx.globalCompositeOperation='destination-over';ctx.fillStyle='white';
  ctx.fillRect(0,0,c.width,c.height);ctx.restore();}}];
 chart=new window.mzPjChart461(canvas,config);
 svg.querySelector('image').setAttribute('href',chart.toBase64Image());
}catch(e){const p=root.querySelector('p');p.hidden=false;p.textContent='Chart.js: '+e.message;}
finally{const c=chart||window.mzPjChart461.getChart(canvas);if(c)c.destroy();holder.remove();}
})();</script>'''
    renderer = (renderer.replace('__ROOT__', root_id).replace('__WIDTH__', str(width))
                .replace('__HEIGHT__', str(height)).replace('__PAYLOAD__', encoded))
    result_name = _pj_result_name(name, 'chart', _html_counter)
    results['items'].append(dict(type='Svg', name=result_name, title=heading,
                                 content=content + library + renderer))
