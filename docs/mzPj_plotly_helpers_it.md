# Helper Plotly guidati — Pj 1.7.0

I cinque helper funzionano con Python Embedded e System, senza richiedere
pacchetti Python Plotly, pandas o NumPy. Le ricette JavaScript sono comuni
in mzGraphics; preparazione e validazione dei dati restano nel linguaggio host.
La selezione interattiva non cambia il dataset e non riesegue Python.

| Funzione | Scopo e opzioni principali |
|---|---|
| `mzpjShowPlotlyScatter(data, x, y, group=None, labels=None, ...)` | Dispersione per gruppi, etichette hover, dimensione/opacità dei punti, selezione lasso |
| `mzpjShowPlotlyLine(data, x, y, group=None, labels=None, ...)` | Profili, ordinamento esplicito, interruzioni per mancanti e hover unificato |
| `mzpjShowPlotlyBar(data, category, value=None, group=None, ...)` | Conteggi/somma/media/valori forniti, barre raggruppate o impilate, orientamento e valori |
| `mzpjShowPlotlyBoxPlot(data, variable, group=None, labels=None, ...)` | Quartili e baffi calcolati nell’host, punti osservati e outlier conservati |
| `mzpjShowPlotlyHeatmap(matrix, x_labels=None, y_labels=None, ...)` | Matrice numerica rettangolare, scala colori, valori delle celle, limiti fissati |

## Opzioni comuni

Nome e titolo: `name`, `title`. Dimensioni: `width=None`, `height=None`;
`export_width=None` è un alias compatibile di width. Gli argomenti locali
prevalgono per ciascun asse su Settings, poi sul default 600 per 500 pixel. Tipo risultato: `result_type='html'`, `'svg'` o `'image'`.
Accordion solo Html: `accordion`, `expanded`, `accordion_type='line'` oppure
`'bordered'`. Svg/Image sono risultati nativi senza accordion o zoom Html.
Lo Svg Plotly incorpora una PNG; non è vettoriale puro.

La barra strumenti è nascosta per default: `modebar=True` la mostra sempre,
`modebar='hover'` al passaggio del mouse, `False` la nasconde. `None` eredita
il default del renderer comune. Svg/Image la escludono sempre. L’helper
generico continua a usare `config={'displayModeBar': True}`.

Per i primi quattro helper: `show_legend`, `color`, `palette`, `x_label`,
`y_label`, `hover_mode` e `drag_mode`. I colori sono esadecimali a sei cifre;
la palette è una lista/tupla non vuota. La legenda è sopra gli assi; le note
metodologiche sono sotto, senza sovrapporre il titolo dell’asse X.
`hover_mode` ammette closest, x, y, x unified, y unified e False; per le linee
il default è x unified. `drag_mode` ammette zoom, pan, select, lasso e False.
Le opzioni avanzate `layout` e `config` accettano dizionari Plotly, copiati
senza modificare gli originali. Un modebar esplicito prevale sul relativo
config; il risultato statico prevale su entrambi.

## Esempi guida

```python
mzpjShowPlotlyScatter(data, 'Age', 'Score', group='Group', labels='Participant',
                     drag_mode='lasso', marker_size=9, name='scores')
mzpjShowPlotlyLine(data, 'Month', 'Score', group='Group', sort_x=True,
                  connect_gaps=False, hover_mode='x unified', name='profiles')
mzpjShowPlotlyBar(data, 'Activity', group='Group', stat='count',
                 bar_mode='group', show_values=True, name='counts')
mzpjShowPlotlyBoxPlot(data, 'Score', group='Group', show_points=True,
                     name='distributions')
mzpjShowPlotlyHeatmap([[1, None, 3], [4, 5, 6]],
                     x_labels=['X', 'Y', 'Z'], y_labels=['A', 'B'],
                     show_values=True, zmin=0, zmax=10, name='matrix')
```

Scatter esclude coppie incomplete/non finite e gruppi mancanti, senza stimare
regressioni. Le linee seguono l’ordine dei dati salvo sort_x=True; i mancanti
interrompono la linea salvo connect_gaps=True. Ordinare richiede ascisse finite.

Le barre ammettono stat=count (omettere value), sum, mean o identity.
Identity richiede un valore valido per categoria entro ogni gruppo. Le celle
assenti sono zero per i conteggi e mancanti per le altre statistiche.
bar_mode ammette group, stack e relative; orientation vertical/horizontal.
Impilare medie non produce una media complessiva; non sono implicati intervalli
di incertezza. Le aggregazioni sono in Python e non cambiano con la legenda.

I boxplot riutilizzano i quartili lineari (N-1)p e i baffi 1,5 IQR dell’helper
D3. Nei piccoli campioni i baffi non oltrepassano verso l’interno i quartili.
Gli outlier restano nei dati. show_points=True mostra tutti i punti; altrimenti
solo gli outlier. Punti sovrapposti non vengono spostati casualmente.

La heatmap accetta fino a 10000 celle; etichette uniche e coerenti con le
dimensioni. None e non finiti sono mancanti; testo e booleani non sono misure.
La prima riga è in alto. Color_scale: Viridis, Cividis, Blues, RdBu, Plasma,
Inferno, Greys; reverse_scale=True inverte i colori. Fornire entrambi zmin/zmax,
finiti e crescenti, oppure nessuno. Non calcola implicitamente correlazioni,
normalizzazioni o cluster.

Provare lo [script 78](../pjscript/78_plotly_guided_helpers.py), senza dataset
esterni: contiene dati simulati ed esempi dei cinque helper. La [guida inglese](mzPj_plotly_helpers.md)
riporta il contratto completo delle opzioni. mzpjShowPlotly resta compatibile.

## Risposte del servizio standalone

L’editor carica la libreria locale. Ogni risultato Plotly Html/Svg del servizio standalone include invece il fallback compresso offline per funzionare nel proprio iframe. Grandi gruppi di grafici possono raggiungere il limite protettivo della risposta: usare chiamate più piccole. Lo script78 è una dimostrazione nell’editor; non sono stati aumentati i limiti dell’API.


### Preparazione delle Image

Il contenitore temporaneo e il relativo titolo restano fuori dall’area visibile durante la cattura. In Results compare direttamente l’Image finale con il suo titolo, senza testi Preparing Image. Gli errori di preparazione o mancata conferma tornano visibili; Python non viene rieseguito. Attendere le immagini finali prima di esportare.
