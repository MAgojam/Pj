# Risultati condivisi: nomi, immagini, testo e serializzazione.

def _pj_accordion_options(accordion, expanded, accordion_type):
    if not isinstance(accordion, bool) or not isinstance(expanded, bool):
        raise TypeError('accordion and expanded must be True or False.')
    if accordion_type not in ('line', 'bordered'):
        raise ValueError('accordion_type must be line or bordered.')
    if not accordion and not expanded:
        raise ValueError('expanded=False requires accordion=True.')


def _pj_wrap_accordion(content, title, accordion=True, expanded=True, accordion_type='line'):
    """Un solo contenitore condiviso; il contenuto del grafico resta esportabile da solo."""
    _pj_accordion_options(accordion, expanded, accordion_type)
    if not accordion:
        return content
    import html
    import uuid
    root = 'mzpj_accordion_' + uuid.uuid4().hex
    style = '''<style>
.jmv-results-html:has(> .content > .mzpj-accordion){width:500px;min-width:0;max-width:100%}
.mzpj-accordion{width:100%;box-sizing:border-box;max-width:100%;min-width:0;margin:6px 0 12px;font:13px/1.5 Arial,sans-serif;color:#334155}
.mzpj-accordion>summary{display:flex;align-items:center;gap:6px;list-style:none;cursor:pointer;color:#3e6da9;font-weight:500;padding:4px 0;overflow-x:auto}
.mzpj-accordion>summary::-webkit-details-marker{display:none}
.mzpj-accordion>summary:focus-visible{outline:2px solid #3e6da9;outline-offset:3px}
.mzpj-accordion[open]>summary{font-weight:700}
.mzpj-accordion-icon{display:flex;align-items:center;justify-content:center;flex:none;width:18px;padding-inline-end:6px;border-inline-end:1px solid rgba(62,109,169,.5)}
.mzpj-accordion-icon svg{width:14px;height:14px;flex:none;overflow:visible}
.mzpj-accordion-icon .mzpj-accordion-plus-minus{width:12px;height:12px}
.mzpj-accordion-icon .horizontal,.mzpj-accordion-icon .vertical{transform-origin:center;transform-box:view-box;transition:transform .3s ease,opacity .3s ease}
.mzpj-accordion-icon .vertical{transform:rotate(0deg);opacity:1}
.mzpj-accordion[open]>summary .vertical{transform:rotate(90deg);opacity:0}
.mzpj-accordion-title{display:flex;align-items:center;flex:1;min-width:0;gap:8px}
.mzpj-accordion-label{flex:none;white-space:nowrap}
.mzpj-accordion-line>summary .mzpj-accordion-title::before,.mzpj-accordion-line>summary .mzpj-accordion-title::after{content:'';height:1px;background:rgba(62,109,169,.5);flex:0 0 30px;transition:height .3s ease,flex-grow .3s ease,background .3s ease}
.mzpj-accordion-line[open]>summary .mzpj-accordion-title::before,.mzpj-accordion-line[open]>summary .mzpj-accordion-title::after{height:2px;background:rgba(62,109,169,.7)}
.mzpj-accordion-line[open]>summary .mzpj-accordion-title::after{flex-grow:1}
.mzpj-accordion-bordered>summary{border-block:1px solid #c5d6e9;padding:7px 0}
.mzpj-accordion-bordered>summary .mzpj-accordion-icon{border:0;padding:0}
.mzpj-accordion-icon .mzpj-accordion-arrow{width:10px;height:10px}
.mzpj-accordion-arrow{transform-origin:center;transform-box:view-box;transform:rotate(0deg);transition:transform .3s ease}
.mzpj-accordion-bordered:dir(rtl)>summary .mzpj-accordion-arrow{transform:rotate(180deg)}
.mzpj-accordion-bordered[open]>summary .mzpj-accordion-arrow{transform:rotate(90deg)}
.mzpj-accordion-content{padding-top:9px;min-width:0;max-width:100%}
/* Le vecchie analisi salvate possono includere transition:none!important.
   Limita la precedenza alle animazioni SVG di questa revisione, come richiesto. */
.mzpj-accordion[data-mzpj-motion="svg"]>summary .horizontal,.mzpj-accordion[data-mzpj-motion="svg"]>summary .vertical{transition:transform .3s ease,opacity .3s ease!important}
.mzpj-accordion[data-mzpj-motion="svg"]>summary .mzpj-accordion-arrow{transition:transform .3s ease!important}
.mzpj-accordion[data-mzpj-motion="svg"]>summary .mzpj-accordion-title::before,.mzpj-accordion[data-mzpj-motion="svg"]>summary .mzpj-accordion-title::after{transition:height .3s ease,flex-grow .3s ease,background .3s ease!important}
</style>'''
    # Stessa geometria del controllo Variables Pjp e di Info & Notes Metafora.
    icon = ('<svg class="mzpj-accordion-plus-minus" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2">'
            '<line class="horizontal" x1="4" y1="8" x2="12" y2="8"/>'
            '<line class="vertical" x1="8" y1="4" x2="8" y2="12"/></svg>'
            if accordion_type == 'line' else
            '<svg class="mzpj-accordion-arrow" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.5">'
            '<polyline points="6,4 10,8 6,12"/></svg>')
    return (style + f'<details id="{root}" data-mzpj-motion="svg" class="mzpj-accordion mzpj-accordion-{accordion_type}"'
            + (' open' if expanded else '') + '><summary class="ignore-html">'
            '<span class="mzpj-accordion-icon" aria-hidden="true">' + icon + '</span>'
            '<span class="mzpj-accordion-title"><span class="mzpj-accordion-label">'
            + html.escape(str(title)) + '</span></span></summary>'
            '<div class="mzpj-accordion-content">' + content + '</div></details>'
            '<script>(function(){const panel=document.getElementById("' + root + '");'
            'panel.addEventListener("toggle",()=>requestAnimationFrame(()=>'
            'window.dispatchEvent(new Event("resize"))));})();</script>')

