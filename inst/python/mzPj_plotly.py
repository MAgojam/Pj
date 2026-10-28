# Due percorsi separati: Html interattivo e Svg statico acquisito una sola volta.
def _pj_show_plotly(figure, *, name=None, title=None, height=800, config=None,
                    static=False, export_width=960):
    import json
    import uuid
    import html
    import re
    if not isinstance(static, bool):
        raise TypeError('static must be True or False.')
    if isinstance(export_width, bool) or not isinstance(export_width, int) or not 400 <= export_width <= 2400:
        raise ValueError('export_width must be an integer between 400 and 2400.')
    if isinstance(height, bool) or not isinstance(height, int) or not 200 <= height <= 3000:
        raise ValueError('height must be an integer between 200 and 3000.')
    if not hasattr(figure, 'to_json'):
        raise TypeError('mzpjShowPlotly() expects a Plotly Figure.')
    payload = json.loads(figure.to_json())
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
    heading = html.escape(str(title or payload['layout'].get('title', {}).get('text', 'Plotly figure')))
    if static:
        # La superficie temporanea scompare dopo toImage: nessun listener persistente.
        content = (f'<div id="{root_id}" style="width:{export_width}px;max-width:100%">'
                   '<p class="mzpj-plotly-status ignore-html" role="status" '
                   'style="font:12px Arial;color:#657b9b">Preparing static Plotly image…</p>'
                   f'<svg xmlns="http://www.w3.org/2000/svg" class="jmv-results-svg-content" '
                   f'width="{export_width}" height="{height}" viewBox="0 0 {export_width} {height}" '
                   'style="max-width:100%;height:auto">'
                   f'<title>{heading}</title><image width="{export_width}" height="{height}" /></svg></div>')
    else:
        content = f'<div id="{root_id}" style="width:100%;min-height:{height}px">Loading Plotly…</div>'
    renderer = r'''<script>(async function(){
const root=document.getElementById(__ROOT__),figure=__FIGURE__,config=__CONFIG__,asset=__ASSET__;
if(!root)return;
const isStatic=__STATIC__,status=isStatic?root.querySelector('.mzpj-plotly-status'):null;
let plot=root,P,resize,removal,temporary=false;
function fail(e){const target=status||root;target.hidden=false;target.style.minHeight='0';
 const detail=e&&e.message?e.message:typeof e==='string'?e:'Static image preparation failed.';
 target.textContent='Plotly could not be displayed: '+detail;target.style.color='#b42318';}
try{
 if(!window.mzPjPlotly411&&asset){
  if(!window.mzPjPlotlyLoading411)window.mzPjPlotlyLoading411=(async()=>{
   const bytes=Uint8Array.from(atob(asset),c=>c.charCodeAt(0));
   const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('deflate'));
   const script=document.createElement('script');script.textContent=await new Response(stream).text();
   document.head.appendChild(script);script.remove();
  })().catch(e=>{delete window.mzPjPlotlyLoading411;throw e;});
  await window.mzPjPlotlyLoading411;
 }
 P=window.mzPjPlotly411;if(!P)throw new Error('The Pj Plotly resource could not be loaded.');
 if(!root.isConnected)return;
 if(isStatic){
  plot=document.createElement('div');temporary=true;
  plot.style.cssText='position:absolute;left:-100000px;top:0;width:__WIDTH__px;height:__HEIGHT__px';
  root.appendChild(plot);
  await P.newPlot(plot,figure.data,figure.layout,config);
  // Il PNG diretto usa blob:, vietato dalla CSP jamovi. SVG completo via data:.
  const source=await P.toImage(plot,{format:'svg',width:__WIDTH__,height:__HEIGHT__});
  const bitmap=new Image();
  await new Promise((resolve,reject)=>{bitmap.onload=resolve;
   bitmap.onerror=()=>reject(new Error('The static Plotly SVG image could not be decoded.'));
   bitmap.src=source;});
  const canvas=document.createElement('canvas');canvas.width=__WIDTH__*2;canvas.height=__HEIGHT__*2;
  const context=canvas.getContext('2d');
  if(!context)throw new Error('The static Plotly image requires a 2D canvas context.');
  context.drawImage(bitmap,0,0,canvas.width,canvas.height);
  const image=canvas.toDataURL('image/png');
  if(!root.isConnected)return;
  root.querySelector('svg.jmv-results-svg-content image').setAttribute('href',image);
  root.dataset.mzpjExportReady='true';status.hidden=true;
 }else{
  root.textContent='';await P.newPlot(plot,figure.data,figure.layout,config);
  resize=new ResizeObserver(()=>{if(root.isConnected)Promise.resolve(P.Plots.resize(plot)).catch(fail);});
  resize.observe(plot);
  removal=new MutationObserver(()=>{if(!root.isConnected){resize.disconnect();removal.disconnect();P.purge(plot);}});
  removal.observe(document.body,{childList:true,subtree:true});
 }
}catch(e){fail(e);}
finally{if(temporary){if(P)P.purge(plot);plot.remove();}}
})();</script>'''
    # Sostituzione unica: mai reinterpretare le etichette dell'utente come template.
    substitutions = dict(ROOT=safe(root_id), FIGURE=safe(payload), CONFIG=safe(settings),
                         ASSET=safe(_pj_plotly_gzip), STATIC=safe(static),
                         WIDTH=str(export_width), HEIGHT=str(height))
    content += re.sub(r'__(ROOT|FIGURE|CONFIG|ASSET|STATIC|WIDTH|HEIGHT)__',
                      lambda match: substitutions[match.group(1)], renderer)
    item = dict(type='Svg' if static else 'Html', name=name, title=title or '', content=content)
    if not _pj_plotly_gzip:
        item['scripts'] = ['extdata/plotly.min.js']
    results['items'].append(item)
