# Dimensioni per singola figura

`mzpjShowImage(png_data, name=None, title=None, *, width=None, height=None)` riceve byte PNG. `mzpjShowSvg(content, name=None, title=None, *, width=None, height=None)` riceve markup SVG completo. Dimensioni in pixel CSS interi positivi, fino a 10000.

Senza argomenti si usano i valori globali del popup. Con entrambi si applicano le dimensioni alla sola figura. Con un solo argomento esplicito, l'altro viene calcolato dalle proporzioni originali PNG o dal viewBox/dimensioni intrinseche SVG: non si eredita l'altra dimensione globale. Byte PNG invariati. Per SVG senza proporzioni ricavabili occorrono entrambi. Gli argomenti non cambiano il popup o le altre figure.

```python
mzpjShowImage(png, width=640, height=400, name='image_custom')
mzpjShowSvg(svg_markup, width=720, height=420, name='svg_custom')
```

D3 e Chart.js espongono già width/height; Plotly nativo usa export_width/height. Nessun accordion o zoom Html per Image/Svg. Le dimensioni salvate da jamovi con un resize possono prevalere sulle dimensioni iniziali dello stesso risultato: per confrontarle usare una nuova analisi/nome. Esempio76. Incluso in Pj1.6.2.