def _pj_result_name(name, prefix, counter, table=False):
    import re
    used = {item.get('name'): item for item in results['items']}
    if name is None:
        while True:
            counter[0] += 1
            name = f'{prefix}_{counter[0]}'
            if name not in used:
                break
    if not isinstance(name, str) or re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', name) is None:
        raise ValueError('Result name must start with a letter and contain only letters, digits and underscores.')
    if name in ('console', 'pythonInfo', 'createdColumns', 'pythonError'):
        raise ValueError('This result name is reserved by Pj.')
    if name in used and not (table and (used[name].get('type') == 'Table' or used[name].get('_pjTable'))):
        raise ValueError(f'Result name {name!r} is already in use; choose a unique name.')
    return name


_plot_counter = [0]
_html_counter = [0]
_text_counter = [0]
_table_counter = [0]


def _pj_graphic_mode(result_type, static=False):
    """Resolve the explicit native type while preserving legacy static calls."""
    if not isinstance(static, bool):
        raise TypeError('static must be True or False.')
    if result_type is None:
        return 'svg' if static else 'html'
    if result_type not in ('html', 'svg', 'image'):
        raise ValueError('result_type must be html, svg or image.')
    if static and result_type == 'html':
        raise ValueError('static=True conflicts with result_type="html".')
    if result_type == 'image' and not globals().get('_pj_image_capture_enabled', False):
        raise RuntimeError('JavaScript Image capture requires the updated Pj/Pjp editor. '
                           'This service host has not enabled its capture bridge. '
                           'PNG bytes can always be passed directly to mzpjShowImage().')
    return result_type


