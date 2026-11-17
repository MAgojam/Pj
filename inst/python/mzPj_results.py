# Risultati condivisi: nomi, immagini, testo e serializzazione.

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


def _pj_emit_graphic(content, name, title, result_type, scripts=None):
    """Native SVG now; native Image after an acknowledged browser PNG capture."""
    if result_type == 'svg':
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
    request = json.dumps(dict(root=root_id, name=name, token=token), ensure_ascii=True)
    # Rendering occurs offscreen, in this analysis's Results iframe. Only the
    # PNG is sent through the native option channel; Python is not rerun.
    bridge = r'''<script>(async function(){
const request=__REQUEST__,root=document.getElementById(request.root);
if(!root)return;
const status=root.querySelector('[data-image-status]');
function fail(error){if(root.isConnected)status.textContent='Image preparation failed: '+String(error&&error.message||error)+'. Run again after correcting the figure.';}
try{
 if(typeof window.setOption!=='function')throw Error('the native Image capture bridge is unavailable');
 const deadline=Date.now()+30000;
 const frame=()=>new Promise(resolve=>requestAnimationFrame(resolve));
 let source;
 while(root.isConnected&&Date.now()<deadline){
  source=root.querySelector('svg.jmv-results-svg-content');
  const error=root.querySelector('.mzpj-cj-error:not([hidden])');
  const plotlyError=root.querySelector('.mzpj-plotly-status');
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
 const canvas=document.createElement('canvas');canvas.width=Math.max(1,Math.round(width*scale));canvas.height=Math.max(1,Math.round(height*scale));
 const context=canvas.getContext('2d');if(!context)throw Error('a 2D canvas is unavailable');
 context.fillStyle='white';context.fillRect(0,0,canvas.width,canvas.height);context.drawImage(bitmap,0,0,canvas.width,canvas.height);
 const content=canvas.toDataURL('image/png').split(',')[1];
 if(content.length>1000000)throw Error('the PNG is too large; reduce the figure dimensions');
 const displayScale=Math.min(1,2000/width,2000/height);
 const entry={name:request.name,token:request.token,content,width:Math.max(1,Math.round(width*displayScale)),height:Math.max(1,Math.round(height*displayScale))};
 let queue=window.mzPjNativeImageQueue;
 if(!queue){
  queue=window.mzPjNativeImageQueue={entries:new Map(),timer:null};
  queue.prune=()=>{for(const [id]of queue.entries)if(!document.getElementById(id))queue.entries.delete(id);};
  queue.observer=new MutationObserver(queue.prune);queue.observer.observe(document.documentElement,{childList:true,subtree:true});
 }
 queue.prune();queue.entries.set(request.root,entry);clearTimeout(queue.timer);
 const accepted=queue.entries.size<=20&&JSON.stringify({version:1,images:Array.from(queue.entries.values())}).length<=1500000;
 if(!accepted){queue.entries.delete(request.root);fail(Error('too many or oversized pending PNG captures; reduce the number or size of figures'));}
 queue.timer=setTimeout(()=>{queue.prune();const payload=JSON.stringify({version:1,images:Array.from(queue.entries.values())});
  if(queue.entries.size)window.setOption('graphicCapture',payload);
 },50);
 if(accepted)status.textContent='Preparing native Image result…';
}catch(error){fail(error);}
})();</script>'''.replace('__REQUEST__', request)
    wrapper = ('<div id="' + root_id + '"><p data-image-status role="status">Preparing native Image…</p>'
               '<div class="ignore-html" style="position:absolute;left:-100000px;top:0;pointer-events:none">'
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

def _pj_add_image(png_data, name=None, title=None):
    """Aggiunge un'immagine PNG (bytes gia' pronti) direttamente ai risultati,
    senza passare da matplotlib - utile per librerie con motore di rendering
    indipendente (plotly, plotnine, PIL, ecc.) che sanno gia' esportare in
    PNG per conto loro. Accetta bytes grezzi, un buffer io.BytesIO, o
    qualunque oggetto con .getvalue()/.read(). title e' opzionale (default
    "Plot Python" lato R se non indicato)."""
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

def _pj_add_html(content, name=None, title=None):
    """title e' opzionale (default "HTML Python" lato R se non indicato)."""
    name = _pj_result_name(name, 'html', _html_counter)

    if content is None:
        content = ""
    elif not isinstance(content, str):
        content = str(content)

    results['items'].append({
        'type': 'Html',
        'name': name,
        'title': title,
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

