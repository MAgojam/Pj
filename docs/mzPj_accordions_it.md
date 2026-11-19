# Accordion condivisi — Pj 1.6.2

La funzione fa parte del candidato 1.6.2. Installare il nuovo candidato prima di
provare lo [script 75](../pjscript/75_accordion_styles.py), senza dataset o librerie
aggiuntive. Lo script 04 usa ora il componente comune: rimossi CSS locale e
modifiche manuali al dizionario del risultato.

## Argomenti

Le funzioni compatibili hanno `accordion=True`, `expanded=True` e
`accordion_type='line'`. Senza specificare il tipo si usa lo stile line.
`accordion=False` mostra direttamente il contenuto. `expanded=False` richiede
`accordion=True` e imposta lo stato iniziale chiuso.

- **line:** +/- SVG animato; in apertura il tratto verticale ruota e scompare.
  Lineetta prima del titolo, linea successiva che si allunga quando aperto.
  Titolo in grassetto da aperto; in chiusura tornano peso normale e linea corta.
- **bordered:** bordi sopra e sotto il titolo, chevron SVG verso il titolo
  quando chiuso, ruotato in basso quando aperto. Anche qui il titolo diventa grassetto.

Componente unico, supporto Enter/Spazio, indicazione del focus e la stessa
animazione di 0,3 secondi di Variables in Pjp. L'animazione resta attiva anche
con preferenza browser di movimento ridotto, come nel controllo di riferimento;
nessuna impostazione del sistema operativo viene modificata. Aprire/chiudere modifica solo la vista,
non le opzioni e non i calcoli Python. I grafici inizializzati da chiusi ricevono
una notifica di ridimensionamento all'apertura.

```python
mzpjShowHtml('<p>Contenuto del report</p>', title='Report')
mzpjShowHtml('<p>Contenuto del report</p>', title='Report',
              accordion_type='bordered', expanded=False)
mzpjShowBar({'Group':['A','B'], 'Value':[12,19]}, 'Group', 'Value',
             stat='identity', result_type='html', title='Esempio',
             accordion_type='line', expanded=True)
```

## Funzioni e tipi

HTML libero, grafici D3, Chart.js e Plotly usano gli stessi argomenti; per i grafici
valgono solo su Html. Svg nativo, anche con `static=True`, non usa accordion o zoom Html. Le tabelle rese con
`render='html'` hanno l'accordion attivo per default. Svg, Image e Table nativi restano
esclusi, comprese le Image ottenute dalla cattura del browser.

La firma di `mzpjShowTable` usa `accordion=None`: risolve automaticamente False
per Table nativo e True per HTML. Un True esplicito con Table nativo produce un
errore; occorre scegliere `render='html'`. Non cambia il default `render='native'`.

Il titolo esterno di jamovi viene eliminato quando lo fornisce il contenitore,
evitando duplicazioni. Un titolo disegnato intenzionalmente dentro un report HTML
o una figura Plotly resta contenuto dell'utente. Se un frammento HTML ha gia un
contenitore proprio, usare `accordion=False` per evitare annidamenti. Gli esempi
D3 numerati delegano ora il contenitore esterno alla funzione comune.

## Svg nativo: ridimensionamento ed export

Svg nativo viene mostrato direttamente, con titolo e ridimensionamento gestiti da jamovi. Nessun accordion, zoom Html o observer deve riscriverne le dimensioni. Gli argomenti accordion restano accettati per compatibilità degli script, ma non racchiudono Svg. La figura mantiene `jmv-results-svg-selection`; D3 resta vettoriale e Chart.js/Plotly mantengono la rappresentazione raster in Svg.