def _pj_emit_graphic(content, name, title, result_type, scripts=None, *,
                     accordion=False, expanded=True, accordion_type='line'):
    """Native SVG now; native Image after an acknowledged browser PNG capture."""
    if result_type == 'svg':
        # Native Svg sizing belongs exclusively to jamovi, without Html containers.
        item = dict(type='Svg', name=name, title=title, content=content)
        if scripts:
            item['scripts'] = scripts
        results['items'].append(item)
        return
    _pj_graphic_mode(result_type)
    if result_type != 'image':
        raise ValueError('Internal graphic dispatcher expects svg or image.')
    import uuid
    token = uuid.uuid4().hex
    root_id = 'mzpj_image_' + token
    request = json.dumps(dict(root=root_id, name=name, token=token, title=str(title or '')), ensure_ascii=True).replace('<', '\\u003c')
    # Rendering occurs offscreen, in this analysis's Results iframe. Only the
    # PNG is sent through the native option channel; Python is not rerun.
    bridge = r'''<script>(async function(){
const request=__REQUEST__,root=document.getElementById(request.root);
if(!root)return;
const status=root.querySelector('[data-image-status]'),errorTitle=root.querySelector('[data-image-error-title]');
function fail(error){if(!root.isConnected)return;root.dataset.mzpjImageCapture='error';root.setAttribute('aria-busy','false');errorTitle.hidden=false;errorTitle.textContent=request.title||request.name;status.hidden=false;status.setAttribute('role','alert');status.textContent='Image preparation failed: '+String(error&&error.message||error)+'. Run again after correcting the figure.';}
try{
 if(typeof window.setOption!=='function')throw Error('the native Image capture bridge is unavailable');
 const deadline=Date.now()+30000;
 const frame=()=>new Promise(resolve=>requestAnimationFrame(resolve));
 let source;
 while(root.isConnected&&Date.now()<deadline){
  source=root.querySelector('svg.jmv-results-svg-content');
  const error=root.querySelector('.mzpj-cj-error:not([hidden])');
  const plotlyError=root.querySelector('.mz-plotly-status, .mzpj-plotly-status');
  if(error)throw Error(error.textContent);
  if(plotlyError&&plotlyError.textContent.startsWith('Plotly could not'))throw Error(plotlyError.textContent);
  if(source&&Array.from(source.querySelectorAll('image')).every(i=>(i.getAttribute('href')||'').startsWith('data:image/'))){await frame();await frame();break;}
  await frame();
 }
 if(!root.isConnected)return;
 if(!source||Date.now()>=deadline)throw Error('the graphic did not finish rendering');
 const width=Number(source.getAttribute('width')),height=Number(source.getAttribute('height'));
 if(!Number.isFinite(width)||!Number.isFinite(height)||width<=0||height<=0)throw Error('invalid figure dimensions');
 const scale=Math.min(2,4000/width,4000/height,Math.sqrt(4000000/(width*height)));
 const copy=source.cloneNode(true);copy.setAttribute('xmlns','http://www.w3.org/2000/svg');
 const style=getComputedStyle(source);copy.style.fontFamily=style.fontFamily;copy.style.fontSize=style.fontSize;
 const bitmap=new Image();
 await new Promise((resolve,reject)=>{bitmap.onload=resolve;bitmap.onerror=()=>reject(Error('the graphic could not be rasterized'));bitmap.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(new XMLSerializer().serializeToString(copy));});
 if(!root.isConnected)return;
 const canvas=document.createElement('canvas');canvas.width=Math.max(1,Math.floor(width*scale));canvas.height=Math.max(1,Math.floor(height*scale));
 const context=canvas.getContext('2d');if(!context)throw Error('a 2D canvas is unavailable');
 context.fillStyle='white';context.fillRect(0,0,canvas.width,canvas.height);context.drawImage(bitmap,0,0,canvas.width,canvas.height);
 const content=canvas.toDataURL('image/png').split(',')[1];
 if(content.length>1000000)throw Error('the PNG is too large; reduce the figure dimensions');
 const displayScale=Math.min(1,2000/width,2000/height);
 const entry={name:request.name,token:request.token,content,width:Math.max(1,Math.round(width*displayScale)),height:Math.max(1,Math.round(height*displayScale))};
 let queue=window.mzPjNativeImageQueue;
 if(!queue){
  queue=window.mzPjNativeImageQueue={entries:new Map(),ackTimers:new Map(),timer:null};
  queue.prune=()=>{for(const [id]of queue.entries)if(!document.getElementById(id)){clearTimeout(queue.ackTimers?.get(id));queue.ackTimers?.delete(id);queue.entries.delete(id);}};
  queue.observer=new MutationObserver(()=>queue.prune());queue.observer.observe(document.documentElement,{childList:true,subtree:true});
 }
 queue.prune();queue.entries.set(request.root,entry);clearTimeout(queue.timer);
 const accepted=queue.entries.size<=20&&JSON.stringify({version:1,images:Array.from(queue.entries.values())}).length<=1500000;
 if(!accepted){queue.entries.delete(request.root);fail(Error('too many or oversized pending PNG captures; reduce the number or size of figures'));}
 queue.timer=setTimeout(()=>{queue.prune();const payload=JSON.stringify({version:1,images:Array.from(queue.entries.values())});
  if(queue.entries.size)window.setOption('graphicCapture',payload);
 },50);
 if(accepted){
  root.dataset.mzpjImageReady='true';
  if(!queue.ackTimers)queue.ackTimers=new Map();
  if(!queue.ackTimers.has(request.root))queue.ackTimers.set(request.root,setTimeout(()=>{queue.ackTimers.delete(request.root);if(root.isConnected)fail(Error('the native Image result was not acknowledged'));},30000));
 }
}catch(error){fail(error);}
})();</script>'''.replace('__REQUEST__', request)
    # Keep the pending host laid out offscreen: display:none would break plot
    # measurements. The CSS applies before scripts run, including its heading.
    # A failure changes the state and restores the ordinary visible result.
    pending_style = ('<style>.jmv-results-html:has([data-mzpj-image-capture="pending"])'
                     '{position:fixed!important;left:-100000px!important;top:0!important;'
                     'margin:0!important;pointer-events:none!important}</style>')
    wrapper = (pending_style + '<div id="' + root_id + '" data-mzpj-image-capture="pending" aria-busy="true">'
               '<strong data-image-error-title hidden></strong><p data-image-status role="status" hidden></p>'
               '<div class="ignore-html" aria-hidden="true" style="position:absolute;left:-100000px;top:0;pointer-events:none">'
               + content + '</div></div>' + bridge)
    item = dict(type='Html', name=name, title=title, content=wrapper,
                image_request=dict(version=1, token=token))
    if scripts:
        item['scripts'] = scripts
    results['items'].append(item)

def _pj_figure_dimension(value, default):
    """Ogni campo vuoto o non valido usa soltanto il proprio valore predefinito."""
    try:
        dimension = int(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return dimension if dimension > 0 else default

def _pj_explicit_dimension(value, parameter):
    if value is None:
        return None
    from numbers import Integral
    if isinstance(value, bool) or not isinstance(value, Integral) or not 1 <= value <= 10000:
        raise ValueError(f'{parameter} must be an integer between 1 and 10000 pixels.')
    return int(value)


def _pj_add_svg(content, name=None, title=None, *, width=None, height=None):
    """Display standalone SVG markup as a native Svg result, without HTML controls."""
    import xml.etree.ElementTree as ET
    import re
    if not isinstance(content, str):
        raise TypeError('mzpjShowSvg(): expected SVG markup as a string.')
    root = ET.fromstring(content)
    if root.tag not in ('svg', '{http://www.w3.org/2000/svg}svg'):
        raise ValueError('mzpjShowSvg(): the root element must be svg.')
    requested_width = _pj_explicit_dimension(width, 'width')
    requested_height = _pj_explicit_dimension(height, 'height')
    if width is None and height is None:
        requested_width = _pj_figure_dimension(FIGWIDTH, None)
        requested_height = _pj_figure_dimension(FIGHEIGHT, None)
    viewbox = re.split(r'[ ,]+', root.get('viewBox', '').strip())
    ratio = None
    if len(viewbox) == 4:
        try:
            vw, vh = float(viewbox[2]), float(viewbox[3])
            if math.isfinite(vw) and math.isfinite(vh) and vw > 0 and vh > 0:
                ratio = vw / vh
        except ValueError:
            pass
    if ratio is None:
        try:
            vw = float(root.get('width', '').removesuffix('px'))
            vh = float(root.get('height', '').removesuffix('px'))
            if math.isfinite(vw) and math.isfinite(vh) and vw > 0 and vh > 0:
                ratio = vw / vh
        except ValueError:
            pass
    if (requested_width is None) != (requested_height is None):
        if ratio is None:
            raise ValueError('mzpjShowSvg(): one dimension requires a valid viewBox or numeric SVG width and height.')
        if requested_width is None:
            requested_width = max(1, round(requested_height * ratio))
        else:
            requested_height = max(1, round(requested_width / ratio))
    if requested_width is not None:
        root.set('width', str(requested_width))
        root.set('height', str(requested_height))
    root.set('class', (root.get('class', '') + ' jmv-results-svg-content jmv-results-svg-selection').strip())
    # Explicit attributes own the initial size; old inline dimensions must not override them.
    if requested_width is not None:
        style = re.sub(r'(^|;)\s*(width|height)\s*:[^;]*', '', root.get('style', ''), flags=re.I)
        root.set('style', style)
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    if root.tag == 'svg':
        root.set('xmlns', 'http://www.w3.org/2000/svg')
    name = _pj_result_name(name, 'svg', _html_counter)
    _pj_emit_graphic(ET.tostring(root, encoding='unicode'), name, title, 'svg')


def _pj_add_image(png_data, name=None, title=None, *, width=None, height=None):
    """Aggiunge un'immagine PNG (bytes gia' pronti) direttamente ai risultati,
    senza passare da matplotlib - utile per librerie con motore di rendering
    indipendente (plotly, plotnine, PIL, ecc.) che sanno gia' esportare in
    PNG per conto loro. Accetta bytes grezzi, un buffer io.BytesIO, o
    qualunque oggetto con .getvalue()/.read(). title e' opzionale (default
    "Plot Python" lato R se non indicato)."""
    local_width = _pj_explicit_dimension(width, 'width')
    local_height = _pj_explicit_dimension(height, 'height')
    if hasattr(png_data, 'getvalue'):
        png_data = png_data.getvalue()
    elif hasattr(png_data, 'read'):
        png_data = png_data.read()

    if not isinstance(png_data, (bytes, bytearray, memoryview)):
        raise TypeError('mzpjShowImage(): expected PNG bytes or a binary buffer.')
    png_data = bytes(png_data)
    # Verifica strutturale PNG senza dipendenze esterne e prima del renderer R.
    import zlib
    if png_data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('mzpjShowImage(): invalid PNG signature.')
    offset, chunks, ended = 8, [], False
    while offset + 12 <= len(png_data):
        length = struct.unpack('>I', png_data[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(png_data):
            raise ValueError('mzpjShowImage(): truncated PNG chunk.')
        kind = png_data[offset + 4:offset + 8]
        body = png_data[offset + 8:end - 4]
        crc = struct.unpack('>I', png_data[end - 4:end])[0]
        if zlib.crc32(kind + body) & 0xffffffff != crc:
            raise ValueError('mzpjShowImage(): invalid PNG checksum.')
        chunks.append(kind)
        if len(chunks) == 1 and (kind != b'IHDR' or length != 13):
            raise ValueError('mzpjShowImage(): invalid PNG header.')
        offset = end
        if kind == b'IEND':
            ended = length == 0
            break
    if not ended or b'IDAT' not in chunks or offset != len(png_data):
        raise ValueError('mzpjShowImage(): incomplete PNG image.')
    width, height = struct.unpack('>II', png_data[16:24])
    if not 0 < width <= 2147483647 or not 0 < height <= 2147483647:
        raise ValueError('mzpjShowImage(): invalid PNG dimensions.')

    # Dimensioni di visualizzazione: i bytes PNG originali restano invariati.
    requested_width = local_width
    requested_height = local_height
    if local_width is None and local_height is None:
        requested_width = _pj_figure_dimension(FIGWIDTH, None)
        requested_height = _pj_figure_dimension(FIGHEIGHT, None)
    if width <= 0 or height <= 0:
        width, height = 600, 500
    if requested_width is not None and requested_height is not None:
        width, height = requested_width, requested_height
    elif requested_width is not None:
        height = max(1, round(height * requested_width / width))
        width = requested_width
    elif requested_height is not None:
        width = max(1, round(width * requested_height / height))
        height = requested_height
    else:
        scale = min(1, 800 / width, 600 / height)
        width = max(1, round(width * scale))
        height = max(1, round(height * scale))

    img_b64 = base64.b64encode(png_data).decode('ascii')
    name = _pj_result_name(name, 'plot', _plot_counter)
    results['items'].append({
        'type': 'Image',
        'name': name,
        'title': title,
        'width': width,
        'height': height,
        'state': img_b64
    })

def _pj_add_html(content, name=None, title=None, *, accordion=True, expanded=True,
                 accordion_type='line'):
    """title e' opzionale (default "HTML Python" lato R se non indicato)."""
    name = _pj_result_name(name, 'html', _html_counter)

    if content is None:
        content = ""
    elif not isinstance(content, str):
        content = str(content)

    content = _pj_wrap_accordion(content, title if title is not None else 'HTML Python',
                                accordion, expanded, accordion_type)
    results['items'].append({
        'type': 'Html',
        'name': name,
        'title': '' if accordion else title,
        'content': content
    })

def _pj_add_text(content, name=None):
    """Aggiunge un risultato jamovi di tipo Text."""
    name = _pj_result_name(name, 'text', _text_counter)

    if content is None:
        content = ""
    elif not isinstance(content, str):
        content = str(content)

    results['items'].append({
        'type': 'Text',
        'name': name,
        'content': content
    })

def _pj_show(*args, **kwargs):
    """Sostituisce plt.show(): cattura la figura corrente, la codifica in
    PNG base64 e la aggiunge a results['items'] come item 'Image' - jamovi
    (pj.b.R::.render) la decodifica e la disegna sul device grafico attivo.
    Cosi' un normale plt.show() nel codice dell'utente (o nello script
    esterno) funziona senza bisogno di nessuna API specifica di Pj."""
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    _pj_add_image(buf.getvalue())
    buf.close()
    plt.close(fig)

if plt is not None:
    plt.show = _pj_show

def _json_safe_value(value):
    """Converte un singolo valore in qualcosa che json.dump puo' sempre serializzare.
    NaN/Inf -> None (JSON standard non li supporta; R/jsonlite legge None come NA).
    Scalari numpy (es. numpy.float64) -> tipo Python nativo.
    """
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if hasattr(value, 'item') and not isinstance(value, (list, dict, str, bytes)):
        try:
            return _json_safe_value(value.item())
        except (ValueError, AttributeError):
            return value
    return value


def _json_safe_column(col_values):
    """Converte una colonna (lista, array numpy, ecc.) in una lista JSON-safe.
    Se l'utente assegna direttamente un array numpy (senza chiamare .tolist()),
    lo convertiamo comunque qui, cosi' non serve ricordarselo ogni volta.
    """
    if hasattr(col_values, 'tolist'):
        col_values = col_values.tolist()
    return [_json_safe_value(v) for v in col_values]

